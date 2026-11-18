import json, re, subprocess, sys, numpy as np
from faster_whisper import WhisperModel
WD, MP4 = sys.argv[1], sys.argv[2]
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",MP4],capture_output=True,text=True).stdout)
print(f"duration: {dur:.2f}s  ({'OK' if 55<=dur<=75 else 'OUT OF RANGE'})")
x = np.frombuffer(subprocess.run(["ffmpeg","-v","quiet","-i",MP4,"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.float32)
m = WhisperModel("small.en", device="cpu", compute_type="int8")
segs,_ = m.transcribe(x, beam_size=5, language="en", word_timestamps=True)
words = [w for s in segs for w in s.words]
hyp = re.sub(r"[^a-z' ]","", " ".join(w.word for w in words).lower()).split()
TL = json.load(open(f"{WD}/timeline.json")); sents = json.load(open(f"{WD}/sents.json"))
ref = re.sub(r"[^a-z' ]","", " ".join(s["text"] for s in sents).lower()).split()
import difflib
sm = difflib.SequenceMatcher(a=ref, b=hyp)
errs = [(op, " ".join(ref[a:b]), " ".join(hyp[c:d])) for op,a,b,c,d in sm.get_opcodes() if op != "equal"]
print(f"words in script: {len(ref)}  word accuracy on final mix: {100*sm.ratio():.1f}%")
for e in errs: print("  diff:", e)
# sync: voice onset of every line (measured from the voice track) vs the pen's start time for that line
r=subprocess.run([sys.executable,"/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad/onset_check.py",WD],capture_output=True,text=True).stdout.strip()
print("pen/voice sync:", r.split(" ",1)[1] if r else "check failed")
