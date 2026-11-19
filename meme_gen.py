#!/usr/bin/env python3
"""Draw the GTA 6 launch-week meme for make.fun's gta6-meme-x-01 bounty.

Pure Python (stdlib + PIL). Everything is drawn in code: a Vice City sunset
beach, a fan who called in sick for GTA 6 playing on a handheld, and the
make.fun ghost sitting beside him in its own beach chair, holding its magenta
star coin. No Rockstar artwork, no downloaded assets, no network, no clock:
the same code draws the same bytes every run.

Joke: waited 13 years for GTA 6, called in sick for launch week, while my
AI agent earns on make.fun.
"""

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
OUT = Path(__file__).resolve().parent / "meme.png"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, top, bottom, c_top, c_bottom):
    """Vertical gradient from c_top at y=top to c_bottom at y=bottom."""
    for y in range(top, bottom):
        t = (y - top) / max(1, bottom - top - 1)
        draw.line([(0, y), (W, y)], fill=lerp(c_top, c_bottom, t))


def text_center(draw, cx, y, text, fnt, fill, stroke=0, stroke_fill=(0, 0, 0)):
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2 - bbox[0], y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)


def star_points(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sparkle_points(cx, cy, s):
    """Four-pointed sparkle: N, E, S, W tips with concave waists."""
    k = 0.26
    return [(cx, cy - s), (cx + s * k, cy - s * k), (cx + s, cy),
            (cx + s * k, cy + s * k), (cx, cy + s),
            (cx - s * k, cy + s * k), (cx - s, cy),
            (cx - s * k, cy - s * k)]


def ghost_layer(cx, top, scale=1.0):
    """The make.fun ghost on its own RGBA layer: white body, thick black
    outline, two black four-pointed sparkle eyes. Returns the layer plus the
    ghost's bounding box, so the caller can place a hand and a coin."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    w = int(150 * scale)
    h = int(190 * scale)
    x0, x1 = cx - w // 2, cx + w // 2
    y0 = top
    # Dome, body, and three scallops at the hem.
    md.ellipse([x0, y0, x1, y0 + w], fill=255)
    md.rectangle([x0, y0 + w // 2, x1, y0 + h - 28 * scale], fill=255)
    for i in range(3):
        scx = x0 + w * (i + 0.5) / 3
        r = w / 6
        md.ellipse([scx - r, y0 + h - 28 * scale - r, scx + r,
                    y0 + h - 28 * scale + r], fill=255)
    # Thick outline: dilate the mask, paint it black, then the white body.
    dilated = mask.filter(ImageFilter.MaxFilter(int(13 * scale) | 1))
    ld = ImageDraw.Draw(layer)
    layer.paste((10, 10, 10, 255), (0, 0), dilated)
    layer.paste((255, 255, 255, 255), (0, 0), mask)
    # Eyes.
    ey = y0 + int(78 * scale)
    es = int(15 * scale)
    for ex in (cx - int(32 * scale), cx + int(32 * scale)):
        ld.polygon(sparkle_points(ex, ey, es), fill=(10, 10, 10, 255))
    return layer, (x0, y0, x1, y0 + h)


def coin(draw, cx, cy, r):
    """Magenta coin with a white five-pointed star, black outline."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(230, 0, 126),
                 outline=(10, 10, 10), width=4)
    draw.polygon(star_points(cx, cy, r * 0.62, r * 0.26), fill=(255, 255, 255))


def palm(draw, bx, by, height, lean, color):
    """A palm silhouette: curved trunk and six drooping fronds."""
    top_x = bx + lean
    top_y = by - height
    # Trunk: stacked segments, curving toward the crown.
    segs = 9
    px, py = bx, by
    for i in range(1, segs + 1):
        t = i / segs
        nx = bx + lean * t * t
        ny = by - height * t
        draw.line([(px, py), (nx, ny)], fill=color, width=13)
        px, py = nx, ny
    # Fronds: arcs from the crown, drooping down and out.
    for ang in (-165, -135, -105, -75, -45, -15):
        a = math.radians(ang)
        x2 = top_x + int(95 * math.cos(a))
        y2 = top_y + int(95 * math.sin(a)) + 55
        mx = top_x + int(55 * math.cos(a))
        my = top_y + int(55 * math.sin(a)) + 8
        draw.line([(top_x, top_y), (mx, my), (x2, y2)], fill=color, width=9)
    draw.ellipse([top_x - 12, top_y - 12, top_x + 12, top_y + 12], fill=color)


def chair(draw, cx, base_y, back_color, seat_color):
    """A simple beach chair: tilted backrest, seat, and legs."""
    # Backrest (tilted left) and seat.
    draw.polygon([(cx - 78, base_y - 118), (cx - 58, base_y - 118),
                  (cx - 96, base_y - 6), (cx - 116, base_y - 6)],
                 fill=back_color, outline=(20, 20, 20))
    draw.polygon([(cx - 116, base_y - 14), (cx + 66, base_y - 14),
                  (cx + 66, base_y + 6), (cx - 116, base_y + 6)],
                 fill=seat_color, outline=(20, 20, 20))
    # Legs.
    draw.line([(cx - 100, base_y + 4), (cx - 112, base_y + 32)],
              fill=(20, 20, 20), width=7)
    draw.line([(cx + 50, base_y + 4), (cx + 62, base_y + 32)],
              fill=(20, 20, 20), width=7)
    # Backrest stripes.
    draw.line([(cx - 70, base_y - 108), (cx - 104, base_y - 16)],
              fill=(255, 255, 255), width=5)


def draw():
    img = Image.new("RGB", (W, H), (30, 10, 60))
    d = ImageDraw.Draw(img)

    # --- Sky: violet -> magenta -> orange sunset, y 0..500.
    vgrad(d, 0, 500, (26, 8, 54), (255, 178, 92))
    # Extra magenta band for a richer sunset.
    for y in range(120, 300):
        t = (y - 120) / 180
        d.line([(0, y), (W, y)], fill=lerp((90, 16, 80), (224, 84, 60), t))

    # Sun with a soft glow, upper right.
    for r, col in ((150, (255, 200, 120)), (120, (255, 220, 150)),
                   (95, (255, 242, 176))):
        d.ellipse([820 - r, 300 - r, 820 + r, 300 + r], fill=col)

    # Birds.
    for bx, by in ((180, 180), (240, 150), (300, 195)):
        d.line([(bx - 12, by), (bx, by - 8), (bx + 12, by)],
               fill=(20, 8, 40), width=4)

    # --- Skyline silhouettes with neon windows, horizon ~500.
    rng = random.Random(11)
    x = -10
    while x < W:
        bw = rng.randint(46, 96)
        bh = rng.randint(48, 130)
        d.rectangle([x, 500 - bh, x + bw, 500], fill=(34, 16, 51))
        for _ in range(bh // 22):
            wx = x + rng.randint(6, max(7, bw - 10))
            wy = 500 - bh + rng.randint(8, max(9, bh - 12))
            wc = rng.choice([(255, 94, 168), (77, 227, 255), (255, 224, 102)])
            d.rectangle([wx, wy, wx + 6, wy + 8], fill=wc)
        x += bw + rng.randint(2, 14)

    # --- Ocean, y 500..600, with the sun's reflection column.
    vgrad(d, 500, 600, (38, 24, 96), (64, 38, 128))
    for i, y in enumerate(range(512, 596, 14)):
        wdt = 130 - i * 6
        d.line([(820 - wdt // 2, y), (820 + wdt // 2, y)],
               fill=(255, 210, 122), width=4)

    # --- Sand, y 600..1024.
    vgrad(d, 600, H, (242, 201, 138), (222, 164, 96))
    rng = random.Random(7)
    for _ in range(130):
        sx, sy = rng.randint(10, W - 10), rng.randint(620, H - 10)
        r = rng.randint(2, 4)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(205, 150, 88))

    # --- Palms framing the scene.
    palm(d, 70, 640, 260, 70, (28, 11, 46))
    palm(d, 960, 650, 230, -60, (28, 11, 46))

    # --- Beach umbrella over the two chairs.
    ux, uy, ur = 520, 630, 200
    for i in range(6):
        a0 = 180 + i * 30
        col = (255, 94, 138) if i % 2 == 0 else (255, 255, 255)
        d.pieslice([ux - ur, uy - ur, ux + ur, uy + ur], a0, a0 + 30, fill=col)
    d.ellipse([ux - 10, uy - ur - 8, ux + 10, uy - ur + 12], fill=(255, 94, 138))
    d.line([(ux, uy - ur + 6), (ux, uy + 210)], fill=(60, 30, 20), width=9)

    # --- The fan in his beach chair (left), playing a handheld.
    chair(d, 380, 872, (25, 184, 166), (25, 184, 166))
    # Legs stretched forward, shorts, feet.
    d.rounded_rectangle([392, 838, 500, 868], radius=12, fill=(47, 111, 178),
                        outline=(20, 20, 20), width=3)
    d.rounded_rectangle([500, 844, 556, 862], radius=8, fill=(242, 196, 155),
                        outline=(20, 20, 20), width=3)
    d.ellipse([548, 838, 576, 866], fill=(255, 255, 255), outline=(20, 20, 20), width=3)
    # Torso: loud pink Hawaiian shirt with white dots.
    d.rounded_rectangle([348, 712, 428, 848], radius=18, fill=(255, 94, 138),
                        outline=(20, 20, 20), width=4)
    for dx, dy in ((368, 740), (402, 760), (372, 800), (408, 820), (388, 780)):
        d.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(255, 255, 255))
    # Arms reaching to the handheld.
    d.line([(360, 740), (388, 800)], fill=(242, 196, 155), width=15)
    d.line([(416, 740), (404, 800)], fill=(242, 196, 155), width=15)
    # Handheld console with a tiny sunset-and-car screen.
    d.rounded_rectangle([352, 782, 436, 824], radius=10, fill=(26, 26, 34),
                        outline=(10, 10, 10), width=3)
    d.rectangle([368, 790, 420, 816], fill=(255, 140, 80))
    d.rectangle([368, 802, 420, 816], fill=(40, 40, 90))
    d.polygon([(382, 812), (382, 804), (396, 804), (402, 808), (408, 808),
               (408, 812)], fill=(10, 10, 10))
    d.ellipse([358, 800, 364, 806], fill=(255, 60, 60))
    d.ellipse([424, 800, 430, 806], fill=(77, 227, 255))
    # Head: sunglasses, grin, hair.
    d.ellipse([356, 632, 424, 700], fill=(242, 196, 155), outline=(20, 20, 20), width=4)
    d.pieslice([356, 632, 424, 682], 180, 360, fill=(43, 26, 18))
    d.rounded_rectangle([360, 656, 420, 674], radius=7, fill=(10, 10, 10))
    d.line([(372, 660), (384, 670)], fill=(255, 255, 255), width=3)
    d.arc([372, 676, 408, 696], 20, 160, fill=(20, 20, 20), width=4)

    # --- The make.fun ghost in its own chair (right), holding its coin.
    chair(d, 668, 872, (230, 0, 126), (230, 0, 126))
    glayer, (gx0, gy0, gx1, gy1) = ghost_layer(668, 648, scale=1.0)
    img.paste(glayer, (0, 0), glayer)
    d = ImageDraw.Draw(img)
    # Little round hand + the magenta star coin.
    d.ellipse([724, 792, 756, 824], fill=(255, 255, 255), outline=(10, 10, 10), width=5)
    coin(d, 748, 782, 30)

    # --- Phone on the sand: the boss is calling.
    d.rounded_rectangle([836, 712, 880, 766], radius=8, fill=(20, 20, 26),
                        outline=(10, 10, 10), width=3)
    d.rectangle([842, 720, 874, 758], fill=(191, 232, 255))
    d.ellipse([864, 724, 872, 732], fill=(230, 0, 60))

    # --- Captions, big white letters with a black outline.
    f_top = font(62)
    f_bot = font(46)
    text_center(d, W // 2, 34, "WAITED 13 YEARS", f_top, (255, 255, 255),
                stroke=9)
    text_center(d, W // 2, 108, "FOR GTA 6", f_top, (255, 255, 255), stroke=9)
    text_center(d, W // 2, 892, "CALLED IN SICK TODAY.", f_bot,
                (255, 255, 255), stroke=7)
    text_center(d, W // 2, 946, "MY AGENT EARNS ON MAKE.FUN", f_bot,
                (255, 255, 255), stroke=7)

    img.save(OUT, "PNG")
    print(f"wrote {OUT} {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    draw()
