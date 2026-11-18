import json, sys, re
WD=sys.argv[1]
s=json.load(open(f"{WD}/sents.json")); pages=json.load(open(f"{WD}/layout.json"))
norm=lambda w: re.sub(r"[^a-z0-9']","",w.lower())
# base length estimate -> widen the pause between rules for short scripts
_speech=sum(x["dur"] for x in s)
_nturn=sum(1 for i in range(len(s)-1) if pages[i+1]!=pages[i])
_nrule=sum(1 for i in range(len(s)-1) if pages[i+1]==pages[i] and s[i+1]["rule"]!=x0["rule"]) if False else None
_intra=sum(1 for i in range(len(s)-1) if pages[i+1]==pages[i] and s[i+1]["rule"]==s[i]["rule"])
_inter=sum(1 for i in range(len(s)-1) if pages[i+1]==pages[i] and s[i+1]["rule"]!=s[i]["rule"])
_base=0.12+_speech+_nturn*1.15+_intra*0.28+_inter*0.58+1.5
RULE_GAP=0.58+min(0.9,max(0.0,(56.5-_base)/max(_inter,1)))
print("rule gap",round(RULE_GAP,2))
t=0.12; out=[]; turns=[]
import difflib
letters=lambda w: re.sub(r"[^a-z0-9]","",w.lower())
def align(toks, ws, dur):
    """map printed tokens to ASR word times by character alignment (robust to apostrophes, hyphens, digits)."""
    ref=""; spans=[]
    for k in toks: a=len(ref); ref+=letters(k); spans.append((a,len(ref)))
    hyp=""; ct=[]
    for w in ws:
        L=letters(w["w"]); n=max(len(L),1)
        for c in range(len(L)): ct.append((w["s"]+(w["e"]-w["s"])*c/n, w["s"]+(w["e"]-w["s"])*(c+1)/n))
        hyp+=L
    m={}
    for a,b,size in difflib.SequenceMatcher(a=ref,b=hyp,autojunk=False).get_matching_blocks():
        for q in range(size): m[a+q]=b+q
    out=[]
    for k,(a,b) in enumerate(spans):
        hits=[m[c] for c in range(a,b) if c in m]
        out.append(dict(w=toks[k],s=ct[hits[0]][0],e=ct[hits[-1]][1]) if hits and b>a else dict(w=toks[k],s=None,e=None))
    # fill gaps (unspoken punctuation or unmatched words) by interpolation
    for k,o in enumerate(out):
        if o["s"] is None:
            prev=next((out[q]["e"] for q in range(k-1,-1,-1) if out[q]["e"] is not None),0.0)
            nxt=next((out[q]["s"] for q in range(k+1,len(out)) if out[q]["s"] is not None),dur)
            if not letters(o["w"]): o["s"]=o["e"]=prev
            else:
                o["s"],o["e"]=prev,max(prev,nxt)
    return out
for i,x in enumerate(s):
    toks=x["text"].split()
    ws=align(toks,x["words"],x["dur"])
    unmatched=[o["w"] for o in ws if letters(o["w"]) and o["e"]-o["s"]<=0]
    if unmatched: print("unmatched", i, unmatched)
    # clamp & make monotonic
    prev=0
    for w in ws: w["s"]=max(w["s"],prev); w["e"]=max(w["e"],w["s"]+0.01); prev=w["e"]
    out.append(dict(t0=round(t,3),t1=round(t+x["dur"],3),file=x["file"],words=ws))
    t+=x["dur"]
    if i+1<len(s):
        if pages[i+1]!=pages[i]:
            turns.append(dict(frm=pages[i],to=pages[i+1],t0=round(t+0.15,3),t1=round(t+0.15+0.8,3))); t+=1.15
        elif s[i+1]["rule"]==x["rule"]: t+=0.28
        else: t+=RULE_GAP
end=t+1.5
json.dump(dict(sent=out,turns=turns,end=round(end,3)),open(f"{WD}/timeline.json","w"),indent=1)
print("end",round(end,2),"turns",turns)
