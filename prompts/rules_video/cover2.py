import json, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S="/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad"
FD=f"{S}/fontpk/x_fontpkg_libre_baskerville-2.5-py3-none-any.whl/fontpkg_libre_baskerville/files"
OUT="/home/user/rea-video/prompts/covers"
meta=json.load(open(f"{S}/videos.json"))
C=json.load(open(f"{S}/copy_21_40.json")); KICK={int(k):v["kicker"] for k,v in C.items()}
def font(sz,w,it=False):
    f=ImageFont.truetype(f"{FD}/LibreBaskerville{'-Italic' if it else ''}[wght].ttf",sz); f.set_variation_by_axes([w]); return f
def wrap(words,f,maxw):
    lines=[[]]
    for w in words:
        if lines[-1] and f.getlength(" ".join(lines[-1]+[w]))>maxw: lines.append([])
        lines[-1].append(w)
    return [" ".join(l) for l in lines]
for m in [m for m in meta if m["n"]>=21]:
    n=m["n"]; W,H=1080,1920
    bg=Image.open(f"{S}/v{n}/cover_bg.png").convert("RGB").filter(ImageFilter.GaussianBlur(9))
    a=np.asarray(bg,np.float32)
    y=np.linspace(0,1,H)[:,None,None]
    band=np.exp(-((y-0.45)/0.20)**2)            # darker band behind the title
    a=a*(0.58-0.36*np.exp(-((y-0.47)/0.26)**2))
    bg=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    d=ImageDraw.Draw(bg)
    title=m["title"].upper()
    words=title.split()
    for sz in range(118,60,-4):
        f=font(sz,700); lines=wrap(words,f,900)
        if len(lines)<=3 and max(f.getlength(l) for l in lines)<=900: break
    lh=int(sz*1.18); total=lh*len(lines)
    cy=int(H*0.45); top=cy-total//2
    # kicker
    kf=font(40,700); kick=" ".join(KICK.get(n,"10 RULES"))
    kw=kf.getlength(kick); ky=top-110
    d.text((W/2,ky),kick,font=kf,fill=(212,170,92),anchor="mm")
    d.line([(W/2-kw/2-90,ky),(W/2-kw/2-30,ky)],fill=(212,170,92),width=3)
    d.line([(W/2+kw/2+30,ky),(W/2+kw/2+90,ky)],fill=(212,170,92),width=3)
    # title with soft shadow
    sh=Image.new("L",(W,H),0); ds=ImageDraw.Draw(sh)
    for i,l in enumerate(lines): ds.text((W/2+4,top+i*lh+lh/2+6),l,font=f,fill=255,anchor="mm")
    sh=sh.filter(ImageFilter.GaussianBlur(10))
    bg=Image.composite(Image.new("RGB",(W,H),(0,0,0)),bg,sh.point(lambda v:int(v*0.8)))
    d=ImageDraw.Draw(bg)
    for i,l in enumerate(lines): d.text((W/2,top+i*lh+lh/2),l,font=f,fill=(246,236,214),anchor="mm")
    # hand-drawn gold underline under the last line
    lw=f.getlength(lines[-1]); uy=top+total+18; x0=W/2-lw/2; x1=W/2+lw/2
    xs=np.linspace(x0,x1,300); r=np.random.default_rng(n)
    ys=uy+2.5*np.sin((xs-x0)/90+r.uniform(0,6))+np.linspace(0,r.uniform(-6,6),300)
    for x,yy,k in zip(xs,ys,np.linspace(0,1,300)):
        rad=5*min(1,k/0.03,(1-k)/0.05+0.3)
        d.ellipse([x-rad,yy-rad,x+rad,yy+rad],fill=(212,170,92))
    # small italic line under
    sf=font(38,450,True)
    d.text((W/2,uy+90),"Move in silence.",font=sf,fill=(225,214,190),anchor="mm")
    fn=f"{OUT}/cover{n:02d}_{m['slug']}.jpg"; bg.save(fn,quality=92); print(fn.split('/')[-1])
