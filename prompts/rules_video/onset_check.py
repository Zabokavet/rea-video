import json, sys, numpy as np, soundfile as sf
WD=sys.argv[1]; TL=json.load(open(f"{WD}/timeline.json"))
a,sr=sf.read(f"{WD}/voice_only.wav"); a=a[:,0]
worst=0; bad=[]
for i,s in enumerate(TL["sent"]):
    w0=s["t0"]+s["words"][0]["s"]; st=max(0,s["t0"]-0.4, (TL["sent"][i-1]["t1"]+0.03) if i else 0)
    seg=np.abs(a[int(st*sr):int((s["t0"]+0.6)*sr)]); fr=int(.01*sr)
    e=np.array([seg[k:k+fr].max() for k in range(0,len(seg)-fr,fr)])
    on=st+np.argmax(e>0.05)*0.01; worst=max(worst,abs(on-w0))
    if abs(on-w0)>0.08: bad.append((i,round(on,2),round(w0,2)))
    # also the end: voice should be silent right after t1
    tail=np.abs(a[int((s["t1"]+0.05)*sr):int((s["t1"]+0.2)*sr)])
    if len(tail) and tail.max()>0.05 and i+1<len(TL["sent"]) and TL["sent"][i+1]["t0"]>s["t1"]+0.2: bad.append((i,"voice continues after t1"))
long=[(i,w["w"],round(w["e"]-w["s"],2)) for i,s in enumerate(TL["sent"]) for w in s["words"] if w["e"]-w["s"]>1.0]
print(WD.split("/")[-1], "worst line-start gap: %.0f ms"%(worst*1000), "issues:",bad, "stretched:",long)
