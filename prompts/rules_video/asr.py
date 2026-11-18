import json, re, sys, subprocess, numpy as np
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","quiet","-i",f,"-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.float32)
from faster_whisper import WhisperModel
S=sys.argv[1]; WD=sys.argv[2]; d=json.load(open(f"{WD}/sents.json"))
m=WhisperModel("small.en",device="cpu",compute_type="int8")
norm=lambda t: re.sub(r"[^a-z' ]","",t.lower()).split()
bad=0
for x in d:
    segs,_=m.transcribe(load(x["file"]),word_timestamps=True,beam_size=5,language="en")
    words=[dict(w=w.word.strip(),s=w.start,e=w.end) for sg in segs for w in sg.words]
    hyp=" ".join(w["w"] for w in words)
    ok=norm(hyp)==norm(x["text"])
    x["words"]=words; x["asr"]=hyp; x["asr_ok"]=ok; bad+= not ok
    print("OK " if ok else "XX ",hyp)
json.dump(d,open(f"{WD}/sents.json","w"),indent=1); print("mismatches:",bad)
