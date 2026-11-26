"""Series voice: Kokoro blend (60% am_onyx deep + 40% am_michael clarity), calm pace.
Generates sentence by sentence and inserts natural pauses (longer on '...')."""
import sys, re, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro("/root/models/kokoro-v1.0.onnx", "/root/models/voices-v1.0.bin")
style = 0.6*k.get_voice_style("am_onyx") + 0.4*k.get_voice_style("am_michael")
text, out = sys.argv[1], sys.argv[2]
speed = float(sys.argv[3]) if len(sys.argv) > 3 else 0.92
# split keeping punctuation; pause lengths by terminator
parts = re.findall(r'.+?(?:\.\.\.|[.:!?—]|$)(?=\s|$)', text.strip())
sr = 24000; buf = []
for p in parts:
    p = p.strip()
    if not p: continue
    say = p.replace("POV:", "P.O.V.").replace("...", ".").replace("—", ",")
    say = say.replace("'post'", "post")
    a, sr = k.create(say, voice=style, speed=speed, lang="en-us")
    # trim leading/trailing silence
    idx = np.where(np.abs(a) > 0.01)[0]
    a = a[max(idx[0]-240,0): idx[-1]+1200]
    buf.append(a)
    pause = 0.75 if p.endswith("...") else 0.45 if p.endswith((".", "?", "!")) else 0.3
    if p.startswith("POV:") and len(buf) == 1: pause = 0.35
    buf.append(np.zeros(int(sr*pause)))
audio = np.concatenate([np.zeros(int(sr*0.25))] + buf)
sf.write(out, audio, sr); print(out, round(len(audio)/sr, 2), "s", [p for p in parts])
