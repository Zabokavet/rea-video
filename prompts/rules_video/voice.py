import json, re, numpy as np, soundfile as sf, sys
from kokoro_onnx import Kokoro
S=sys.argv[1]
k=Kokoro(f"{S}/models/kokoro-v1.0.onnx",f"{S}/models/voices-v1.0.bin")
style=0.6*k.get_voice_style("am_michael")+0.4*k.get_voice_style("am_onyx")
rules=[
"The less you say, the more your words weigh.",
"Never explain yourself to someone who has already decided to misunderstand you.",
"When you are angry, say nothing. Anger makes honest men say permanent things in temporary moments.",
"Do not announce your plans. Show the results and let people ask how.",
"A man who talks about everything he is doing is doing very little.",
"Listen twice as much as you speak. People tell you exactly who they are if you let them talk long enough.",
"Silence after disrespect is not weakness. It is a sentence being prepared.",
"Never correct people in public. Win in private, or don't win at all.",
"If you must speak, ask questions. The one asking questions controls the conversation.",
"Your silence makes loud people nervous. Keep it.",
"There are deeper rules than these, and they are not taught for free. Follow this page. One rule every day.",
]
out=[]
for ri,r in enumerate(rules):
    sents=re.split(r'(?<=[.!?])\s+',r)
    for si,s in enumerate(sents):
        a,sr=k.create(s,voice=style,speed=0.92,lang="en-us")
        # trim silence
        e=np.abs(a); idx=np.where(e>0.01)[0]; a=a[max(0,idx[0]-int(.03*sr)):idx[-1]+int(.06*sr)]
        fn=f"{S}/v1/s_{ri:02d}_{si}.wav"; sf.write(fn,a,sr)
        out.append(dict(rule=ri,sent=si,text=s,file=fn,dur=len(a)/sr,sr=sr))
        print(ri,si,round(len(a)/sr,2),s)
json.dump(out,open(f"{S}/v1/sents.json","w"),indent=1)
