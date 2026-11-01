#!/usr/bin/env python3
"""Virtual-Dice-Roller wordmark banner: a wide low horizon across the dry lake bed at
hard noon, cracked foreground, rippled salt, a tumbleweed against an agave rosette,
flat mesa bands at the far edge, and at the lower left a trail register open on a camp
table carrying the name in Are You Serious in dark ink, with a pencil and dice beside it."""
import sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
random.seed(23)
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
W, H = 1600, 560
img = Image.new("RGB", (W, H), (247, 243, 232)); d = ImageDraw.Draw(img, "RGBA")
for mx, mw, my, bands in ((820, 360, 96, [(168, 74, 52), (201, 138, 122), (222, 196, 168)]),
                          (1210, 330, 82, [(160, 61, 42), (196, 122, 100), (216, 186, 158)])):
    yy = my
    for col in bands:
        d.polygon([(mx + (yy - my) // 6, yy), (mx + mw - (yy - my) // 6, yy), (mx + mw - (yy - my) // 6 - 4, yy + 26), (mx + (yy - my) // 6 + 4, yy + 26)], fill=col); yy += 26
    d.polygon([(mx + 16, yy), (mx + mw - 16, yy), (mx + mw - 26, 236), (mx + 26, 236)], fill=(196, 160, 138))
d.rectangle([0, 232, W, H], fill=(238, 230, 210))
for i, yy in enumerate(range(258, 360, 20)):
    pts = [(x, yy + 6 * math.sin(x / 120 + i * 1.7)) for x in range(-20, W + 20, 24)]
    d.line(pts, fill=(255, 253, 244), width=5); d.line([(x, y + 8) for (x, y) in pts], fill=(201, 138, 122), width=2)
# agave and tumbleweed in the midground right
ax, ay = 1330, 372
for a in range(0, 360, 30):
    r = math.radians(a); d.polygon([(ax - 5, ay), (ax + 5, ay), (ax + 52 * math.cos(r), ay + 22 * math.sin(r))], fill=(77, 122, 82))
random.seed(31); twx, twy, twr = 1248, 356, 40
for i in range(34):
    a = random.uniform(0, 6.28); x1, y1 = twx + random.uniform(.3, 1) * twr * math.cos(a), twy + random.uniform(.3, 1) * twr * .78 * math.sin(a)
    a2 = a + random.uniform(.6, 1.6); d.line([(x1, y1), (twx + twr * math.cos(a2), twy + twr * .78 * math.sin(a2))], fill=(146, 118, 82), width=3)
d.ellipse([twx - twr, twy - twr * .78, twx + twr, twy + twr * .78], outline=(128, 102, 70), width=3)
# cracked foreground strip
random.seed(11)
for row, yy in enumerate(range(420, 580, 74)):
    for xx in range(-40, 1700, 150):
        cx, cy = xx + random.uniform(-20, 20), yy + random.uniform(-10, 10)
        pts = []
        for a in range(0, 360, 60):
            r = math.radians(a + random.uniform(-14, 14)); rad = random.uniform(64, 84)
            pts.append((cx + rad * math.cos(r), cy + rad * .55 * math.sin(r)))
        d.polygon(pts, fill=random.choice([(240, 232, 212), (236, 226, 202)]), outline=(58, 36, 48), width=6)
# camp table and the open trail register, lower left
d.polygon([(40, 470), (860, 470), (920, 560), (0, 560)], fill=(122, 88, 58))
d.polygon([(70, 386), (400, 372), (400, 516), (70, 530)], fill=(243, 234, 210), outline=(160, 61, 42), width=3)
d.polygon([(400, 372), (730, 386), (730, 530), (400, 516)], fill=(248, 241, 222), outline=(160, 61, 42), width=3)
for i in range(5):
    d.line([(92, 418 + i * 20), (378, 408 + i * 20)], fill=(190, 178, 152), width=2)
    d.line([(422, 408 + i * 20), (708, 418 + i * 20)], fill=(190, 178, 152), width=2)
size = 44 if v == "v1" else 48
f = ImageFont.truetype("fonts/AreYouSerious.ttf", size)
d.text((400, 448), "Virtual-Dice-Roller", font=f, anchor="mm", fill=(43, 33, 24))
d.polygon([(756, 512), (830, 498), (834, 508), (760, 524)], fill=(217, 164, 65))  # pencil
d.polygon([(830, 498), (846, 496), (834, 508)], fill=(43, 33, 24))
for (dx, dy, pips) in ((762, 428, [(0, 0)]), (802, 454, [(-12, -12), (12, 12)])):
    d.rounded_rectangle([dx, dy, dx + 44, dy + 44], 9, fill=(250, 248, 240), outline=(43, 33, 24), width=3)
    for (ox, oy) in pips: d.ellipse([dx + 22 + ox - 5, dy + 22 + oy - 5, dx + 22 + ox + 5, dy + 22 + oy + 5], fill=(160, 61, 42))
rng = np.random.default_rng(4); a = np.asarray(img).astype(np.int16); n = rng.normal(0, 3, a.shape[:2])[..., None]
img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
out = "banner.png" if v == "ship" else f"scratch/banner-{v}.png"
img.save(out); print(out)
