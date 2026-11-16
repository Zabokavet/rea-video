"""Local image generation (diffusers) with character/location consistency + upscaling.

Model presets (all open weights, no account needed):
  sd15-lcm       Lykon/dreamshaper-8 + LCM-LoRA, 6 steps        CPU ~60 s/frame, 4 GB RAM    CreativeML OpenRAIL-M
  sdxl-lightning SDXL base + ByteDance SDXL-Lightning 4-step       GPU >= 8 GB                   OpenRAIL++
  flux-schnell   black-forest-labs/FLUX.1-schnell 4-step          GPU >= 16 GB (offload 12)     Apache-2.0
Consistency:
  * a style bible (global prompt) appended to every frame
  * characters/locations described once in the project and injected verbatim wherever they appear
  * deterministic seeds per (character set, location) so recurring scenes share composition DNA
  * optional IP-Adapter: a reference portrait per character conditions every frame that character is in
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .util import STUDIO_HOME, log

PRESETS = {
    "sd15-lcm": dict(repo="Lykon/dreamshaper-8", lora="latent-consistency/lcm-lora-sdv1-5", steps=6, cfg=1.5,
                     base=512, family="sd15", license="CreativeML OpenRAIL-M (commercial OK with use restrictions)"),
    "sd15": dict(repo="Lykon/dreamshaper-8", steps=28, cfg=6.5, base=512, family="sd15",
                 license="CreativeML OpenRAIL-M"),
    "sdxl-lightning": dict(repo="stabilityai/stable-diffusion-xl-base-1.0", lightning="ByteDance/SDXL-Lightning",
                           steps=4, cfg=0.0, base=1024, family="sdxl", license="CreativeML OpenRAIL++-M"),
    "flux-schnell": dict(repo="black-forest-labs/FLUX.1-schnell", steps=4, cfg=0.0, base=1024, family="flux",
                         license="Apache-2.0"),
}

NEGATIVE = ("text, watermark, logo, signature, caption, letters, picture frame, border, canvas edge, blurry, lowres, jpeg artifacts, deformed, "
            "disfigured, bad anatomy, extra fingers, extra limbs, mutated hands, cartoon, 3d render, plastic skin")


def default_preset(tier: str) -> str:
    return {"cpu": "sd15-lcm", "gpu-small": "sd15-lcm", "gpu-mid": "sdxl-lightning",
            "gpu-large": "flux-schnell"}.get(tier, "sd15-lcm")


def gen_size(aspect: str, preset: str) -> tuple[int, int]:
    base = PRESETS[preset]["base"]
    ratio = {"16:9": 16 / 9, "9:16": 9 / 16, "1:1": 1.0, "4:5": 4 / 5, "21:9": 21 / 9}.get(aspect, 16 / 9)
    area = base * base * (1.6 if base == 512 else 1.0)  # SD1.5 tolerates ~1.6x its native area well
    w = math.sqrt(area * ratio)
    h = w / ratio
    return int(round(w / 16) * 16), int(round(h / 16) * 16)


class ImageGenerator:
    def __init__(self, preset: str = "sd15-lcm", device: str | None = None, ip_adapter: bool = False):
        self.preset = preset
        self.cfg = PRESETS[preset]
        from .hardware import torch_device
        self.device = device or torch_device()
        self.ip_adapter = ip_adapter and self.cfg["family"] == "sd15"
        self._pipe = None

    # ---------------------------------------------------------- loading
    def _load(self):
        if self._pipe is not None:
            return self._pipe
        import torch
        torch.set_num_threads(max(1, (__import__("os").cpu_count() or 4)))
        dtype = torch.float16 if self.device == "cuda" else (torch.bfloat16 if self.cfg["family"] == "flux" and self.device != "cpu" else torch.float32)
        fam = self.cfg["family"]
        log(f"loading image model {self.cfg['repo']} on {self.device} (first run downloads weights)")
        if fam == "sd15":
            from diffusers import LCMScheduler, StableDiffusionPipeline
            pipe = StableDiffusionPipeline.from_pretrained(self.cfg["repo"], torch_dtype=dtype, safety_checker=None,
                                                           requires_safety_checker=False)
            if self.cfg.get("lora"):
                pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
                pipe.load_lora_weights(self.cfg["lora"], adapter_name="lcm")
            if self.ip_adapter:
                pipe.load_ip_adapter("h94/IP-Adapter", subfolder="models", weight_name="ip-adapter-plus_sd15.safetensors")
                pipe.set_ip_adapter_scale(0.55)
            elif self.cfg.get("lora"):
                pipe.fuse_lora()
        elif fam == "sdxl":
            from diffusers import EulerDiscreteScheduler, StableDiffusionXLPipeline
            from huggingface_hub import hf_hub_download
            pipe = StableDiffusionXLPipeline.from_pretrained(self.cfg["repo"], torch_dtype=dtype,
                                                             variant="fp16" if dtype == torch.float16 else None)
            pipe.load_lora_weights(hf_hub_download(self.cfg["lightning"], "sdxl_lightning_4step_lora.safetensors"))
            pipe.fuse_lora()
            pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
        else:
            from diffusers import FluxPipeline
            pipe = FluxPipeline.from_pretrained(self.cfg["repo"], torch_dtype=dtype)
        if self.device == "cuda" and fam != "sd15":
            pipe.enable_model_cpu_offload()
        else:
            pipe = pipe.to(self.device)
        if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_tiling"):
            pipe.vae.enable_tiling()
        pipe.set_progress_bar_config(disable=True)
        self._pipe = pipe
        return pipe

    # ---------------------------------------------------------- generation
    def generate(self, prompt: str, out: Path, aspect: str = "16:9", seed: int = 0, negative: str = NEGATIVE,
                 reference: Path | None = None, steps: int | None = None) -> Path:
        import torch
        pipe = self._load()
        w, h = gen_size(aspect, self.preset)
        kw = dict(prompt=prompt, width=w, height=h, num_inference_steps=steps or self.cfg["steps"],
                  guidance_scale=self.cfg["cfg"], generator=torch.Generator("cpu").manual_seed(seed))
        if self.cfg["family"] == "sd15":
            kw["negative_prompt"] = negative
            if self.ip_adapter:
                kw["ip_adapter_image"] = Image.open(reference).convert("RGB") if reference else Image.new("RGB", (224, 224), (127, 127, 127))
                pipe.set_ip_adapter_scale(0.55 if reference else 0.0)
        if self.cfg["family"] == "flux":
            kw["max_sequence_length"] = 256
        img = pipe(**kw).images[0]
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        return out


# -------------------------------------------------------------- prompt building
def build_prompt(scene: dict, project: dict) -> str:
    parts = [scene.get("visual", "")]
    chars = project.get("characters") or {}
    for c in scene.get("characters", []) or []:
        if c in chars:
            parts.append(chars[c].get("description", ""))
    locs = project.get("locations") or {}
    if scene.get("location") in locs:
        parts.append(locs[scene["location"]].get("description", ""))
    if scene.get("lighting"):
        parts.append(scene["lighting"])
    parts.append(project.get("visual_style", ""))
    return ", ".join(p.strip().strip(",") for p in parts if p and p.strip())


def scene_seed(scene: dict, project: dict, index: int) -> int:
    if "seed" in scene:
        return int(scene["seed"])
    base = int(project.get("seed", 1234))
    chars = project.get("characters") or {}
    # characters with a fixed seed pull every scene they are in toward the same "look"
    for c in scene.get("characters", []) or []:
        if "seed" in chars.get(c, {}):
            return int(chars[c]["seed"]) + index * 7
    return base + index * 101


# -------------------------------------------------------------- upscaling
_esrgan = None


def _esrgan_model():
    global _esrgan
    if _esrgan is None:
        import urllib.request

        import spandrel
        import torch
        path = STUDIO_HOME / "models" / "RealESRGAN_x4plus.pth"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            log("downloading Real-ESRGAN x4plus (BSD-3, 64 MB)")
            urllib.request.urlretrieve(
                "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth", path)
        from .hardware import torch_device
        _esrgan = spandrel.ModelLoader().load_from_file(str(path)).eval().to(torch_device())
        _esrgan.model.to(torch.float32)
    return _esrgan


def upscale(img: Image.Image, target_w: int, target_h: int, method: str = "auto") -> Image.Image:
    """Resize to cover target, using Real-ESRGAN when available (method=auto|esrgan|lanczos)."""
    scale = max(target_w / img.width, target_h / img.height)
    if method in ("auto", "esrgan") and scale > 1.3:
        try:
            img = _esrgan_upscale(img)
        except Exception as e:  # spandrel not installed or download blocked
            if method == "esrgan":
                raise
            log(f"Real-ESRGAN unavailable ({type(e).__name__}); using Lanczos + unsharp")
    scale = max(target_w / img.width, target_h / img.height)
    img = img.resize((math.ceil(img.width * scale), math.ceil(img.height * scale)), Image.LANCZOS)
    if scale > 1.2:
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    left = (img.width - target_w) // 2
    top = (img.height - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _esrgan_upscale(img: Image.Image, tile: int = 256) -> Image.Image:
    import torch
    model = _esrgan_model()
    dev = next(model.model.parameters()).device
    x = torch.from_numpy(np.asarray(img.convert("RGB"), dtype=np.float32) / 255).permute(2, 0, 1)[None].to(dev)
    _, _, H, W = x.shape
    out = torch.zeros(1, 3, H * 4, W * 4)
    pad = 16
    with torch.no_grad():
        for y in range(0, H, tile):
            for xx in range(0, W, tile):
                y0, x0 = max(0, y - pad), max(0, xx - pad)
                y1, x1 = min(H, y + tile + pad), min(W, xx + tile + pad)
                o = model(x[:, :, y0:y1, x0:x1]).cpu()
                oy, ox = (y - y0) * 4, (xx - x0) * 4
                th, tw = min(tile, H - y) * 4, min(tile, W - xx) * 4
                out[:, :, y * 4:y * 4 + th, xx * 4:xx * 4 + tw] = o[:, :, oy:oy + th, ox:ox + tw]
    arr = (out[0].clamp(0, 1).permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(arr)


# -------------------------------------------------------------- placeholder (explicit opt-in only)
def placeholder(text: str, out: Path, aspect: str = "16:9", seed: int = 0) -> Path:
    """A clearly-synthetic gradient card. Only used with --allow-placeholder (e.g. CI) and always reported."""
    w, h = gen_size(aspect, "sd15-lcm")
    rng = np.random.default_rng(seed)
    c1, c2 = rng.integers(10, 90, 3), rng.integers(60, 200, 3)
    t = np.linspace(0, 1, h)[:, None, None]
    arr = (c1 * (1 - t) + c2 * t).repeat(w, axis=1).astype(np.uint8)
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    d.text((20, h - 40), "PLACEHOLDER: " + text[:80], fill=(255, 255, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out
