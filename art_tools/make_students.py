"""ELSC Game - student sprites (boy + girl), NES style.

16 x 16 px (one tile, Link-size). Strict NES rule: 3 colors per sprite + transparent.
  D = dark   : hair, jeans, shoes, eyes, backpack (black)
  S = skin   : face, hands, and the T-shirt under the blazer
  B = blazer : one color per character (no red or blue: those belong to the Noise Tornado)
Frames per direction: stand, walk1, walk2. Left = right mirrored (like NES hardware flipping).
"""
import json
import math
from PIL import Image

T = 16
PALS = {
    "boy":  {"D": "000000", "S": "F0D0B0", "B": "00A844"},   # green-teal blazer
    "girl": {"D": "000000", "S": "F0D0B0", "B": "F878F8"},   # lilac-pink blazer + ribbon
}

# ------------------------------------------------------------ upper bodies (rows 0-12)
BOY = {
    "down": [
        "................",
        "....D.DDD.D.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDSSSSSSDD...",
        "...DSSSSSSSSD...",
        "...SSDSSSSDSS...",
        "....SSSSSSSS....",
        ".....SSSSSS.....",
        "....BBBSSBBB....",
        "...BBBBSSBBBB...",
        "..SBBBBSSBBBBS..",
        "..SBBBBBBBBBBS..",
    ],
    "up": [
        "................",
        "....D.DDD.D.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDDDDDDDDD...",
        "...DDDDDDDDDD...",
        "...SDDDDDDDDS...",
        "....DDDDDDDD....",
        ".....SSSSSS.....",
        "....BDDDDDDB....",
        "...BBDDDDDDBB...",
        "..SBBDDDDDDBBS..",
        "..SBBBBBBBBBBS..",
    ],
    "right": [
        "................",
        ".....D.DDD......",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDDDDSSSSD...",
        "...DDDDSSSSSS...",
        "...DDDSSSSDSS...",
        "....DDSSSSSSS...",
        ".....DSSSSS.....",
        "....DDBBBBB.....",
        "...DDDBBBBBB....",
        "...DDDBBBSBB....",
        "....DDBBBBBB....",
    ],
}

GIRL = {
    "down": [
        "..........BB....",
        ".....DDDDDDB....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDSSSSSSDD...",
        "..DDSSSSSSSSDD..",
        "..DDSDSSSSDSDD..",
        "..DDSSSSSSSSDD..",
        "..DD.SSSSSS.DD..",
        "..DDBBBSSBBBDD..",
        "...BBBBSSBBBB...",
        "..SBBBBSSBBBBS..",
        "..SBBBBBBBBBBS..",
    ],
    "up": [
        "................",
        ".....DDDDDD.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDDDBBDDDD...",
        "...DDDDDDDDDD...",
        "..SDDDDDDDDDDS..",
        "...DDDDDDDDDD...",
        "....DDDDDDDD....",
        "....BBBDDBBB....",
        "...BBBBDDBBBB...",
        "..SBBBBBDBBBBS..",
        "..SBBBBBBBBBBS..",
    ],
    "right": [
        "................",
        "......DDDDD.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "..BDDDDDSSSSD...",
        ".DDDDDDSSSSSS...",
        "DDD.DDSSSSDSS...",
        "DD..DDSSSSSSS...",
        "D....DSSSSS.....",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "....BBBBBSBB....",
        ".....BBBBBBB....",
    ],
}

# ------------------------------------------------------------ legs (rows 13-15)
LEGS = {
    "front": {
        "stand": ["....DDDDDDDD....", "....DDD..DDD....", "....DDD..DDD...."],
        "walk1": ["....DDDDDDDD....", "....DDD..DDD....", "....DDD........."],
        "walk2": ["....DDDDDDDD....", "....DDD..DDD....", ".........DDD...."],
    },
    "side": {
        "stand": [".....DDDDDD.....", ".....DD..DD.....", ".....DD..DD....."],
        "walk1": [".....DDDDDD.....", "....DD....DD....", "...DD......DD..."],
        "walk2": [".....DDDDDD.....", "......DDDD......", "......DDDD......"],
    },
}


def arm_swing(rows, frame, direction):
    """Tiny arm swing while walking (front and back views): one hand lifts a pixel each step."""
    rows = [list(r) for r in rows]
    if direction in ("down", "up") and frame != "stand":
        col = 2 if frame == "walk1" else 13          # left hand on step 1, right hand on step 2
        if rows[12][col] == "S":
            rows[12][col] = "."
            rows[10][col] = "S"
    return ["".join(r) for r in rows]


def build(char, direction, frame):
    art = BOY if char == "boy" else GIRL
    base_dir = "right" if direction == "left" else direction
    top = arm_swing(art[base_dir], frame, base_dir)
    legs = LEGS["side" if base_dir == "right" else "front"][frame]
    rows = top + legs
    if direction == "left":
        rows = [r[::-1] for r in rows]
    assert len(rows) == T and all(len(r) == T for r in rows), (char, direction, frame)
    return rows


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def to_img(rows, pal):
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    px = im.load()
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != ".":
                px[x, y] = rgb(pal[c])
    return im


DIRS = ["down", "up", "left", "right"]
FRAMES = ["stand", "walk1", "walk2"]
sprites, atlas = {}, {}
sheet = Image.new("RGBA", (T * len(DIRS) * len(FRAMES), T * 2), (0, 0, 0, 0))
for row, char in enumerate(["boy", "girl"]):
    for di, d in enumerate(DIRS):
        for fi, fr in enumerate(FRAMES):
            name = f"{char}_{d}_{fr}"
            im = to_img(build(char, d, fr), PALS[char])
            cols = {c for c in "".join(build(char, d, fr)) if c != "."}
            assert len(cols) <= 3, (name, cols)
            sprites[name] = im
            x, y = (di * len(FRAMES) + fi) * T, row * T
            sheet.paste(im, (x, y), im)
            atlas[name] = {"x": x, "y": y, "w": T, "h": T}
sheet.save("students_sheet.png")
json.dump({"tile_size": T, "sheet": "students_sheet.png", "frames_per_direction": FRAMES,
           "walk_cycle": ["walk1", "walk2"], "sprites": atlas}, open("students_sheet.json", "w"), indent=2)

# ------------------------------------------------------------ previews
big = sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST)
bgp = Image.new("RGBA", big.size, (90, 90, 90, 255))
bgp.alpha_composite(big)
bgp.save("students_sheet_6x.png")

furn = Image.open("elsc_furniture_sheet.png")
fat = json.load(open("elsc_furniture_sheet.json"))["sprites"]
cloud = Image.open("noise_tornado_stage1.png")


def spr(n):
    q = fat[n]
    return furn.crop((q["x"], q["y"], q["x"] + q["w"], q["y"] + q["h"]))


W, H = 8 * T, 5 * T
bg = Image.new("RGBA", (W, H))
for ty in range(5):
    for tx in range(8):
        bg.alpha_composite(spr("carpet_a" if (tx + ty) % 2 == 0 else "carpet_b"), (tx * T, ty * T))
bg.alpha_composite(spr("chair_green_N"), (int(5.5 * T), 0))
bg.alpha_composite(spr("table_square"), (5 * T, 1 * T))
bg.alpha_composite(spr("chair_red_S"), (int(5.5 * T), 3 * T))
bg.alpha_composite(spr("chair_blue_W"), (4 * T, int(1.5 * T)))

# each student walks a little square: right, down, left, up
path = [("right", 1, 0)] * 8 + [("down", 0, 1)] * 6 + [("left", -1, 0)] * 8 + [("up", 0, -1)] * 6
frames_out = []
for i in range(len(path) * 2):
    fr = bg.copy()
    fr.alpha_composite(cloud.crop(((i % 6) * 32, 0, (i % 6) * 32 + 32, 32)), (int(5.2 * T), int(3.1 * T)))
    for k, (char, ox, oy) in enumerate([("boy", 6, 6), ("girl", 30, 20)]):
        pos = [ox, oy]
        step = (i + k * 14) % len(path)
        for j in range(step):
            pos[0] += path[j][1] * 3
            pos[1] += path[j][2] * 3
        d = path[step][0]
        walk = "walk1" if (i // 2) % 2 == 0 else "walk2"
        fr.alpha_composite(sprites[f"{char}_{d}_{walk}"], (pos[0], pos[1]))
    frames_out.append(fr.resize((W * 5, H * 5), Image.NEAREST).convert("RGB"))
frames_out[0].save("students_preview.gif", save_all=True, append_images=frames_out[1:], duration=110, loop=0)

# standing line-up on carpet at 8x
line = Image.new("RGBA", (T * 8, T), (0, 0, 0, 0))
for tx in range(8):
    line.alpha_composite(spr("carpet_a" if tx % 2 == 0 else "carpet_b"), (tx * T, 0))
for k, n in enumerate(["boy_down_stand", "boy_right_stand", "boy_up_stand", "boy_left_stand",
                       "girl_down_stand", "girl_right_stand", "girl_up_stand", "girl_left_stand"]):
    line.alpha_composite(sprites[n], (k * T, 0))
line.resize((line.width * 8, line.height * 8), Image.NEAREST).save("students_standing_8x.png")
print("ok:", len(sprites), "sprites, each <= 3 NES colors")
