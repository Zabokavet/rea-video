import json, sys, re
WD=sys.argv[1]
s=json.load(open(f"{WD}/sents.json")); pages=json.load(open(f"{WD}/layout.json"))
norm=lambda w: re.sub(r"[^a-z0-9']","",w.lower())
t=0.12; out=[]; turns=[]
for i,x in enumerate(s):
    toks=x["text"].split(); ws=x["words"]
    if len(ws)!=len(toks) or any(norm(a)!=norm(b["w"]) for a,b in zip(toks,ws)):
        print("align fallback", i)  # proportional by characters
        tot=sum(len(k) for k in toks); acc=0; ws=[]
        for k in toks: ws.append(dict(w=k,s=x["dur"]*acc/tot,e=x["dur"]*(acc+len(k))/tot)); acc+=len(k)
    # clamp & make monotonic
    prev=0
    for w in ws: w["s"]=max(w["s"],prev); w["e"]=max(w["e"],w["s"]+0.04); prev=w["e"]
    out.append(dict(t0=round(t,3),t1=round(t+x["dur"],3),file=x["file"],words=ws))
    t+=x["dur"]
    if i+1<len(s):
        if pages[i+1]!=pages[i]:
            turns.append(dict(frm=pages[i],to=pages[i+1],t0=round(t+0.15,3),t1=round(t+0.15+0.8,3))); t+=1.15
        elif s[i+1]["rule"]==x["rule"]: t+=0.28
        else: t+=0.58
end=t+1.5
json.dump(dict(sent=out,turns=turns,end=round(end,3)),open(f"{WD}/timeline.json","w"),indent=1)
print("end",round(end,2),"turns",turns)
