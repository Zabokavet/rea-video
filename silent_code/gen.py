"""Keyframe generator: RealVisXL V5 Lightning (photoreal SDXL), CPU bf16, 768x1344 (9:16).
usage: gen.py shots.json outdir [only_id] ; shots.json = {"common":..., "neg":..., "shots":[{"id","prompt","seeds":[..]}]}"""
import sys, json, os, time, torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
torch.set_num_threads(os.cpu_count())
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; only = sys.argv[3:] 
os.makedirs(out, exist_ok=True)
pipe = StableDiffusionXLPipeline.from_pretrained("SG161222/RealVisXL_V5.0_Lightning", torch_dtype=torch.bfloat16, variant="fp16")
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, algorithm_type="sde-dpmsolver++", use_karras_sigmas=True)
pipe.set_progress_bar_config(disable=True)
neg = cfg["neg"]
for s in cfg["shots"]:
    if only and s["id"] not in only: continue
    for seed in s["seeds"]:
        fn = f"{out}/{s['id']}_{seed}.png"
        if os.path.exists(fn): continue
        t = time.time()
        img = pipe(prompt=s["prompt"] + ", " + cfg["common"], negative_prompt=neg, width=768, height=1344,
                   num_inference_steps=6, guidance_scale=1.5, generator=torch.Generator().manual_seed(seed)).images[0]
        img.save(fn); print(fn, round(time.time()-t, 1), "s", flush=True)
