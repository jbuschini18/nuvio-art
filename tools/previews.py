from PIL import Image, ImageDraw, ImageFont
FP='/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf'; F=ImageFont.truetype(FP,22)
names=['popular','trending','top-rated','recommended','anticipated','latest']; W,H=800,450
def fr(p,frac=0.5):
    im=Image.open(p); n=getattr(im,'n_frames',1)
    if n>1: im.seek(int(n*frac))
    return im.convert('RGB')
s=Image.new('RGB',(W*2+30,(H+34)*len(names)+40),(20,20,20)); d=ImageDraw.Draw(s)
d.text((10,8),'BEFORE (v2, 400x225 GIF upscaled)',font=F,fill='white'); d.text((W+30,8),'AFTER (v3, 800x450 animated WebP)',font=F,fill='white')
for i,n in enumerate(names):
    y=40+i*(H+34)
    s.paste(fr(f'nuvio-art-v2/discover/focus/{n}.gif').resize((W,H),Image.BILINEAR),(10,y+28))
    s.paste(fr(f'nuvio-art-v3/discover/focus/{n}.webp').resize((W,H)),(W+20,y+28)); d.text((10,y+2),n,font=F,fill='white')
s.save('previews/discover_focus_before_after.png')
z=Image.new('RGB',(1200,len(names)*250),(20,20,20))
for i,n in enumerate(names):
    a=fr(f'nuvio-art-v2/discover/focus/{n}.gif').resize((1600,900),Image.BILINEAR).crop((0,450,600,700))
    b=fr(f'nuvio-art-v3/discover/focus/{n}.webp').resize((1600,900),Image.LANCZOS).crop((0,450,600,700))
    z.paste(a,(0,i*250)); z.paste(b,(600,i*250))
z.save('previews/discover_text_zoom_before_after.png')
c=Image.new('RGB',(1310,394*len(names)+40),(20,20,20)); d=ImageDraw.Draw(c)
d.text((10,8),'Cover BEFORE (400x225)',font=F,fill='white'); d.text((660,8),'Cover AFTER (1280x720)',font=F,fill='white')
for i,n in enumerate(names):
    y=40+i*394
    c.paste(Image.open(f'nuvio-art-v2/discover/cover/{n}.png').convert('RGB').resize((640,360),Image.BILINEAR),(10,y+28))
    c.paste(Image.open(f'nuvio-art-v3/discover/cover/{n}.png').convert('RGB').resize((640,360),Image.LANCZOS),(660,y+28)); d.text((10,y+2),n,font=F,fill='white')
c.save('previews/discover_covers_before_after.png')
t=Image.new('RGB',(640*3+40,2*394+40),(20,20,20)); d=ImageDraw.Draw(t); f16=ImageFont.truetype(FP,16)
for j,lab in enumerate(['BEFORE: v2 cover (1280x1024) as shown in a 16:9 tile = squashed','AFTER: v3 cover 1280x720, logo undistorted','Focused GIF (unchanged)']):
    d.text((10+j*650,8),lab,font=f16,fill='white')
for i,n in enumerate(['crunchyroll','hulu']):
    y=40+i*394
    t.paste(Image.open(f'/workspace/scratch/{n}_v2.png').convert('RGB').resize((640,360)),(10,y+28))
    t.paste(Image.open(f'nuvio-art-v3/streaming/cover/{n}.png').convert('RGB').resize((640,360),Image.LANCZOS),(660,y+28))
    t.paste(fr(f'nuvio-art-v3/streaming/focus/{n}.gif').resize((640,360)),(1310,y+28)); d.text((10,y+2),n,font=F,fill='white')
t.save('previews/crunchyroll_hulu_before_after.png')
