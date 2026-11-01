#!/usr/bin/env python3
"""Virtual-Dice-Roller introduction banner: the playa of the ancient lake, wordless.
Ground level over cracked mud polygons with curled rims and shadowed fissures, a resting
tumbleweed, rippled salt running to scattered agave rosettes, mesa strata at the horizon
under a sky white sky, heat shimmer over the far playa. No text of any kind."""
import sys, random, math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
random.seed(41)
W, H = 1600, 900
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
SKY = (247, 243, 232); CRUST = (238, 230, 210); RED = (160, 61, 42); ROSE = (201, 138, 122)
PLUM = (58, 36, 48); AGAVE = (77, 122, 82); INK = (43, 33, 24)
img = Image.new("RGB", (W, H), SKY); d = ImageDraw.Draw(img, "RGBA")
# sky white sky, bleached gradient
for y in range(0, 430):
    t = y / 430; d.line([(0, y), (W, y)], fill=(int(250 - 8 * t), int(246 - 10 * t), int(236 - 12 * t)))
# mesas: flat strata bands, level tops
for mx, mw, my, bands in ((60, 430, 300, [(168, 74, 52), (201, 138, 122), (222, 196, 168)]),
                          (560, 520, 318, [(160, 61, 42), (196, 122, 100), (216, 186, 158)]),
                          (1150, 400, 292, [(172, 82, 58), (205, 146, 128), (226, 202, 172)])):
    yy = my
    for i, col in enumerate(bands):
        inset = (yy - my) // 6
        d.polygon([(mx + inset, yy), (mx + mw - inset, yy), (mx + mw - inset - 6, yy + 34), (mx + inset + 6, yy + 34)], fill=col); yy += 34
    d.polygon([(mx + 22, yy), (mx + mw - 22, yy), (mx + mw - 34, 486), (mx + 34, 486)], fill=(196, 160, 138))
    d.polygon([(mx + 34, 470), (mx + mw - 34, 470), (mx + mw - 10, 492), (mx + 10, 492)], fill=(120, 84, 70, 90))
# heat shimmer over the far playa (soft wavy light band)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
for i in range(7):
    yy = 448 + i * 9
    pts = [(x, yy + 4 * math.sin(x / 90 + i)) for x in range(0, W + 40, 40)]
    ld.line(pts, fill=(255, 252, 240, 46), width=5)
img = Image.alpha_composite(img.convert("RGBA"), layer.filter(ImageFilter.GaussianBlur(4))).convert("RGB"); d = ImageDraw.Draw(img, "RGBA")
# rippled salt and sand, long even waves
for i, yy in enumerate(range(486, 660, 22)):
    pts = [(x, yy + 7 * math.sin(x / 120 + i * 1.7)) for x in range(-20, W + 20, 24)]
    d.line(pts, fill=(255, 253, 244), width=6)
    pts2 = [(x, yy + 9 + 7 * math.sin(x / 120 + i * 1.7)) for x in range(-20, W + 20, 24)]
    d.line(pts2, fill=ROSE, width=3)
# agave rosettes, stiff green stars close to the ground
def agave(cx, cy, s):
    for a in range(0, 360, 30):
        r = math.radians(a + random.uniform(-6, 6)); L = s * random.uniform(.8, 1.15)
        x2, y2 = cx + L * math.cos(r), cy + L * .42 * math.sin(r)
        d.polygon([(cx - 5, cy), (cx + 5, cy), (x2, y2)], fill=AGAVE)
    d.ellipse([cx - 6, cy - 4, cx + 6, cy + 4], fill=(58, 98, 64))
for ax, ay, s in ((240, 560, 46), (1330, 590, 54), (880, 530, 34), (1520, 520, 30)):
    agave(ax, ay, s)
# cracked polygons fill the lower half
d.rectangle([0, 648, W, H], fill=(186, 162, 132))
random.seed(7)
cells = []
for row, yy in enumerate(range(640, 980, 108)):
    for col, xx in enumerate(range(-60, 1700, 168)):
        jx, jy = xx + random.uniform(-30, 30), yy + random.uniform(-18, 18)
        cells.append((jx, jy))
for (cx, cy) in cells:
    pts = []
    sc = random.uniform(.78, 1.28)
    for a in range(0, 360, 60):
        r = math.radians(a + random.uniform(-16, 16)); rad = random.uniform(72, 96) * sc
        pts.append((cx + rad * math.cos(r), cy + rad * .58 * math.sin(r)))
    d.polygon(pts, fill=(random.choice([(240, 232, 212), (236, 226, 202), (243, 236, 218)])), outline=PLUM, width=7)
    # curled rim: a lit edge on the top side, shadow below
    d.arc([cx - 70, cy - 42, cx + 70, cy + 40], 180, 330, fill=(255, 254, 248), width=4)
    for gx in range(3):
        ex, ey = cx + random.uniform(-50, 50), cy + random.uniform(-22, 22)
        d.ellipse([ex, ey, ex + 4, ey + 3], fill=ROSE)  # loose grains in the fissures
# tumbleweed resting against the nearest plate edge, lattice shadow first
twx, twy, twr = (430, 742, 62) if v != "v1" else (430, 742, 40)
for i in range(26):
    a = random.uniform(0, 6.28); x2, y2 = twx + twr * .9 * math.cos(a + .3), twy + 14 + twr * .5 * math.sin(a)
    d.line([(twx, twy + 16), (x2, y2)], fill=(120, 96, 70, 110), width=3)
random.seed(19)
for i in range(46):
    a = random.uniform(0, 6.28); r1 = random.uniform(.3, 1) * twr
    x1, y1 = twx + r1 * math.cos(a), twy + r1 * .78 * math.sin(a)
    a2 = a + random.uniform(.6, 1.6); x2, y2 = twx + twr * math.cos(a2), twy + twr * .78 * math.sin(a2)
    d.line([(x1, y1), (x2, y2)], fill=(146, 118, 82), width=3)
d.ellipse([twx - twr, twy - twr * .78, twx + twr, twy + twr * .78], outline=(128, 102, 70), width=4)
rng = np.random.default_rng(3); a = np.asarray(img).astype(np.int16); n = rng.normal(0, 3, a.shape[:2])[..., None]
img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
out = "intro-banner.png" if v == "ship" else f"scratch/intro-{v}.png"
img.save(out); print(out)
