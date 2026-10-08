"""ELSC Game - Noise Tornado as a cartoon FIGHT CLOUD, one size per stage (6 frames each).

  Stage 1: 32 x 32 px (2 x 2 tiles)   Stage 2: 48 x 48 px (3 x 3)   Stage 3: 64 x 64 px (4 x 4)

A bouncing ball of dust with fists, feet, books and faces popping in and out. Bigger stages are
drawn natively (same pixel size as everything else) with more puffs, faces, fists and books.
NES-style layering: cloud sprite (3 colors) + debris sprite (3 colors) on top.
"""
import sys
import json
import math
import random
from PIL import Image

FRAMES = 6
SIZES = {1: 32, 2: 48, 3: 64}
S, K = 32, 1.0          # set per stage in build()
CLOUD = {"W": "FCFCFC", "G": "BCBCBC", "K": "000000"}     # dust white, shade gray, black eyes/impact marks
DEBRIS = {"S": "F0D0B0", "R": "F83800", "B": "0058F8"}    # skin, red (sleeves, shoes, books), blue (jeans, books)


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def puffs(f):
    """The cloud is a cluster of round puffs that shift and bounce every frame."""
    r = random.Random(f * 7 + 3)
    bounce = round([0, -1, -2, -1, 0, 1][f] * K)
    cx, cy = S // 2, S // 2 + bounce
    out = [(cx, cy, 8.5 * K)]
    n = {1.0: 8, 1.5: 10, 2.0: 12}[K]
    for i in range(n):
        a = 2 * math.pi * i / n + f * 0.45 + r.uniform(-0.25, 0.25)
        rr = r.uniform(4.2, 5.8) * K
        d = r.uniform(7.0, 8.6) * K
        out.append((cx + math.cos(a) * d, cy + math.sin(a) * d * 0.9, rr))
    return out


def cloud_layer(f):
    P = puffs(f)
    g = [["" for _ in range(S)] for _ in range(S)]
    for y in range(S):
        for x in range(S):
            inside = [(px, py, pr) for (px, py, pr) in P if (x - px) ** 2 + (y - py) ** 2 <= pr ** 2]
            if not inside:
                continue
            c = "W"
            # shade the lower-right rim of each outer puff (light from the top-left)
            for (px, py, pr) in inside:
                d = math.hypot(x - px, y - py)
                if d > pr - 1.6 and (x - px) + (y - py) > pr * 0.5:
                    only_this = all((x - qx) ** 2 + (y - qy) ** 2 > (qr - 0.8) ** 2
                                    for (qx, qy, qr) in P if (qx, qy, qr) != (px, py, pr))
                    if only_this:
                        c = "G"
            g[y][x] = c
    r = random.Random(100 + f)
    # dust swirls inside
    lo, hi = round(6 * K), S - 1 - round(6 * K)
    for _ in range(round(10 * K * K)):
        x, y = r.randint(lo, hi), r.randint(lo, hi)
        if g[y][x] == "W":
            g[y][x] = "G"
            if x + 1 < S and g[y][x + 1] == "W":
                g[y][x + 1] = "G"
    # faces peeking out of the dust: angry eyes, some with a yelling mouth
    FACES = [
        ["K...K", ".K.K.", ".....", "KK.KK"],                   # angry brows + eyes
        ["KK.KK", ".....", ".KKK.", ".KKK."],                   # wide eyes + yelling mouth
        ["K...K", ".K.K.", "KK.KK", ".....", ".KKK."],          # angry + shouting
        ["K.K.K.K", ".K...K.", "K.K.K.K"],                      # dizzy X eyes
    ]
    extra = round((K - 1) * 4)                       # stage 2: +2 faces, stage 3: +4
    for _ in range(r.choice([1, 2, 2]) + extra):
        face = r.choice(FACES)
        fh, fw = len(face), len(face[0])
        for _try in range(200):
            x, y = r.randint(round(5 * K), S - 6 - fw), r.randint(round(6 * K), S - 7 - fh)
            if all(g[y + dy][x + dx] in ("W", "G") for dy in range(-1, fh + 1) for dx in range(-1, fw + 1)):
                for dy in range(-1, fh + 1):
                    for dx in range(-1, fw + 1):
                        g[y + dy][x + dx] = "W"           # clear the dust behind the face
                for dy, row in enumerate(face):
                    for dx, ch in enumerate(row):
                        if ch == "K":
                            g[y + dy][x + dx] = "K"
                break
    # impact marks flying off the cloud
    marks = [["K.K", ".K.", "K.K"], [".K.", "KKK", ".K."], ["K..", ".K.", "..K"]]
    for _ in range(3 + extra):
        for _try in range(30):
            a = r.uniform(0, 2 * math.pi)
            x = int(S // 2 + math.cos(a) * 14 * K)
            y = int(S // 2 + math.sin(a) * 13 * K)
            m = r.choice(marks)
            if 0 <= x < S - 3 and 0 <= y < S - 3 and all(g[y + dy][x + dx] == "" for dy in range(3) for dx in range(3)):
                for dy, row in enumerate(m):
                    for dx, ch in enumerate(row):
                        if ch == "K":
                            g[y + dy][x + dx] = "K"
                break
    return g


# debris shapes, pointing RIGHT (rotated/mirrored to point out of the cloud)
FIST = ["RRRRR.SS", "RRRRRSSSS", "RRRRR.SSS"]
FOOT = ["BBBBBB...", "BBBBBBRRR", "BBBBBBRRR"]
BOOK_R = ["RRRRR", "RSSSR", "RSSSR", "RRRRR"]
BOOK_B = ["BBBB", "BSSB", "BSSB", "BBBB"]
PAGE = ["SSS", "S.S", "SSS"]


def orient(shape, direction):
    w = max(len(r) for r in shape)
    rows = [r.ljust(w, ".") for r in shape]
    if direction == "R":
        return rows
    if direction == "L":
        return [r[::-1] for r in rows]
    cols = ["".join(rows[y][x] for y in range(len(rows))) for x in range(w)]   # transpose: points down
    return cols if direction == "D" else cols[::-1]


def debris_layer(f):
    P = puffs(f)
    cx, cy = P[0][0], P[0][1]
    g = [["" for _ in range(S)] for _ in range(S)]
    r = random.Random(500 + f * 13)
    kinds = [FIST, FIST, FOOT, FOOT, BOOK_R, BOOK_B, PAGE]
    if K > 1:
        kinds = kinds * 2
    r.shuffle(kinds)
    count = r.choice([3, 4, 4]) + round((K - 1) * 6)   # stage 2: +3 items, stage 3: +6
    base = r.uniform(0, 2 * math.pi)
    for i, shape in enumerate(kinds[:count]):
        a = base + 2 * math.pi * i / count + r.uniform(-0.3, 0.3)
        dx, dy = math.cos(a), math.sin(a)
        direction = ("R" if dx > 0 else "L") if abs(dx) > abs(dy) else ("D" if dy > 0 else "U")
        rows = orient(shape, direction)
        h, w = len(rows), len(rows[0])
        # anchor so the item pokes OUT of the cloud's edge
        ex, ey = cx + dx * 10 * K, cy + dy * 9 * K
        x0 = int(round(ex - (0 if direction == "R" else w - 1 if direction == "L" else w // 2)))
        y0 = int(round(ey - (0 if direction == "D" else h - 1 if direction == "U" else h // 2)))
        for yy, row in enumerate(rows):
            for xx, ch in enumerate(row):
                X, Y = x0 + xx, y0 + yy
                if ch != "." and 0 <= X < S and 0 <= Y < S:
                    g[Y][X] = ch
    return g


def to_img(grid, pal):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    px = im.load()
    for y in range(S):
        for x in range(S):
            if grid[y][x]:
                px[x, y] = rgb(pal[grid[y][x]])
    return im


def build(stage):
    global S, K
    S, K = SIZES[stage], SIZES[stage] / 32
    frames = []
    for f in range(FRAMES):
        cl, db = cloud_layer(f), debris_layer(f)
        for name, layer, pal in (("cloud", cl, CLOUD), ("debris", db, DEBRIS)):
            used = {c for row in layer for c in row if c}
            assert len(used) <= 3, (name, f, used)
        im = to_img(cl, CLOUD)
        im.alpha_composite(to_img(db, DEBRIS))
        frames.append(im)
    strip = Image.new("RGBA", (S * FRAMES, S), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        strip.paste(im, (i * S, 0), im)
    return frames, strip


ALL = {}
for stage in (1, 2, 3):
    frames, strip = build(stage)
    ALL[stage] = frames
    strip.save(f"noise_tornado_stage{stage}.png")
    json.dump({"stage": stage, "sheet": f"noise_tornado_stage{stage}.png", "frame_size": [S, S],
               "tiles": [S // 16, S // 16], "frames": FRAMES, "fps": 10, "loop": True,
               "frames_xywh": [{"x": i * S, "y": 0, "w": S, "h": S} for i in range(FRAMES)],
               "hitbox_suggested": [round(S * 0.62), round(S * 0.62)],
               "note": "Play frames 0-5 in a loop. Use a hitbox smaller than the drawing, centered."},
              open(f"noise_tornado_stage{stage}.json", "w"), indent=2)


# frames up close, all three sizes
Z, GAP = 4, 12
Wb = max(SIZES.values()) * Z * FRAMES + GAP * (FRAMES + 1)
Hb = sum(v * Z + GAP for v in SIZES.values()) + GAP
big = Image.new("RGBA", (Wb, Hb), (90, 90, 90, 255))
y = GAP
for stage, frames in ALL.items():
    sz = SIZES[stage]
    for i, im in enumerate(frames):
        big.alpha_composite(im.resize((sz * Z, sz * Z), Image.NEAREST), (GAP + i * (64 * Z + GAP), y))
    y += sz * Z + GAP
big.save("noise_tornado_sizes_frames.png")

# all three on the real stage, side by side, same scale as the game
stage_img = Image.open("preview_stage_1x.png").convert("RGBA")
import os
boy = None                                     # the student is only shown if the student sheet exists yet
if os.path.exists("students_sheet.png"):
    students = Image.open("students_sheet.png").convert("RGBA")
    q = json.load(open("students_sheet.json"))["sprites"]["boy_down_stand"]
    boy = students.crop((q["x"], q["y"], q["x"] + 16, q["y"] + 16))
view = (48, 128, 48 + 256, 128 + 176)          # one 16 x 11 screen around T1/T2/T4/T6
panels = []
for i in range(12):
    row = []
    for stage in (1, 2, 3):
        fr = stage_img.crop(view)
        sz = SIZES[stage]
        fr.alpha_composite(ALL[stage][i % FRAMES], (150 - sz // 2, 100 - sz // 2))
        if boy is not None:
            fr.alpha_composite(boy, (72, 92))          # the student on open floor, same spot each time
        row.append(fr)
    panel = Image.new("RGBA", (256 * 3 + 16, 176), (56, 56, 56, 255))
    for k, fr in enumerate(row):
        panel.alpha_composite(fr, (k * (256 + 8), 0))
    panels.append(panel.resize((panel.width * 2, panel.height * 2), Image.NEAREST).convert("RGB"))
panels[0].save("noise_tornado_sizes_preview.gif", save_all=True, append_images=panels[1:], duration=100, loop=0)
panels[0].save("noise_tornado_sizes_still.png")
print("ok: stages 1-3 drawn (32, 48, 64 px), each layer <= 3 NES colors")
