"""ELSC Game - Noise Tornado concept (6-frame spin loop, 32 x 32 px = 2 x 2 tiles).

NES-style layering: the whirlwind is one 3-color sprite and the flying debris
(arms, legs, books) is a second 3-color sprite drawn on top, the way NES games
stacked sprites to get more colors.
"""
import math
from PIL import Image

S, FRAMES = 32, 6
CLOUD = {"W": "FCFCFC", "G": "BCBCBC", "K": "000000"}     # white body, gray bands, black speed streaks
DEBRIS = {"S": "F0D0B0", "R": "F83800", "B": "0058F8"}    # skin, red (sleeves, books), blue (jeans, books)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def cx_at(y, f):
    """Center of the funnel at height y: the tip sways as it spins."""
    return 15.5 + 2.2 * math.sin(2 * math.pi * f / FRAMES + y / 7.0) * (y / 31.0)


def halfw(y, f=0):
    """Width of the funnel, with a jagged, wobbling outline that changes every frame."""
    jag = 1.3 * math.sin(y * 1.7 + f * 2.1) + 0.8 * math.sin(y * 3.1 - f * 1.3)
    return max(1.5, 12.5 - (y - 3) * 0.40 + jag)


def cloud_layer(f):
    g = [["" for _ in range(S)] for _ in range(S)]
    for y in range(1, 28):
        cx, hw = cx_at(y, f), halfw(y, f)
        if y < 4:                                   # lumpy top rim
            hw -= [4, 1.5, 0][y - 1]
        for x in range(S):
            t = (x - cx) / hw
            if abs(t) > 1:
                continue
            v = y * 0.9 + t * 5 - f * 1.6           # slanted bands that slide as it spins
            band = math.floor(v / 2.4) % 3
            c = "G" if band == 2 else "W"
            if t > 0.8:
                c = "G"                             # shaded right edge (light from the top-left)
            if band == 2 and abs(t) > 0.55 and (y + f) % 3 == 0:
                c = "K"                             # speed streaks at the edges
            g[y][x] = c
        # swoosh lines just outside the funnel on some rows
        if (y + 2 * f) % 5 == 0:
            for side in (-1, 1):
                for k in range(2, 4 + (y % 2)):
                    x = int(round(cx + side * (hw + k)))
                    if 0 <= x < S and g[y][x] == "":
                        g[y][x] = "K"
    # dust puff where the tip touches the floor
    tipx = cx_at(27, f)
    for y in range(27, 32):
        w = [3, 5, 6, 5, 3][y - 27]
        for x in range(int(tipx - w), int(tipx + w) + 1):
            if 0 <= x < S:
                g[y][x] = "G" if (x + y + f) % 3 else "W"
    # the odd flying sheet of paper (white, in the cloud layer)
    for k, (yy, ph) in enumerate([(9, 0.5), (21, 3.6)]):
        a = ph + 2 * math.pi * f / FRAMES
        x0 = int(round(cx_at(yy, f) + math.cos(a) * (halfw(yy) + 4)))
        if math.sin(a) > -0.3:
            for dx, dy in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1)]:
                if 0 <= x0 + dx < S and 0 <= yy + dy < S:
                    g[yy + dy][x0 + dx] = "W" if dy == 0 else "G"
    return g


# little debris shapes, drawn pointing right (mirrored when on the left side)
ARM = ["RRRR.S.", "RRRRSSS", "RRRRSS.", ".....S."]   # sleeve + open hand
LEG = ["BBBBB..", "BBBBBRR", "BBBBBRR"]                # jeans + sneaker
BOOK_R = ["RRRRR", "RSSSR", "RSSSR", "RRRRR"]          # red book, pages showing
BOOK_B = ["BBBB", "BSSB", "BBBB"]                       # blue book


def debris_layer(f):
    g = [["" for _ in range(S)] for _ in range(S)]
    items = [(ARM, 7, 0.2), (BOOK_R, 4, 2.3), (LEG, 13, 4.1), (BOOK_B, 11, 1.2), (ARM, 18, 3.0), (LEG, 22, 5.3)]
    for shape, y0, ph in items:
        a = ph + 2 * math.pi * f / FRAMES
        c, s = math.cos(a), math.sin(a)
        if s < -0.35 and abs(c) < 0.8:
            continue                              # behind the funnel: hidden
        side = 1 if c >= 0 else -1
        rows = shape if side > 0 else [r[::-1] for r in shape]
        w = len(rows[0])
        # at the sides things stick OUT of the funnel; in front they tumble across it
        edge = cx_at(y0, f) + side * (halfw(y0, f) * abs(c) - 2 + 3 * abs(c))
        x0 = int(round(edge if side > 0 else edge - w + 1))
        for dy, r in enumerate(rows):
            for dx, ch in enumerate(r):
                x, y = x0 + dx, y0 + dy
                if ch != "." and 0 <= x < S and 0 <= y < S:
                    g[y][x] = ch
    return g


def to_img(grid, pal):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = im.load()
    for y in range(S):
        for x in range(S):
            if grid[y][x]:
                px[x, y] = rgb(pal[grid[y][x]])
    return im


frames = []
for f in range(FRAMES):
    im = to_img(cloud_layer(f), CLOUD)
    im.alpha_composite(to_img(debris_layer(f), DEBRIS))
    frames.append(im)

# frame strip (the sprite sheet for the tornado)
strip = Image.new("RGBA", (S * FRAMES, S), (0, 0, 0, 0))
for i, im in enumerate(frames):
    strip.paste(im, (i * S, 0), im)
strip.save("tornado_sheet.png")

# preview: animated on the real carpet next to a table and chair, 5x zoom
furn = Image.open("elsc_furniture_sheet.png")
import json
atlas = json.load(open("elsc_furniture_sheet.json"))["sprites"]
def spr(n):
    r = atlas[n]
    return furn.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
bg = Image.new("RGBA", (96, 64))
for ty in range(4):
    for tx in range(6):
        bg.alpha_composite(spr("carpet_a" if (tx + ty) % 2 == 0 else "carpet_b"), (tx * 16, ty * 16))
bg.alpha_composite(spr("chair_red_W"), (56, 16))
bg.alpha_composite(spr("chair_green_N"), (72, 0))
bg.alpha_composite(spr("table_square"), (72, 16))
gif = []
for i in range(FRAMES * 3):
    fr = bg.copy()
    x = 8 + int(8 * math.sin(i / (FRAMES * 3) * 2 * math.pi))
    fr.alpha_composite(frames[i % FRAMES], (x, 18))
    gif.append(fr.resize((96 * 5, 64 * 5), Image.NEAREST).convert("RGB"))
gif[0].save("tornado_preview.gif", save_all=True, append_images=gif[1:], duration=90, loop=0)
big = Image.new("RGBA", (S * FRAMES * 6 + 10 * (FRAMES - 1), S * 6), (90, 90, 90, 255))
for i, im in enumerate(frames):
    big.alpha_composite(im.resize((S * 6, S * 6), Image.NEAREST), (i * (S * 6 + 10), 0))
big.save("tornado_frames_6x.png")

# NES rule check per layer
for f in range(FRAMES):
    for name, layer, pal in (("cloud", cloud_layer(f), CLOUD), ("debris", debris_layer(f), DEBRIS)):
        used = {c for row in layer for c in row if c}
        assert len(used) <= 3, (name, f, used)
print("ok: 6 frames, each layer <= 3 NES colors")
