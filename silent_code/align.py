"""Word-level timing for the EXACT script words, using Whisper word timestamps + sequence alignment.
Also reports transcription accuracy as a voice QC."""
import sys, re, json, difflib
from faster_whisper import WhisperModel
audio, script, out = sys.argv[1], sys.argv[2], sys.argv[3]
m = WhisperModel("small.en", device="cpu", compute_type="int8")
import subprocess, numpy as np
pcm = np.frombuffer(subprocess.run(["ffmpeg","-v","quiet","-i",audio,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
# every script opens with a standalone "POV:" phrase: time it from audio energy, align the rest separately
env = np.array([np.sqrt((pcm[i:i+160]**2).mean()) for i in range(0, len(pcm)-160, 160)])  # 10 ms frames
on = np.where(env > 0.02)[0]; st = on[0]
k = st
while k < len(env) and (env[k:k+25] > 0.02).any(): k += 1   # until >=250 ms of silence
pov = (st/100, k/100)
off = int((pov[1]+0.1)*16000)
segs, _ = m.transcribe(pcm[off:], word_timestamps=True, beam_size=5, initial_prompt="POV:")
hw = [w for s in segs for w in s.words]
for w in hw: w.start += off/16000; w.end += off/16000
norm = lambda t: re.sub(r"[^a-z0-9']", "", t.lower().replace("’", "'"))
sw = script.split()
assert sw[0] == "POV:"; sw = sw[1:]
hn = [norm(w.word) for w in hw]
hn = ["pov" if h in ("pov", "pv", "pob") else h for h in hn]
sn = [norm(w) for w in sw]
sm = difflib.SequenceMatcher(None, sn, hn, autojunk=False)
t = [None]*len(sw)
for a, b, n in sm.get_matching_blocks():
    for i in range(n): t[a+i] = (hw[b+i].start, hw[b+i].end)
# fill gaps from replace opcodes / interpolation
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "replace" and j2 > j1:
        s0, e0 = hw[j1].start, hw[j2-1].end
        for k in range(i1, i2):
            f0, f1 = (k-i1)/(i2-i1), (k-i1+1)/(i2-i1)
            t[k] = (s0+(e0-s0)*f0, s0+(e0-s0)*f1)
for k in range(len(t)):
    if t[k] is None:
        prev = t[k-1][1] if k else 0.0
        nxt = next((t[j][0] for j in range(k+1, len(t)) if t[j]), prev+0.4)
        t[k] = (prev, min(nxt, prev+0.4))
ratio = sm.ratio()
print("heard:", " ".join(w.word.strip() for w in hw))
print("match ratio:", round(ratio, 3))
t = [pov] + t; sw = ["POV:"] + sw
json.dump([{"w": w, "s": round(a, 3), "e": round(b, 3)} for w, (a, b) in zip(sw, t)], open(out, "w"), indent=0)
