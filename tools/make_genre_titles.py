"""Code-drawn genre title logos (no AI) matching the luckynumb3rs genre titles:
pure-white RGBA on transparency, tight crop (0 px padding), ~260-300 px tall, themed display font
with one letter swapped for a small drawn icon. Rendered at 4x and downsampled for clean edges."""
import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops
G = "/usr/share/fonts/truetype/sand-box/google/"
S = 4  # supersample

def text_mask(txt, font_path, px):
    f = ImageFont.truetype(font_path, px * S); b = f.getbbox(txt)
    m = Image.new("L", (b[2] - b[0] + 40 * S, b[3] - b[1] + 320 * S), 0)
    ImageDraw.Draw(m).text((20 * S - b[0], 140 * S - b[1]), txt, font=f, fill=255)
    return m, f, (20 * S - b[0], 140 * S - b[1])

def star(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n); rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

def finish(m, out, height):
    bb = m.getbbox(); m = m.crop(bb)
    w = round(m.size[0] * height / m.size[1]); m = m.resize((w, height), Image.LANCZOS)
    im = Image.new("RGBA", m.size, (255, 255, 255, 0)); im.putalpha(m)
    im.save(out, "WEBP", quality=90, alpha_quality=100, method=6); print(out, im.size)

def adventure(out):
    # Alfa Slab One; first "A" becomes a snow-capped mountain with a flag on the summit,
    # and a compass star sits above the "V" (like Action's star / Animation's sparkle).
    txt = "ADVENTURE"; m, f, (ox, oy) = text_mask(txt, G + "Alfa Slab One/AlfaSlabOne-Regular.ttf", 300)
    d = ImageDraw.Draw(m)
    a_l, a_t, a_r, a_b = f.getbbox("A"); a_l += ox; a_r += ox; a_t += oy; a_b += oy
    ah = a_b - a_t; aw = a_r - a_l; apex_x = a_l + aw * 0.5
    # snow line: zig-zag knock-out band across the upper third of the A
    y0 = a_t + ah * 0.34; zz = []
    n = 6
    for i in range(n + 1):
        x = a_l + aw * (0.18 + 0.64 * i / n); zz.append((x, y0 + (14 * S if i % 2 else -2 * S)))
    band = zz + [(p[0], p[1] + 16 * S) for p in reversed(zz)]
    d.polygon(band, fill=0)
    # summit flag
    pole_top = a_t - ah * 0.42
    d.rectangle([apex_x - 7 * S, pole_top, apex_x + 7 * S, a_t + 10 * S], fill=255)
    d.polygon([(apex_x + 5 * S, pole_top), (apex_x + 5 * S + aw * 0.42, pole_top + ah * 0.11), (apex_x + 5 * S, pole_top + ah * 0.22)], fill=255)
    # compass star above the V
    v_off = f.getlength("AD"); v_w = f.getlength("V")
    cx = ox + v_off + v_w * 0.5; cy = a_t - ah * 0.26
    d.polygon(star(cx, cy, ah * 0.27, ah * 0.06, n=4, rot=-90), fill=255)
    d.polygon(star(cx, cy, ah * 0.15, ah * 0.045, n=4, rot=-45), fill=255)
    d.ellipse([cx - ah * 0.035, cy - ah * 0.035, cx + ah * 0.035, cy + ah * 0.035], fill=0)
    finish(m, out, 300)

def war(out):
    # Black Ops One (military stencil); the "A" crossbar becomes a knocked-out star,
    # with two rank chevrons under the word.
    txt = "WAR"; m, f, (ox, oy) = text_mask(txt, G + "Black Ops One/BlackOpsOne-Regular.ttf", 300)
    d = ImageDraw.Draw(m)
    w_off = f.getlength("W"); a_w = f.getlength("A")
    l, t, r, b = f.getbbox(txt); t += oy; b += oy; h = b - t
    am = Image.new("L", m.size, 0); ImageDraw.Draw(am).text((ox + w_off, oy), "A", font=f, fill=255)
    ab = am.getbbox(); cx = (ab[0] + ab[2]) / 2; cy = t + h * 0.62          # centre of the A's actual ink
    d.polygon(star(cx, cy, h * 0.21, h * 0.085), fill=0)
    d.polygon(star(cx, cy, h * 0.13, h * 0.052), fill=255)
    # chevrons centred under the word
    x0 = ox + l; x1 = ox + r; mid = (x0 + x1) / 2; cw = (x1 - x0) * 0.16; th = h * 0.075; dep = h * 0.09
    for k in range(2):
        y = b + h * 0.09 + k * h * 0.20
        d.polygon([(mid - cw, y), (mid, y + dep), (mid + cw, y), (mid + cw, y + th), (mid, y + dep + th), (mid - cw, y + th)], fill=255)
    finish(m, out, 300)

if __name__ == "__main__":
    art = sys.argv[1]
    adventure(f"{art}/genres/title/adventure.webp"); war(f"{art}/genres/title/war.webp")
