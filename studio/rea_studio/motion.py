"""Turn a keyframe into a moving shot.

Three engines, chosen per scene (`motion:` key) or automatically by hardware tier:
  camera     Sub-pixel eased camera moves (push-in, pull-out, pan, tilt, drift, orbit, handheld) rendered
             with OpenCV on an upscaled keyframe. Fast on any CPU; this is the "Ken Burns done right" look
             used by most documentaries.
  parallax   2.5D: Depth-Anything-V2-Small (Apache-2.0) depth map -> foreground/background move at different
             speeds. Adds real depth to stills. CPU-friendly (~3 s per keyframe + render).
  animate    True AI motion with AnimateDiff-Lightning (ByteDance, OpenRAIL) in video-to-video mode: the
             camera-move clip of *our* keyframe is re-noised and re-generated, so water, clouds, fire, crowds
             move while composition/characters stay those of the keyframe. CPU: minutes per clip.
  wan        Wan2.2-TI2V-5B image-to-video (Apache-2.0) through diffusers. Needs an NVIDIA GPU >= 12 GB
             (24 GB comfortable). Not runnable on CPU-only machines.
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from .util import log

MOVES = ["push_in", "pull_out", "pan_left", "pan_right", "tilt_up", "tilt_down", "drift", "static",
         "orbit", "handheld", "push_in_fast", "parallax_in", "parallax_left", "parallax_right"]


def _ease(t: float, kind: str = "inout") -> float:
    if kind == "linear":
        return t
    if kind == "out":
        return 1 - (1 - t) ** 3
    return t * t * (3 - 2 * t)  # smoothstep


def move_params(move: str, t: float, focus: tuple[float, float] = (0.5, 0.5)) -> tuple[float, float, float, float]:
    """-> (zoom, cx, cy, rotation_deg) at normalised time t."""
    e = _ease(t)
    fx, fy = focus
    if move in ("push_in", "parallax_in"):
        return 1.0 + 0.16 * e, 0.5 + (fx - 0.5) * 0.4 * e, 0.5 + (fy - 0.5) * 0.4 * e, 0
    if move == "push_in_fast":
        return 1.0 + 0.32 * _ease(t, "out"), fx, fy, 0
    if move == "pull_out":
        return 1.18 - 0.18 * e, fx + (0.5 - fx) * e, fy + (0.5 - fy) * e, 0
    if move in ("pan_left", "parallax_left"):
        return 1.14, 0.56 - 0.12 * e, 0.5, 0
    if move in ("pan_right", "parallax_right"):
        return 1.14, 0.44 + 0.12 * e, 0.5, 0
    if move == "tilt_up":
        return 1.14, 0.5, 0.56 - 0.12 * e, 0
    if move == "tilt_down":
        return 1.14, 0.5, 0.44 + 0.12 * e, 0
    if move == "orbit":
        return 1.12 + 0.04 * e, 0.47 + 0.06 * e, 0.5, -1.2 + 2.4 * e
    if move == "drift":
        return 1.06 + 0.05 * e, 0.48 + 0.04 * e, 0.51 - 0.02 * e, 0
    if move == "handheld":
        n = lambda s, f: sum(math.sin(t * f * k + s * k) / k for k in (1, 2.3, 4.1))  # noqa: E731
        return 1.1, 0.5 + 0.006 * n(1, 9), 0.5 + 0.006 * n(5, 7), 0.25 * n(3, 5)
    return 1.02 + 0.015 * e, 0.5, 0.5, 0  # static = slow "breathing"


class FFmpegWriter:
    def __init__(self, path: Path, w: int, h: int, fps: int, crf: int = 16):
        self.p = subprocess.Popen(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)

    def write(self, frame: np.ndarray):
        self.p.stdin.write(np.ascontiguousarray(frame, dtype=np.uint8).tobytes())

    def close(self):
        self.p.stdin.close()
        if self.p.wait() != 0:
            raise RuntimeError("ffmpeg encoder failed")


def _view(src: np.ndarray, W: int, H: int, zoom: float, cx: float, cy: float, rot: float,
          depth: np.ndarray | None = None, par: tuple[float, float] = (0, 0)) -> np.ndarray:
    Hs, Ws = src.shape[:2]
    k = (Ws / zoom) / W
    vw, vh = Ws / zoom, Hs / zoom
    # keep the window inside the image (rotation needs a little margin, covered by zoom >= 1.1 moves)
    cxp = min(max(cx * Ws, vw / 2), Ws - vw / 2)
    cyp = min(max(cy * Hs, vh / 2), Hs - vh / 2)
    a = math.radians(rot)
    ca, sa = math.cos(a) * k, math.sin(a) * k
    M = np.array([[ca, -sa, cxp - ca * W / 2 + sa * H / 2],
                  [sa, ca, cyp - sa * W / 2 - ca * H / 2]], dtype=np.float32)
    if depth is None:
        return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP,
                              borderMode=cv2.BORDER_REFLECT)
    # 2.5D: per-pixel offset proportional to depth (near = 1). Build sampling maps then remap.
    xs, ys = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    mx = M[0, 0] * xs + M[0, 1] * ys + M[0, 2]
    my = M[1, 0] * xs + M[1, 1] * ys + M[1, 2]
    d = cv2.remap(depth, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    mx = mx - par[0] * Ws * (d - 0.5)
    my = my - par[1] * Hs * (d - 0.5)
    return cv2.remap(src, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


_depth_pipe = None


def depth_map(img: Image.Image) -> np.ndarray:
    global _depth_pipe
    if _depth_pipe is None:
        from transformers import pipeline
        _depth_pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf")
    small = img.copy()
    small.thumbnail((768, 768))
    d = np.asarray(_depth_pipe(small)["depth"], dtype=np.float32)
    d = cv2.resize(d, img.size, interpolation=cv2.INTER_CUBIC)
    d = (d - d.min()) / max(1e-6, d.max() - d.min())
    return cv2.GaussianBlur(d, (0, 0), 3).astype(np.float32)


def camera_clip(keyframe: Path, out: Path, duration: float, W: int, H: int, fps: int = 30,
                move: str = "push_in", focus=(0.5, 0.5), upscale_method: str = "auto") -> Path:
    from .images import upscale
    over = 1.25  # source is larger than the frame so moves stay sharp
    tw, th = int(W * over), int(H * over)
    # Upscaling (Real-ESRGAN on CPU ~1 min) is cached next to the keyframe: re-renders and other-language
    # versions that reuse the keyframe skip it.
    import hashlib

    from .util import STUDIO_HOME
    digest = hashlib.sha256(Path(keyframe).read_bytes()).hexdigest()[:20]
    cache = STUDIO_HOME / "cache" / "upscaled" / f"{digest}_{tw}x{th}_{upscale_method}.png"
    if cache.exists():
        src_img = Image.open(cache).convert("RGB")
    else:
        src_img = upscale(Image.open(keyframe).convert("RGB"), tw, th, upscale_method)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            src_img.save(cache)
        except OSError:
            pass
    src = np.asarray(src_img)
    depth = None
    if move.startswith("parallax"):
        try:
            depth = depth_map(src_img)
        except Exception as e:
            log(f"depth model unavailable ({type(e).__name__}: {e}); parallax -> plain camera move")
    n = max(2, int(round(duration * fps)))
    wr = FFmpegWriter(out, W, H, fps)
    for i in range(n):
        t = i / (n - 1)
        z, cx, cy, r = move_params(move, t, focus)
        par = (0.0, 0.0)
        if depth is not None:
            amt = 0.035 * _ease(t)
            par = {"parallax_left": (-amt, 0), "parallax_right": (amt, 0)}.get(move, (0, -amt * 0.4))
            if move == "parallax_in":  # near objects grow faster than far ones
                frame = _view(src, W, H, z, cx, cy, r).astype(np.float32)
                near = _view(src, W, H, z * (1 + 0.06 * _ease(t)), cx, cy, r).astype(np.float32)
                dview = _view(depth, W, H, z, cx, cy, r)
                a = np.clip((dview - 0.45) * 3, 0, 1)[..., None]
                wr.write(frame * (1 - a) + near * a)
                continue
        wr.write(_view(src, W, H, z, cx, cy, r, depth, par))
    wr.close()
    return out


# ------------------------------------------------------------------ AI motion
_ad_pipe = None


def animate_clip(keyframe: Path, out: Path, duration: float, W: int, H: int, fps: int = 30,
                 prompt: str = "", move: str = "drift", strength: float = 0.55, frames: int = 16,
                 seed: int = 0, negative: str = "text, watermark, blurry, deformed") -> Path:
    """AnimateDiff-Lightning video-to-video on a camera move of the keyframe, then upscaled & retimed."""
    global _ad_pipe
    import tempfile

    import torch
    from diffusers import AnimateDiffVideoToVideoPipeline, EulerDiscreteScheduler, MotionAdapter
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    from .hardware import torch_device
    dev = torch_device()
    if _ad_pipe is None:
        log("loading AnimateDiff-Lightning (first run downloads ~1 GB)")
        dtype = torch.float16 if dev == "cuda" else torch.float32
        ad = MotionAdapter().to(dev, dtype)
        ad.load_state_dict(load_file(hf_hub_download("ByteDance/AnimateDiff-Lightning",
                                                     "animatediff_lightning_4step_diffusers.safetensors"), device=dev))
        p = AnimateDiffVideoToVideoPipeline.from_pretrained("Lykon/dreamshaper-8", motion_adapter=ad, torch_dtype=dtype)
        p.scheduler = EulerDiscreteScheduler.from_config(p.scheduler.config, timestep_spacing="trailing",
                                                         beta_schedule="linear")
        p.set_progress_bar_config(disable=True)
        p.enable_vae_slicing()
        _ad_pipe = p.to(dev)
    # generation resolution: ~512 on the long side keeps CPU time sane
    ar = W / H
    gw, gh = (512, int(round(512 / ar / 8) * 8)) if ar >= 1 else (int(round(512 * ar / 8) * 8), 512)
    img = Image.open(keyframe).convert("RGB")
    base = np.asarray(img.resize((int(gw * 1.2), int(gh * 1.2)), Image.LANCZOS))
    init = []
    for i in range(frames):
        z, cx, cy, r = move_params(move, i / (frames - 1))
        init.append(Image.fromarray(_view(base, gw, gh, 1 + (z - 1) * 0.5, cx, cy, r * 0.5)))
    res = _ad_pipe(video=init, prompt=prompt, negative_prompt=negative, strength=strength, guidance_scale=1.0,
                   height=gh, width=gw,
                   num_inference_steps=4, decode_chunk_size=2,
                   generator=torch.Generator("cpu").manual_seed(seed))
    gen = res.frames[0]
    with tempfile.TemporaryDirectory() as d:
        raw = out.with_suffix(".ai_raw.mp4")  # kept for inspection / re-timing
        wr = FFmpegWriter(raw, gw, gh, 8, crf=12)
        for f in gen:
            f = f.convert("RGB")
            if f.size != (gw, gh):  # never let a size mismatch corrupt the raw stream
                f = f.resize((gw, gh), Image.LANCZOS)
            wr.write(np.asarray(f))
        wr.close()
        # 16 frames @8fps = 2 s. Motion-interpolate to target fps, slow to fill, ping-pong if still short.
        src_len = frames / 8
        slow = min(2.5, max(1.0, duration / src_len))
        loops = max(1, math.ceil(duration / (src_len * slow * 2)))
        # frame blending (not motion-compensated interpolation, which makes block artifacts on AI frames)
        vf = (f"setpts={slow:.3f}*PTS,framerate=fps={fps}:interp_start=0:interp_end=255:scene=100,"
              f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6")
        from .util import ffmpeg
        mid = Path(d) / "mid.mp4"
        ffmpeg("-i", raw, "-vf", vf, "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", mid)
        pp = Path(d) / "pp.mp4"
        ffmpeg("-i", mid, "-filter_complex", "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1[o]", "-map", "[o]",
               "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", pp)
        ffmpeg("-stream_loop", str(loops), "-i", pp, "-t", f"{duration:.3f}", "-c:v", "libx264", "-crf", "16",
               "-pix_fmt", "yuv420p", "-r", str(fps), out)
    return out


def wan_clip(keyframe: Path, out: Path, duration: float, W: int, H: int, fps: int = 24, prompt: str = "",
             seed: int = 0) -> Path:
    """Wan2.2 TI2V-5B image-to-video (GPU only). 121 frames @24fps max per call (~5 s)."""
    import torch
    from diffusers import AutoencoderKLWan, WanImageToVideoPipeline
    from diffusers.utils import export_to_video

    from .hardware import torch_device
    if torch_device() != "cuda":
        raise RuntimeError("Wan video generation needs an NVIDIA GPU (>=12 GB VRAM). Use motion: animate or camera.")
    repo = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
    vae = AutoencoderKLWan.from_pretrained(repo, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanImageToVideoPipeline.from_pretrained(repo, vae=vae, torch_dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    gw, gh = (1280, 704) if W >= H else (704, 1280)
    n = min(121, int(duration * 24) // 4 * 4 + 1)
    frames = pipe(image=Image.open(keyframe).convert("RGB").resize((gw, gh)), prompt=prompt, height=gh, width=gw,
                  num_frames=n, guidance_scale=5.0, num_inference_steps=40,
                  generator=torch.Generator("cpu").manual_seed(seed)).frames[0]
    tmp = out.with_suffix(".raw.mp4")
    export_to_video(frames, str(tmp), fps=24)
    from .util import ffmpeg
    ffmpeg("-i", tmp, "-vf", f"scale={W}:{H}:flags=lanczos,fps={fps},tpad=stop_mode=clone:stop_duration={duration}",
           "-t", f"{duration:.3f}", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out)
    tmp.unlink(missing_ok=True)
    return out
