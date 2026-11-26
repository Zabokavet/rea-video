"""Generate the avatar's own mouth shapes + blink by inpainting only those regions (same character, same light).
usage: mouths.py <avatar.png> <landmarks.json> <outdir>"""
import sys, json, os, torch, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from diffusers import StableDiffusionXLInpaintPipeline, DPMSolverMultistepScheduler
torch.set_num_threads(os.cpu_count())
src, lmf, out = sys.argv[1:4]; os.makedirs(out, exist_ok=True)
img = Image.open(src).convert("RGB"); lm = np.array(json.load(open(lmf)))
pipe = StableDiffusionXLInpaintPipeline.from_pretrained("SG161222/RealVisXL_V5.0_Lightning", torch_dtype=torch.bfloat16, variant="fp16")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, algorithm_type="sde-dpmsolver++", use_karras_sigmas=True)
pipe.set_progress_bar_config(disable=True)
style = "3d animated film style character, stylized render, soft subsurface skin, same lighting, highly detailed"
neg = "deformed, extra teeth, blurry, lowres, photo, text, watermark, asymmetric"
m = lm[48:68]; mc = m.mean(0); mw = np.ptp(m[:, 0])
def mouth_mask():
    k = Image.new("L", img.size, 0); d = ImageDraw.Draw(k)
    d.ellipse([mc[0] - mw * 0.78, mc[1] - mw * 0.42, mc[0] + mw * 0.78, mc[1] + mw * 0.75], fill=255)
    return k.filter(ImageFilter.GaussianBlur(6))
def eye_mask():
    k = Image.new("L", img.size, 0); d = ImageDraw.Draw(k)
    for e in (lm[36:42], lm[42:48]):
        c = e.mean(0); w = np.ptp(e[:, 0])
        d.ellipse([c[0] - w * 0.8, c[1] - w * 0.55, c[0] + w * 0.8, c[1] + w * 0.5], fill=255)
    return k.filter(ImageFilter.GaussianBlur(4))
jobs = [("small", "close up face, mouth slightly open while speaking, lips parted, top teeth slightly visible", mouth_mask(), 0.75),
        ("open", "close up face, mouth open wide while speaking, saying ah, teeth and tongue visible, jaw dropped", mouth_mask(), 0.88),
        ("oh", "close up face, lips rounded into a small o shape while speaking, saying oh", mouth_mask(), 0.85),
        ("ee", "close up face, mouth open in a wide flat shape saying ee, teeth visible", mouth_mask(), 0.82),
        ("blink", "close up face, eyes gently closed, relaxed eyelids", eye_mask(), 0.85)]
only = sys.argv[4:]
for name, p, mask, st in jobs:
    if only and name not in only: continue
    for seed in (1, 2):
        fn = f"{out}/{name}_{seed}.png"
        if os.path.exists(fn): continue
        r = pipe(prompt=f"{p}, {style}", negative_prompt=neg, image=img, mask_image=mask, width=768, height=1344, strength=st,
                 num_inference_steps=8, guidance_scale=1.5, generator=torch.Generator().manual_seed(seed)).images[0]
        Image.composite(r, img, mask).save(fn); print(fn, flush=True)
mouth_mask().save(f"{out}/mask_mouth.png"); eye_mask().save(f"{out}/mask_eyes.png")
