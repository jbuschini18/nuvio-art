"""Rebuild Discover focus GIFs + covers at streaming-tile quality.
Old: 400x225 GIF (latest 564x320), text baked in and dithered -> jagged when upscaled on a 4K TV.
New: the original animated gradient is kept (text removed by inpainting, upscaled 2x), and the
label is re-drawn as clean anti-aliased vector text (Inter Bold, 4x supersampled) at 800x450,
encoded as animated WebP (q85; GIF at this size was 9-31 MB because of the dithering). Cover = 1280x720 PNG."""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ART = sys.argv[1]; SRC = sys.argv[2]           # SRC = folder with the v2 discover/ files
FONT = "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"
LABELS = {"popular": "Popular", "trending": "Trending", "top-rated": "Top Rated",
          "recommended": "Recommended", "anticipated": "Anticipated", "latest": "Latest"}

def frames(path):
    im = Image.open(path); out = []
    for i in range(im.n_frames):
        im.seek(i); out.append((im.convert("RGB"), im.info.get("duration", 70)))
    return out

def text_mask(rgb):
    a = np.asarray(rgb).astype(int); mn = a.min(2); mx = a.max(2)
    m = (mn > 215) & (mx - mn < 40)                 # near-white, unsaturated = label pixels
    return m

def blur_fill(rgb, mask, r=12):
    a = np.asarray(rgb).astype(np.float32); w = (~mask).astype(np.float32)
    def box(x, k, ax):
        pad = [(0, 0)] * x.ndim; pad[ax] = (k + 1, k); xp = np.pad(x, pad, mode="edge"); c = np.cumsum(xp, axis=ax)
        hi = np.take(c, range(2 * k + 1, c.shape[ax]), axis=ax); lo = np.take(c, range(0, c.shape[ax] - 2 * k - 1), axis=ax)
        return (hi - lo) / (2 * k + 1)
    def gb(x):                                   # 3 box passes ~ gaussian
        for _ in range(3): x = box(box(x, r, 0), r, 1)
        return x
    num = np.stack([gb(a[..., c] * w) for c in range(3)], 2); den = gb(w)[..., None] + 1e-4
    fill = num / den; out = np.where(mask[..., None], fill, a)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))

def label_box(fr):
    """Label = pixels that stay near-white in >=85% of frames (the gradient moves, the text doesn't)."""
    sample = fr[:: max(1, len(fr) // 24)]; cnt = None
    for rgb, _ in sample:
        m = text_mask(rgb).astype(np.int32); cnt = m if cnt is None else cnt + m
    acc = cnt >= 0.85 * len(sample); h, w = acc.shape; acc[: h // 4] = False
    ys, xs = np.nonzero(acc); return (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1), acc

def font(px):
    f = ImageFont.truetype(FONT, px)
    try: f.set_variation_by_axes([max(14, min(32, px)), 700])
    except Exception: pass
    return f

def draw_label(img, text, box, scale):
    W, H = img.size; S = 4
    x0, y0, x1, y1 = [v * scale for v in box]; target_w = x1 - x0
    px = 10
    while True:                                     # fit cap-to-baseline width to original label
        f = font(px * S); b = f.getbbox(text)
        if (b[2] - b[0]) / S >= target_w or px > 400: break
        px += 1
    layer = Image.new("L", (W * S, H * S), 0); d = ImageDraw.Draw(layer)
    b = f.getbbox(text); d.text((x0 * S - b[0], y0 * S - b[1]), text, font=f, fill=255)
    a = layer.resize((W, H), Image.LANCZOS)
    shadow = a.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.25))
    img.paste((0, 0, 0), (0, 0), shadow); img.paste((255, 255, 255), (0, 0), a)
    return img

def encode_webp(pngs_dir, durs, out_webp):
    """Animated WebP: 24-bit colour + smooth anti-aliased text, far smaller than GIF.
    Same format as the studio focus tiles (luckynumb3rs animated .webp) already working in his Nuvio."""
    fs = sorted(os.listdir(pngs_dir)); ims = [Image.open(os.path.join(pngs_dir, f)).convert("RGB") for f in fs]
    ims[0].save(out_webp, save_all=True, append_images=ims[1:], duration=durs, loop=0, quality=85, method=5)

def encode(pngs_dir, durs, out_gif):
    # constant frame rate from the source (they are constant per file)
    fps = round(1000 / durs[0], 3)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{pngs_dir}/%04d.png", "-vf",
                    "split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=bayer:bayer_scale=5",
                    "-loop", "0", out_gif + ".raw.gif"], check=True)
    subprocess.run(["gifsicle", "-O3", "--lossy=20", out_gif + ".raw.gif", "-o", out_gif], check=True)
    os.remove(out_gif + ".raw.gif")

for slug, label in LABELS.items():
    fr = frames(f"{SRC}/discover/focus/{slug}.gif")
    w0, h0 = fr[0][0].size
    W, H = 800, 450; scale = W / w0
    box, _ = label_box(fr)
    if label is None:
        print(slug, "skipped (optional folder; source label not standard)"); continue
    with tempfile.TemporaryDirectory() as td:
        for i, (rgb, dur) in enumerate(fr):
            m = text_mask(rgb); mm = np.zeros_like(m)
            x0, y0, x1, y1 = box; mm[max(0, y0 - 4):y1 + 4, max(0, x0 - 4):x1 + 4] = True
            m = Image.fromarray(((m & mm) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))
            bg = blur_fill(rgb, np.asarray(m) > 0)
            big = bg.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
            draw_label(big, label, box, scale).save(f"{td}/{i:04d}.png")
            if i == 0:
                cov = bg.resize((1280, 720), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
                draw_label(cov, label, box, 1280 / w0).save(f"{ART}/discover/cover/{slug}.png", optimize=True)
        encode_webp(td, [d for _, d in fr], f"{ART}/discover/focus/{slug}.webp")
    old = f"{ART}/discover/focus/{slug}.gif"
    if os.path.exists(old) and os.path.exists(f"{SRC}/discover/focus/{slug}.gif") and open(old,"rb").read() != open(f"{SRC}/discover/focus/{slug}.gif","rb").read():
        os.remove(old)                              # drop the oversized GIF attempt; keep v2 original only if untouched
    print(slug, f"{w0}x{h0} -> {W}x{H}", len(fr), "frames", os.path.getsize(f"{ART}/discover/focus/{slug}.webp") // 1024, "KB")
