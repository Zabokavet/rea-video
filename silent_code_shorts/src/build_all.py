"""Build all 5 Shorts: python3 build_all.py --voice path/to/en_US-ryan-high.onnx [--only 1,3]"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio, render, scripts

ap = argparse.ArgumentParser()
ap.add_argument("--voice", required=True)
ap.add_argument("--work", default="/tmp/silent_code_build")
ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "videos"))
ap.add_argument("--only", default="")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
sel = {int(x) for x in a.only.split(",") if x}
for i, v in enumerate(scripts.VIDEOS, 1):
    if sel and i not in sel:
        continue
    t0 = time.time()
    wd = os.path.join(a.work, v["slug"])
    print(f"[{i}] {v['title']}", flush=True)
    meta = audio.build(v, wd, a.voice)
    out = os.path.join(a.out, f"silent_code_{v['slug']}.mp4")
    render.render_video(os.path.join(wd, "timeline.json"), os.path.join(wd, "mix.wav"), out, v["lines"],
                        {int(30 * meta["lines"][4]["start"]) + 20: os.path.join(a.out, f"thumb_{v['slug']}.jpg")})
    print(f"    -> {out} ({meta['duration']}s) in {time.time() - t0:.0f}s", flush=True)
