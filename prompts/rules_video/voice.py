import json, re, numpy as np, soundfile as sf, sys
from kokoro_onnx import Kokoro
S=sys.argv[1]
k=Kokoro(f"{S}/models/kokoro-v1.0.onnx",f"{S}/models/voices-v1.0.bin")
style=0.6*k.get_voice_style("am_michael")+0.4*k.get_voice_style("am_onyx")
WD=sys.argv[2]
rules=json.load(open(f"{WD}/rules.json"))
out=[]
for ri,r in enumerate(rules):
    sents=re.split(r'(?<=[.!?])\s+',r)
    for si,s in enumerate(sents):
        a,sr=k.create(s,voice=style,speed=0.92,lang="en-us")
        # trim silence
        e=np.abs(a); idx=np.where(e>0.01)[0]; a=a[max(0,idx[0]-int(.03*sr)):idx[-1]+int(.06*sr)]
        fn=f"{WD}/s_{ri:02d}_{si}.wav"; sf.write(fn,a,sr)
        out.append(dict(rule=ri,sent=si,text=s,file=fn,dur=len(a)/sr,sr=sr))
        print(ri,si,round(len(a)/sr,2),s)
json.dump(out,open(f"{WD}/sents.json","w"),indent=1)
