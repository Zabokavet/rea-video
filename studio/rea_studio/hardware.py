"""Inspect the machine and pick a capability tier.

Tiers decide default models so we never install something the box cannot run:
  cpu        no usable GPU            -> SD1.5+LCM stills, camera-motion clips, AnimateDiff-Lightning short clips (slow)
  gpu-small  NVIDIA/Apple <= 8 GB     -> + SD1.5/SDXL-Turbo fast, AnimateDiff, Wan2.1 1.3B (480p, offload)
  gpu-mid    12-16 GB                 -> + SDXL, Wan2.2 TI2V-5B / LTX-Video 2B (720p)
  gpu-large  >= 24 GB                 -> + FLUX.1-schnell, Wan2.2 14B (fp8), CogVideoX-5B
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass, field

from .util import STUDIO_HOME, which


@dataclass
class Hardware:
    os: str
    os_version: str
    arch: str
    cpu: str
    cpu_cores: int
    ram_gb: float
    disk_free_gb: float
    gpu: str | None = None
    vram_gb: float = 0.0
    accelerator: str = "cpu"  # cpu | cuda | mps | rocm
    python: str = platform.python_version()
    ffmpeg: str | None = None
    tier: str = "cpu"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _cmd(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def _cpu_name() -> str:
    if platform.system() == "Linux":
        try:
            for line in open("/proc/cpuinfo"):
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
    if platform.system() == "Darwin":
        return _cmd(["sysctl", "-n", "machdep.cpu.brand_string"]) or platform.processor()
    return platform.processor() or platform.machine()


def _ram_gb() -> float:
    try:
        if platform.system() == "Linux":
            for line in open("/proc/meminfo"):
                if line.startswith("MemTotal"):
                    return round(int(line.split()[1]) / 1024 / 1024, 1)
        if platform.system() == "Darwin":
            return round(int(_cmd(["sysctl", "-n", "hw.memsize"])) / 1024**3, 1)
        if platform.system() == "Windows":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong * 6)]
            m = MS(); m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.ullTotalPhys / 1024**3, 1)
    except Exception:
        pass
    return 0.0


def _gpu() -> tuple[str | None, float, str]:
    if which("nvidia-smi"):
        out = _cmd(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
        if out:
            name, mem = [s.strip() for s in out.splitlines()[0].split(",")]
            return name, round(float(mem) / 1024, 1), "cuda"
    if which("rocm-smi"):
        out = _cmd(["rocm-smi", "--showproductname", "--json"])
        if out:
            return "AMD GPU (ROCm)", 0.0, "rocm"
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        # Apple Silicon shares RAM; roughly 2/3 is usable by MPS.
        return "Apple Silicon (MPS)", round(_ram_gb() * 0.66, 1), "mps"
    return None, 0.0, "cpu"


def detect() -> Hardware:
    disk = shutil.disk_usage(STUDIO_HOME if STUDIO_HOME.exists() else os.path.expanduser("~"))
    gpu, vram, acc = _gpu()
    ff = _cmd(["ffmpeg", "-version"]).splitlines()[:1]
    hw = Hardware(
        os=platform.system(), os_version=platform.release(), arch=platform.machine(),
        cpu=_cpu_name(), cpu_cores=os.cpu_count() or 1, ram_gb=_ram_gb(),
        disk_free_gb=round(disk.free / 1024**3, 1), gpu=gpu, vram_gb=vram, accelerator=acc,
        ffmpeg=ff[0] if ff else None,
    )
    if acc == "cpu":
        hw.tier = "cpu"
        hw.notes.append("No GPU: stills are generated with SD1.5+LCM (~30-90 s each); motion comes from "
                        "cinematic camera moves; true AI video clips (AnimateDiff-Lightning) take minutes each.")
    elif vram < 10:
        hw.tier = "gpu-small"
    elif vram < 20:
        hw.tier = "gpu-mid"
    else:
        hw.tier = "gpu-large"
    if hw.ram_gb and hw.ram_gb < 12:
        hw.notes.append("Less than 12 GB RAM: keep to SD1.5-class models; avoid Wan/LTX text encoders (T5/umT5 need 10+ GB).")
    if hw.disk_free_gb < 25:
        hw.notes.append(f"Only {hw.disk_free_gb} GB free disk: install the 'core' model set only.")
    if not hw.ffmpeg:
        hw.notes.append("ffmpeg missing: install it first (apt install ffmpeg / brew install ffmpeg / winget install ffmpeg).")
    return hw


def torch_device() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


if __name__ == "__main__":
    print(json.dumps(detect().to_dict(), indent=2))
