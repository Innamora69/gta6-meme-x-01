#!/usr/bin/env python3
"""Draw the gta6-meme-x-01 meme (1600x900 PNG) with Pillow.

Scene: a Vice City sunset. The make.fun ghost (official mark-1024.png
from https://make.fun/press/) stands on the road in sunglasses with a
$ pendant while GTA's WASTED screen fires above it. The joke: YOU got
wasted waiting 13 years for GTA VI; the ghost's agent already got paid
on make.fun.

Run: python3 draw_meme.py  ->  meme.png (1600x900)
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1600, 900

BLACK = "/usr/share/fonts/truetype/noto/NotoSansDisplay-Black.ttf"
BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

INK = (18, 10, 36)
GOLD = (245, 197, 66)
SUN_YELLOW = (255, 215, 106)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(draw):
    """Vertical Vice City sunset, purple -> magenta -> orange -> gold."""
    stops = [
        (0.00, (22, 10, 51)),
        (0.35, (91, 26, 110)),
        (0.55, (196, 28, 131)),
        (0.75, (255, 94, 58)),
        (0.92, (255, 179, 71)),
        (1.00, (255, 215, 106)),
    ]
    horizon = 560
    for y in range(horizon):
        t = y / horizon
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                draw.line([(0, y), (W, y)], fill=lerp(c0, c1, f))
                break


def draw_sun(draw):
    cx, cy, r = 1150, 470, 105
    for rr, alpha in ((170, 40), (140, 70), (118, 110)):
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(glow)
        g.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=(255, 200, 90, alpha))
        base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        base.paste(glow, (0, 0), glow)
        draw._image.paste(Image.alpha_composite(
            draw._image.convert("RGBA"), base).convert("RGB"), (0, 0))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 243, 196))


def draw_skyline(draw):
    """Distant Vice City towers along the horizon, a few windows lit."""
    rnd = random.Random(6)
    x = -20
    base = 560
    while x < W + 20:
        bw = rnd.randint(50, 130)
        bh = rnd.randint(40, 130)
        draw.rectangle([x, base - bh, x + bw, base], fill=(28, 16, 51))
        for _ in range(rnd.randint(2, 7)):
            wx = rnd.randint(x + 6, x + bw - 12)
            wy = rnd.randint(base - bh + 8, base - 14)
            draw.rectangle([wx, wy, wx + 6, wy + 8],
                           fill=(255, 200, 90) if rnd.random() < 0.6
                           else (255, 120, 180))
        x += bw + rnd.randint(4, 26)


def draw_ocean(draw):
    draw.rectangle([0, 560, W, 612], fill=(36, 26, 77))
    rnd = random.Random(11)
    for _ in range(26):
        x = rnd.randint(0, W - 120)
        y = rnd.randint(566, 602)
        ln = rnd.randint(40, 140)
        draw.line([(x, y), (x + ln, y)], fill=(255, 154, 92), width=2)


def draw_road(draw):
    draw.polygon([(0, 900), (0, 612), (700, 612), (900, 612), (W, 612),
                  (W, 900)], fill=(23, 18, 38))
    # Edge lines converging on the vanishing point.
    draw.line([(300, 900), (700, 612)], fill=(255, 200, 90), width=4)
    draw.line([(1300, 900), (900, 612)], fill=(255, 200, 90), width=4)
    # Dashed centre line.
    for i in range(6):
        t0 = i / 6
        t1 = (i + 0.45) / 6
        y0 = 612 + (900 - 612) * t0
        y1 = 612 + (900 - 612) * t1
        w0 = 3 + 8 * t0
        draw.line([(800, y0), (800, y1)], fill=(255, 240, 180),
                  width=int(w0))


def tracked_text(draw, cx, y, text, font, fill, stroke, stroke_w,
                 tracking=0):
    """Draw one line centred on cx, letterspaced by `tracking` px."""
    widths = []
    total = 0
    for ch in text:
        w = draw.textlength(ch, font=font)
        widths.append(w)
        total += w
    total += tracking * max(0, len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill,
                  stroke_width=stroke_w, stroke_fill=stroke)
        x += w + tracking
    return total


def fit_font(draw, text, path, start, max_width, tracking=0):
    size = start
    while size > 10:
        f = ImageFont.truetype(path, size)
        w = draw.textlength(text, font=f) + tracking * max(0, len(text) - 1)
        if w <= max_width:
            return f
        size -= 4
    return ImageFont.truetype(path, 10)


def draw_ghost(base):
    """Paste the official mark, then dress it: sunglasses + $ pendant."""
    ghost = Image.open(os.path.join(HERE, "mark-1024.png")).convert("RGBA")
    size = 280
    ghost = ghost.resize((size, size), Image.LANCZOS)
    gx, gy = 660, 505
    base.alpha_composite(ghost, (gx, gy))
    d = ImageDraw.Draw(base)
    # Soft shadow under the floating ghost.
    d.ellipse([gx + 55, gy + size + 2, gx + size - 55, gy + size + 20],
              fill=(0, 0, 0, 110))
    # Sunglasses over the sparkle eyes (fractions from the mark's SVG:
    # sparkle centres at (0.447, 0.406) and (0.597, 0.387)).
    for fx, fy in ((0.447, 0.406), (0.597, 0.387)):
        lx = gx + fx * size - 18
        ly = gy + fy * size - 13
        d.rounded_rectangle([lx, ly, lx + 36, ly + 26], radius=9,
                            fill=(10, 8, 16, 255))
    d.line([(gx + 0.447 * size + 18, gy + 0.406 * size),
            (gx + 0.597 * size - 18, gy + 0.387 * size)],
           fill=(10, 8, 16, 255), width=6)
    # $ pendant on the ghost's lower body: the "already paid" signal.
    px, py = gx + size // 2, gy + int(size * 0.72)
    d.ellipse([px - 24, py - 24, px + 24, py + 24],
              fill=GOLD + (255,), outline=(120, 80, 0, 255), width=3)
    f = ImageFont.truetype(BOLD, 32)
    d.text((px, py), "$", font=f, fill=(20, 12, 0, 255), anchor="mm")


def main():
    img = Image.new("RGB", (W, H), (22, 10, 51))
    draw = ImageDraw.Draw(img)
    sky_gradient(draw)
    draw_sun(draw)
    draw_skyline(draw)
    draw_ocean(draw)
    draw_road(draw)
    # No palms: the first render's thin silhouettes read as cranes, not
    # trees, and the skyline + sun + road already say Vice City.

    # Title card.
    title = "GRAND THEFT AUTO VI"
    tf = fit_font(draw, title, BOLD, 52, 1200, tracking=10)
    tracked_text(draw, W // 2, 26, title, tf, (255, 255, 255),
                 (10, 8, 16), 4, tracking=10)

    # The GTA punchline.
    wf = fit_font(draw, "WASTED", BLACK, 290, 1420, tracking=22)
    tracked_text(draw, W // 2, 88, "WASTED", wf, (255, 255, 255),
                 (10, 8, 16), 12, tracking=22)

    # The ghost, dressed rich.
    rgba = img.convert("RGBA")
    draw_ghost(rgba)
    img = rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    # The two-line payoff, big enough to read at 768 px wide:
    # the wait above the ghost, the payoff below it.
    l1 = "13 YEARS WAITING FOR GTA VI."
    f1 = fit_font(draw, l1, BOLD, 54, 1480, tracking=2)
    tracked_text(draw, W // 2, 438, l1, f1, (255, 255, 255),
                 (10, 8, 16), 5, tracking=2)
    l2 = "MY AGENT GOT PAID ON MAKE.FUN."
    f2 = fit_font(draw, l2, BOLD, 54, 1480, tracking=2)
    tracked_text(draw, W // 2, 812, l2, f2, SUN_YELLOW,
                 (10, 8, 16), 5, tracking=2)

    out = os.path.join(HERE, "meme.png")
    img.save(out, "PNG")
    print("saved", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
