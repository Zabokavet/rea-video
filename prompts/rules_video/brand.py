import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S="/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad"
FD=f"{S}/fontpk/x_fontpkg_libre_baskerville-2.5-py3-none-any.whl/fontpkg_libre_baskerville/files"
OUT="/home/user/rea-video/prompts/brand"
GOLD=(212,170,92); CREAM=(246,236,214)
def font(sz,w,it=False):
    f=ImageFont.truetype(f"{FD}/LibreBaskerville{'-Italic' if it else ''}[wght].ttf",sz); f.set_variation_by_axes([w]); return f
def ink(d,x0,x1,y,th,seed,col=GOLD):
    r=np.random.default_rng(seed); xs=np.linspace(x0,x1,500)
    ys=y+th*0.5*np.sin((xs-x0)/((x1-x0)/3.2)+r.uniform(0,6))+np.linspace(0,th*0.8,500)
    for x,yy,k in zip(xs,ys,np.linspace(0,1,500)):
        rad=th*min(1,k/0.03+0.25,(1-k)/0.06+0.25); d.ellipse([x-rad,yy-rad,x+rad,yy+rad],fill=col)
def radial(w,h,cx,cy,inner,outer,scale):
    y,x=np.mgrid[0:h,0:w].astype(np.float32); r=np.sqrt(((x-cx)/scale)**2+((y-cy)/scale)**2)
    t=np.clip(r,0,1)[...,None]; img=np.array(inner)*(1-t)+np.array(outer)*t
    img+=np.random.default_rng(1).normal(0,2.2,img.shape)
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8))

# ---------- profile picture (circle-safe, 1080x1080; works for YouTube 800x800 + TikTok)
P=1080
im=radial(P,P,P*0.42,P*0.38,(58,44,32),(12,10,9),P*0.75); d=ImageDraw.Draw(im)
d.ellipse([60,60,P-60,P-60],outline=GOLD,width=6)
d.ellipse([84,84,P-84,P-84],outline=(GOLD[0],GOLD[1],GOLD[2]),width=2)
f=font(400,700); d.text((P/2,P/2-40),"SC",font=f,fill=CREAM,anchor="mm")
ink(d,P/2-230,P/2+230,P/2+170,9,3)
sf=font(46,700); d.text((P/2,P/2+265)," ".join("THE SILENT CODE"),font=font(40,700),fill=GOLD,anchor="mm")
im.save(f"{OUT}/profile_picture_1080.png"); im.resize((800,800),Image.LANCZOS).save(f"{OUT}/profile_picture_youtube_800.png")
im.resize((200,200),Image.LANCZOS).save(f"{OUT}/profile_picture_tiktok_200.png")

# ---------- YouTube banner 2560x1440 (text inside the 1546x423 safe area)
W,H=2560,1440
bg=Image.open(f"{S}/v1/cover_bg.png").convert("RGB")
band=bg.crop((0,420,1080,420+608)).resize((W,int(608*W/1080)),Image.BICUBIC).crop((0,0,W,H)) if False else bg.resize((W,int(1920*W/1080)),Image.BICUBIC).crop((0,1300,W,1300+H))
band=band.filter(ImageFilter.GaussianBlur(30))
a=np.asarray(band,np.float32); y=np.linspace(0,1,H)[:,None,None]; x=np.linspace(0,1,W)[None,:,None]
a=a*(0.42-0.22*np.exp(-((y-0.5)/0.18)**2))*(1-0.35*np.abs(x-0.5)*2)
b=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); d=ImageDraw.Draw(b)
tf=font(118,700); d.text((W/2,H/2-60),"THE SILENT CODE",font=tf,fill=CREAM,anchor="mm")
tw=tf.getlength("THE SILENT CODE"); ink(d,W/2-tw/2,W/2+tw/2,H/2+28,6,5)
d.text((W/2,H/2+105),"Rules nobody teaches you.  One rule every day.",font=font(46,450,True),fill=(228,216,192),anchor="mm")
b.save(f"{OUT}/youtube_banner_2560x1440.png")
# preview of what phones see (safe area)
b.crop(((W-1546)//2,(H-423)//2,(W+1546)//2,(H+423)//2)).save(f"{S}/banner_safe_preview.png")
print("ok")
