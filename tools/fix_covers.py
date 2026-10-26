"""Re-letterbox Crunchyroll / Hulu Originals covers (were 1280x1024, shown stretched in 16:9 tiles).
Logo is cut out undistorted, kept at its original width share (capped at 0.62, the other covers are 0.55-0.62), centred."""
import sys
from PIL import Image, ImageOps
ART = sys.argv[1]
def bbox_white(im, thr=200):
    g = im.convert("L").point(lambda v: 255 if v >= thr else 0); return g.getbbox()
for n in ("crunchyroll", "hulu"):
    src = Image.open(f"/workspace/scratch/{n}_v2.png").convert("RGB")
    bg = src.getpixel((5, 5))
    lb = bbox_white(src); logo = src.crop(lb)
    g = Image.open(f"{ART}/streaming/focus/{n}.gif"); g.seek(g.n_frames // 2); f = g.convert("RGB")
    fb = bbox_white(f, 225); fw = (fb[2] - fb[0]) / f.size[0]; cy = ((fb[1] + fb[3]) / 2) / f.size[1]; cx = ((fb[0] + fb[2]) / 2) / f.size[0]
    W, H = 1280, 720
    fw = min((lb[2] - lb[0]) / src.size[0], 0.62); cx = 0.5; cy = ((lb[1] + lb[3]) / 2) / src.size[1]
    tw = round(W * fw); th = round(logo.size[1] * tw / logo.size[0])   # same aspect as source logo
    logo = logo.resize((tw, th), Image.LANCZOS)
    out = Image.new("RGB", (W, H), bg); out.paste(logo, (round(W * cx - tw / 2), round(H * cy - th / 2)))
    out.save(f"{ART}/streaming/cover/{n}.png", optimize=True)
    print(n, "src", src.size, "logo bbox", lb, "focus rel width %.3f" % fw, "->", out.size, (tw, th))
