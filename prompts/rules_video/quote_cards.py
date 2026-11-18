import json, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S="/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad"
FD=f"{S}/fontpk/x_fontpkg_libre_baskerville-2.5-py3-none-any.whl/fontpkg_libre_baskerville/files"
OUT=f"{S}/daily"; os.makedirs(OUT,exist_ok=True)
GOLD=(212,170,92); INK=(28,32,66); TEXT=(36,28,22)
W,H=1080,1350
def font(sz,w,it=False):
    f=ImageFont.truetype(f"{FD}/LibreBaskerville{'-Italic' if it else ''}[wght].ttf",sz); f.set_variation_by_axes([w]); return f
def noise(w,h,sc,seed):
    r=np.random.default_rng(seed); s=r.standard_normal((max(2,h//sc),max(2,w//sc))).astype(np.float32)
    im=Image.fromarray(((s-s.min())/(np.ptp(s)+1e-6)*255).astype(np.uint8)).resize((w,h),Image.BICUBIC)
    a=np.asarray(im,np.float32)/255; return (a-a.mean())/(a.std()+1e-6)
# --- static background: dark brown desk + lamp glow
y,x=np.mgrid[0:H,0:W].astype(np.float32)
glow=np.exp(-(((x-W*0.30)/(W*0.9))**2+((y-H*0.22)/(H*0.8))**2))
grain=noise(W,H,0,1) if False else noise(W,H,6,1)*0.4+noise(W,H,60,2)*0.6
desk=np.array([40,26,17],np.float32)*(0.55+0.75*glow)[...,None]*(1+0.06*grain[...,None])
BG=Image.fromarray(np.clip(desk,0,255).astype(np.uint8))
# page
PX0,PY0,PX1,PY1=90,120,990,1170; PW,PH=PX1-PX0,PY1-PY0
py,px=np.mgrid[0:PH,0:PW].astype(np.float32)
pap=np.array([238,228,206],np.float32)[None,None,:]+(4*noise(PW,PH,120,3)+2*noise(PW,PH,14,4))[...,None]
shade=(1-0.40*np.exp(-px/40)-0.12*np.exp(-px/200))*(1-0.08*np.exp(-np.minimum.reduce([PW-1-px,py,PH-1-py])/24))
lamp=0.70+0.38*np.exp(-(((px+PX0-W*0.25)/(W*0.85))**2+((py+PY0-H*0.15)/(H*0.85))**2))
pap=pap*(shade*lamp)[...,None]*np.array([1,0.95,0.86])
PAGE=Image.fromarray(np.clip(pap,0,255).astype(np.uint8))
sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).rectangle([PX0+14,PY0+22,PX1+14,PY1+22],fill=210); sh=sh.filter(ImageFilter.GaussianBlur(22))
BG=Image.composite(Image.new("RGB",(W,H),(6,4,3)),BG,sh)
# page-edge stack on the right/bottom
d=ImageDraw.Draw(BG)
for k in range(6):
    c=200-k*18; d.rectangle([PX0+4,PY1+2+k*2,PX1+4+k*2,PY1+3+k*2],fill=(c,c-8,c-22)); d.rectangle([PX1+2+k*2,PY0+4,PX1+3+k*2,PY1+4+k*2],fill=(c,c-8,c-22))
BG.paste(PAGE,(PX0,PY0))

def wrap(text,f,maxw):
    lines=[[]]
    for w in text.split():
        if lines[-1] and f.getlength(" ".join(lines[-1]+[w]))>maxw: lines.append([])
        lines[-1].append(w)
    return [" ".join(l) for l in lines]
def underline(d,x0,x1,yy,seed):
    r=np.random.default_rng(seed); L=x1-x0; xs=np.linspace(x0,x1,max(30,int(L)))
    ys=yy+1.3*np.sin(xs/r.uniform(60,110)+r.uniform(0,6))+np.linspace(0,r.uniform(-2.5,2.5),len(xs))
    for xx,y2,k in zip(xs,ys,np.linspace(0,1,len(xs))):
        rad=2.6*min(1,k/0.02+0.4,(1-k)/0.03+0.4); d.ellipse([xx-rad,y2-rad,xx+rad,y2+rad],fill=INK)
ROMAN=["I","II","III","IV","V","VI","VII","VIII","IX","X"]
def card(rule_text,rule_no,topic,seed,fn):
    im=BG.copy(); d=ImageDraw.Draw(im)
    TX0=PX0+110; TW=PW-110-90
    for sz in range(66,38,-2):
        f=font(sz,440); lines=wrap(rule_text,f,TW); lh=int(sz*1.62)
        if lh*len(lines)<=560: break
    total=lh*len(lines); top=PY0+(PH-total)//2+5
    # header: chapter label
    hf=font(30,450,True); d.text((PX0+PW/2+10,PY0+120),f"{topic}",font=hf,fill=(120,98,72),anchor="mm")
    d.text((PX0+PW/2+10,PY0+175),f"Rule {ROMAN[rule_no-1]}",font=font(34,700),fill=(150,112,58),anchor="mm")
    for i,l in enumerate(lines):
        base=top+i*lh+int(sz*0.9)
        d.text((TX0,base),l,font=f,fill=TEXT,anchor="ls")
        underline(d,TX0-4,TX0+f.getlength(l)+6,base+14,seed*31+i)
    # footer branding on the desk
    ff=font(30,700); d.text((W/2,PY1+70)," ".join("THE SILENT CODE"),font=ff,fill=GOLD,anchor="mm")
    d.text((W/2,PY1+112),"@thesilentcode",font=font(24,450,True),fill=(196,176,140),anchor="mm")
    im.save(fn,quality=93)

meta=json.load(open(f"{S}/videos.json"))
TOPIC={m["n"]:m["title"] for m in meta}
items=[]
for day in range(200):
    n=day%20+1; r=day//20
    rules=json.load(open(f"{S}/v{n}/rules.json"))[:10]
    items.append(dict(day=day+1,video=n,rule=r+1,topic=TOPIC[n],text=rules[r]))
for it in items:
    fn=f"{OUT}/day{it['day']:03d}.jpg"; card(it["text"],it["rule"],it["topic"],it["day"],fn); it["file"]=os.path.basename(fn)
json.dump(items,open(f"{S}/daily_items.json","w"),indent=1)
print(len(items))
