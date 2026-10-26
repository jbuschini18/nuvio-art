import numpy as np, cairosvg, io, subprocess, os, sys, shutil
from PIL import Image
W,H,FPS,N=800,450,30,180
def white_logo(svg,width,crop=None):
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=svg,output_width=width*3 if crop else width))).convert('RGBA')
    if crop:  # crop as fraction of width (x0,x1), then rescale to target width
        x0,x1=crop; im=im.crop((int(im.width*x0),0,int(im.width*x1),im.height)); im=im.resize((width,int(im.height*width/im.width)),Image.LANCZOS)
    a=np.array(im); a[...,:3]=255; im=Image.fromarray(a)
    bb=im.getbbox(); return im.crop(bb)
TILES={
 'peacock':dict(svg='src/peacock_2026.svg',cols=[(200,20,200),(110,100,255),(90,70,240),(70,40,210)],base=(34,18,92),inten=.9,rad=(.2,.32),seed=3,lw=.36),
 'starz':  dict(svg='src/starz_2022.svg',cols=[(125,132,136),(90,100,105),(55,105,112),(140,145,148)],base=(22,25,28),inten=.8,rad=(.2,.32),seed=11,lw=.34),
 'shudder':dict(svg='src/shudder_2017.svg',cols=[(230,40,40),(200,0,10),(240,90,90),(170,0,0)],base=(80,0,6),inten=.9,rad=(.2,.32),seed=5,lw=.38),
 'discoveryplus':dict(svg='src/discoveryplus.svg',cols=[(40,120,255),(0,160,255),(60,140,250),(110,180,255)],base=(6,36,120),inten=.85,rad=(.2,.32),seed=8,lw=.38,crop=(0.27,1.0)),
}
yy,xx=np.mgrid[0:H,0:W]; xx=xx/W; yy=yy/H*(H/W)
def build(name,p,lossy=200):
    rng=np.random.default_rng(p['seed'])
    B=[dict(c=np.array(c)/255,cx=rng.uniform(.1,.9),ax=rng.uniform(.22,.34),cy=rng.uniform(.05,.5),ay=rng.uniform(.10,.17),
        k1=int(rng.choice([1,2])),k2=int(rng.choice([1,2])),p1=rng.uniform(0,6.3),p2=rng.uniform(0,6.3),r=rng.uniform(*p['rad'])) for c in p['cols']]
    base=np.array(p['base'])/255
    L=white_logo(p['svg'],int(W*p['lw']),p.get('crop')); pos=((W-L.width)//2,(H-L.height)//2)
    d=f'tmp_{name}'; os.makedirs(d,exist_ok=True)
    for f in range(N):
        t=2*np.pi*f/N; acc=np.ones((H,W,3))
        for b in B:
            cx=b['cx']+b['ax']*np.sin(b['k1']*t+b['p1']); cy=b['cy']+b['ay']*np.cos(b['k2']*t+b['p2'])
            g=np.exp(-((xx-cx)**2+(yy-cy)**2)/b['r']**2)[...,None]; acc*=(1-b['c']*g*p['inten'])
        img=1-acc*(1-base)
        fr=Image.fromarray((np.clip(img,0,1)*255+0.5).astype(np.uint8)).convert('RGBA'); fr.alpha_composite(L,pos)
        fr.convert('RGB').save(f'{d}/{f:03d}.png')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{d}/%03d.png','-vf',
      'split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=bayer:bayer_scale=5','-loop','0',f'{name}_raw.gif'],check=True)
    subprocess.run(['gifsicle','-O3',f'--lossy={lossy}',f'{name}_raw.gif','-o',f'{name}.gif'],check=True); os.remove(f'{name}_raw.gif')
    C=Image.new('RGBA',(1280,720),(51,51,51,255)); L2=white_logo(p['svg'],int(1280*.60),p.get('crop')); C.alpha_composite(L2,((1280-L2.width)//2,(720-L2.height)//2)); C.save(f'{name}_cover.png')
    shutil.rmtree(d); print(name,os.path.getsize(f'{name}.gif'),os.path.getsize(f'{name}_cover.png'))
if __name__=='__main__':
    for n in (sys.argv[1:] or TILES): build(n,TILES[n])
