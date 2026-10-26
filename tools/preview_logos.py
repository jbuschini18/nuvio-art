from PIL import Image, ImageDraw, ImageFont
B='/workspace/nuvio/drafts/final/nuvio-art-v4/genres/title/'
fs=['adventure','war','action','thriller']
s=Image.new('RGB',(1500,620),(24,24,28)); d=ImageDraw.Draw(s)
F=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf',20)
for i,n in enumerate(fs):
    im=Image.open(B+n+'.webp').convert('RGBA'); im.thumbnail((640,130)); x=40+(i%2)*740; y=40+(i//2)*290
    s.paste(im,(x,y+40),im); d.text((x,y),('NEW: ' if i<2 else 'existing: ')+n+f'  ({Image.open(B+n+".webp").size[0]}x{Image.open(B+n+".webp").size[1]})',font=F,fill=(170,170,170))
s.save('/workspace/nuvio/drafts/final/previews/adventure_war_logos.png')
