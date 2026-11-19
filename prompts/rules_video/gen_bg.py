# usage: gen_bg.py <prompt_id> <seed> [seed...]
import sys, torch, time
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from safetensors.torch import load_file
S="/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad"
torch.set_num_threads(4)
PROMPTS={
"sheet":"top-down photograph of a large blank sheet of aged cream paper lying on a dark wooden desk, the empty paper covers most of the frame, dark wood visible at the edges, warm candlelight from the left, soft shadows, moody, photorealistic, film grain",
"parch2":"macro photograph of blank aged parchment paper filling the frame, slightly wrinkled, warm golden candlelight from the upper left, darker edges, cinematic, photorealistic",

"journal":"overhead photograph of an open blank journal with completely empty cream pages on a dark walnut desk, warm candle light from the left, deep shadows, moody, photorealistic, film photo",
"parch":"macro photograph of a single sheet of blank aged parchment paper filling the frame, warm candlelight from the left, soft shadows, dark vignette edges, photorealistic, film grain",

"page":"overhead close-up photograph of a single blank page of an antique open book lying on a dark walnut desk, page fills most of the frame, empty aged cream paper with subtle fibers, warm candlelight from the left side, soft natural shadows near the spine, moody dark room, shallow depth of field, photorealistic, 35mm film photo, high detail, no text, no writing",
"page2":"top-down photograph of an old leather-bound book open on a dark wooden table, blank yellowed pages, warm golden lamp light falling from the upper left, deep shadows at the edges, cinematic moody atmosphere, photorealistic, film grain, no text",
}
from accelerate import init_empty_weights
with init_empty_weights():
    unet=UNet2DConditionModel.from_config(UNet2DConditionModel.load_config(f"{S}/sdxl/unet/config.json"))
sd=load_file(f"{S}/lightning/sdxl_lightning_4step_unet.safetensors")
for k in list(sd): sd[k]=sd[k].to(torch.bfloat16)
unet.load_state_dict(sd, assign=True); del sd
pipe=StableDiffusionXLPipeline.from_pretrained(f"{S}/sdxl", unet=unet, torch_dtype=torch.bfloat16, variant="fp16")
pipe.enable_attention_slicing()
pipe.scheduler=EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
pid=sys.argv[1]
for sd in sys.argv[2:]:
    t=time.time()
    img=pipe(PROMPTS[pid], num_inference_steps=4, guidance_scale=0, width=768, height=1344, generator=torch.Generator().manual_seed(int(sd))).images[0]
    img.save(f"{S}/bg/{pid}_{sd}.png"); print("saved",pid,sd,round(time.time()-t),"s",flush=True)
