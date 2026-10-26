"""Procedurally generate minimalist-style gradient title cards (no AI, no logos).
Matches the look of rsa16/NuvioMinimalistCollection genre cards: soft multi-blob
gradient, bold white title bottom-left, small subtitle. 1280x673 PNG."""
import hashlib, math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT = "/usr/share/fonts/truetype/sand-box/google/Figtree/Figtree-VariableFont_wght.ttf"
W, H = 1280, 673
PALETTES = [
    [(255,94,58),(255,42,104),(40,10,60)], [(0,198,255),(0,114,255),(10,10,40)],
    [(255,177,0),(255,80,0),(60,10,0)],   [(140,82,255),(255,60,172),(20,0,40)],
    [(0,230,160),(0,140,255),(0,20,40)],   [(255,60,60),(120,0,180),(10,0,20)],
    [(255,210,90),(0,170,150),(10,40,50)], [(90,120,255),(170,240,255),(10,20,60)],
]
def card(slug, title, subtitle, out):
    h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    pal = PALETTES[h % len(PALETTES)]
    img = Image.new("RGB", (W, H), pal[2])
    layer = Image.new("RGB", (W, H), pal[2]); d = ImageDraw.Draw(layer)
    for i, col in enumerate(pal[:2] * 2):
        r = 260 + ((h >> (i*5)) % 200)
        cx = int(W * (0.2 + 0.6 * (((h >> (i*7)) % 100) / 100)))
        cy = int(H * (0.05 + 0.6 * (((h >> (i*11)) % 100) / 100)))
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
    img = layer.filter(ImageFilter.GaussianBlur(160))
    # darken bottom-left for legibility
    shade = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(shade)
    for y in range(H):
        sd.line([(0,y),(W,y)], fill=int(150 * max(0, (y - H*0.35)/(H*0.65))))
    img = Image.composite(Image.new("RGB",(W,H),(0,0,0)), img, shade)
    d = ImageDraw.Draw(img)
    ft = ImageFont.truetype(FONT, 118); ft.set_variation_by_axes([800])
    fs = ImageFont.truetype(FONT, 44); fs.set_variation_by_axes([500])
    size = 118
    while d.textlength(title, font=ft) > W - 120 and size > 60:
        size -= 6; ft = ImageFont.truetype(FONT, size); ft.set_variation_by_axes([800])
    d.text((60, H - 120 - size), title, font=ft, fill=(255,255,255))
    if subtitle: d.text((64, H - 100), subtitle, font=fs, fill=(235,235,235))
    img.save(out, optimize=True)
if __name__ == "__main__":
    import json
    for slug, title, sub in json.load(open(sys.argv[1])):
        card(slug, title, sub, os.path.join(sys.argv[2], f"gen-{slug}.png"))
