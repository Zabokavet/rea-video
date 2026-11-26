"""QC for a finished Short: format, duration, loudness, narration-vs-script (Whisper on the FINAL mix), captions-vs-script."""
import sys, re, json, subprocess, difflib, numpy as np
from faster_whisper import WhisperModel
D, F = sys.argv[1], sys.argv[2]
script = open(f"{D}/script.txt").read().split()
p = json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height,codec_name,r_frame_rate","-of","json",F],capture_output=True,text=True).stdout)
v = [s for s in p["streams"] if s.get("width")][0]
dur = float(p["format"]["duration"])
print(f"format: {v['width']}x{v['height']} {v['codec_name']} {v['r_frame_rate']}  9:16={v['width']*16==v['height']*9}  duration={dur:.2f}s  in 25-35s={25<=dur<=35}")
lo = subprocess.run(["ffmpeg","-i",F,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
print("loudness:", re.findall(r"I:\s+(-?[\d.]+) LUFS", lo)[-1], "LUFS  true peak:", re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lo)[-1], "dBTP")
pcm = np.frombuffer(subprocess.run(["ffmpeg","-v","quiet","-i",F,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
segs,_ = WhisperModel("small.en",device="cpu",compute_type="int8").transcribe(pcm, beam_size=5)
heard = " ".join(s.text.strip() for s in segs)
n = lambda ws: [re.sub(r"[^a-z0-9']","",w.lower()) for w in ws]
a, b = n(script), n(heard.replace("P.O.V.","POV").split())
a = [x for x in a if x]; b = [x for x in b if x]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
print("narration heard in final mix:", heard)
print("narration word match vs script:", round(sm.ratio(),3), [ (t,a[i1:i2],b[j1:j2]) for t,i1,i2,j1,j2 in sm.get_opcodes() if t!="equal"])
ass = open(f"{D}/build/captions.ass").read()
caps = []
for line in ass.splitlines():
    if line.startswith("Dialogue: 1,"):
        txt = re.sub(r"\{[^}]*\}","",line.split(",,0,0,0,,",1)[1])
        caps.append(txt)
# each chunk appears once per word; take unique consecutive chunks
uniq = [c for i,c in enumerate(caps) if i==0 or c!=caps[i-1]]
capwords = " ".join(uniq).split()
sw = [w.replace("—","") for w in script if w.replace("—","")]
print("captions == script word-for-word:", capwords == sw)
if capwords != sw: print(difflib.ndiff(sw, capwords))
