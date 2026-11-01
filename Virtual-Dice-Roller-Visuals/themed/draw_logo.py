#!/usr/bin/env python3
"""Virtual-Dice-Roller logo: top down, one cracked playa polygon plate with curled edges,
a single sky white die face up inside it, pips as pits filled with red rock dust, an agave
green rim fleck on one side only, and the name in Are You Serious beneath."""
import sys, math, random
from PIL import Image, ImageDraw, ImageFont
random.seed(5)
v = sys.argv[1] if len(sys.argv) > 1 else "ship"
S = 1000
img = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
thick = 15 if v == "v1" else 22
# the cracked plate, an irregular polygon
cx, cy, R = 500, 400, 300
pts = []
for a in range(0, 360, 45):
    r = math.radians(a + random.uniform(-9, 9)); rad = R * random.uniform(.88, 1.02)
    pts.append((cx + rad * math.cos(r), cy + rad * .86 * math.sin(r)))
d.polygon(pts, fill=(238, 230, 210, 255), outline=(58, 36, 48, 255), width=thick)
# curling fissure lines from the rim toward the die
for (px, py) in pts[::2]:
    mx, my = cx + (px - cx) * .55, cy + (py - cy) * .55
    d.line([(px, py), (mx + random.uniform(-20, 20), my)], fill=(58, 36, 48, 255), width=max(6, thick - 8))
# curled rim highlight on the top edge
d.arc([cx - R + 26, cy - R * .86 + 20, cx + R - 26, cy + R * .86 - 20], 190, 330, fill=(255, 254, 248, 255), width=10)
# agave green rim fleck on the right side only: a small rosette at the fissure
ax, ay = cx + R * .97, cy + 30
for a in range(0, 360, 36):
    r = math.radians(a); d.polygon([(ax - 6, ay), (ax + 6, ay), (ax + 52 * math.cos(r), ay + 24 * math.sin(r))], fill=(77, 122, 82, 255))
# the die, face up, sky white, pips as dust filled pits (five)
dx, dy, ds = cx - 105, cy - 105, 210
d.rounded_rectangle([dx, dy, dx + ds, dy + ds], 34, fill=(250, 248, 240, 255), outline=(43, 33, 24, 255), width=10)
for (px, py) in ((dx + 52, dy + 52), (dx + ds - 52, dy + 52), (dx + ds // 2, dy + ds // 2), (dx + 52, dy + ds - 52), (dx + ds - 52, dy + ds - 52)):
    d.ellipse([px - 21, py - 21, px + 21, py + 21], fill=(160, 61, 42, 255), outline=(120, 44, 30, 255), width=3)
f = ImageFont.truetype("fonts/AreYouSerious.ttf", 92)
d.text((500, 800), "Virtual-Dice-Roller", font=f, anchor="mm", fill=(201, 110, 96, 255))
out = "logo.png" if v == "ship" else f"scratch/logo-{v}.png"
img.save(out)
img.resize((64, 64)).save("scratch/logo64-ship.png" if v == "ship" else f"scratch/logo64-{v}.png")
print(out)
