"""ELSC Game - SEATED (studying) sprites for the boy and girl, NES style.

The student sits on a chair facing the table and reads an open book.
Same heads, colors and 3-color rule as make_students.py.
2 frames per side: read1 and read2 (a small head nod over the book), loop while charging.

Chair sides (which side of the table the chair is on) and what we see:
  N = chair above the table -> student faces down (front view), drawn IN FRONT of the chair
  S = chair below the table -> student faces up (back view), drawn BEHIND the chair's backrest
  W = chair left of table   -> student faces right (side view)
  E = chair right of table  -> student faces left (side view, mirrored)
"""
import json
from PIL import Image

src = open("make_students.py").read().split("DIRS = ")[0]   # reuse heads, palettes, helpers
exec(src)

HEAD_ROWS = 9   # rows 0-8 are the head in every standing sprite

BODY = {
    "boy": {
        "N": [
            "....BBBSSBBB....",
            "...BBBBSSBBBB...",
            "..BSSSSSDSSSSSB.",      # hands holding an open book (cream pages, black spine)
            "..BSSSSSDSSSSSB.",
            "...DDDDDDDDDD...",      # lap
            "...DD......DD...",
            "................",
        ],
        "S": [
            "....BBBBBBBB....",
            "...BBBBBBBBBB...",
            "..BBBBBBBBBBBB..",      # elbows out, reading
            "..BBBBBBBBBBBB..",
            "...DDDDDDDDDD...",
            "................",
            "................",
        ],
        "W": [
            "....DDBBBBB.....",      # backpack against the chair back
            "...DDDBBBBBB....",
            "...DDDBBBBSSDS..",      # arms forward holding the book
            "....DDBBBBSSDS..",
            ".....DDDDDDDDD..",      # thighs on the seat
            "...........DD...",      # lower legs down
            "...........DD...",
        ],
    },
    "girl": {
        "N": [
            "..DDBBBSSBBBDD..",      # long hair over the shoulders
            "...BBBBSSBBBB...",
            "..BSSSSSDSSSSSB.",
            "..BSSSSSDSSSSSB.",
            "...DDDDDDDDDD...",
            "...DD......DD...",
            "................",
        ],
        "S": [
            "....BBBDDBBB....",      # ponytail down her back
            "...BBBBDDBBBB...",
            "..BBBBBBDBBBBB..",
            "..BBBBBBBBBBBB..",
            "...DDDDDDDDDD...",
            "................",
            "................",
        ],
        "W": [
            ".....BBBBBB.....",
            "....BBBBBBBB....",
            "....BBBBBSSDS...",
            ".....BBBBSSDS...",
            ".....DDDDDDDDD..",
            "...........DD...",
            "...........DD...",
        ],
    },
}
HEAD_FROM = {"N": "down", "S": "up", "W": "right"}
# where to draw the student relative to the chair's tile (pixels), and whether the chair goes on top
PLACE = {"N": (0, -7, False), "S": (0, -8, True), "W": (1, -6, False), "E": (-1, -6, False)}


def seated(char, side, frame):
    art = BOY if char == "boy" else GIRL
    base = "W" if side == "E" else side
    head = art[HEAD_FROM[base]][:HEAD_ROWS]
    rows = [list(r) for r in head + BODY[char][base]]
    if frame == "read2":                       # head nods down one pixel over the book
        body = [list(r) for r in BODY[char][base]]
        rows = [["."] * T] + [list(r) for r in head]
        for x in range(T):                     # the chin overlaps the top row of the body
            if rows[HEAD_ROWS][x] == ".":
                rows[HEAD_ROWS][x] = body[0][x]
        rows += body[1:]
    rows = ["".join(r) for r in rows]
    if side == "E":
        rows = [r[::-1] for r in rows]
    assert len(rows) == T and all(len(r) == T for r in rows), (char, side, frame)
    assert len({c for c in "".join(rows) if c != "."}) <= 3
    return rows


SIDES = ["N", "S", "W", "E"]
FR = ["read1", "read2"]
sprites, atlas = {}, {}
sheet = Image.new("RGBA", (T * len(SIDES) * len(FR), T * 2), (0, 0, 0, 0))
for row, char in enumerate(["boy", "girl"]):
    for si, sd in enumerate(SIDES):
        for fi, fr in enumerate(FR):
            name = f"{char}_seat_{sd}_{fr}"
            im = to_img(seated(char, sd, fr), PALS[char])
            x, y = (si * len(FR) + fi) * T, row * T
            sheet.paste(im, (x, y), im)
            sprites[name] = im
            dx, dy, chair_on_top = PLACE[sd]
            atlas[name] = {"x": x, "y": y, "w": T, "h": T, "offset_from_chair": [dx, dy],
                           "draw_chair_on_top": chair_on_top}
sheet.save("students_seated_sheet.png")
json.dump({"tile_size": T, "sheet": "students_seated_sheet.png", "loop": ["read1", "read2"], "fps": 2,
           "note": "Draw at the chair's position plus offset_from_chair. If draw_chair_on_top is true, "
                   "draw the chair AFTER the student (the backrest hides the student's back).",
           "sprites": atlas}, open("students_seated_sheet.json", "w"), indent=2)

# ------------------------------------------------------------ previews
furn = Image.open("elsc_furniture_sheet.png")
fat = json.load(open("elsc_furniture_sheet.json"))["sprites"]


def fsp(n):
    q = fat[n]
    return furn.crop((q["x"], q["y"], q["x"] + q["w"], q["y"] + q["h"]))


def scene(frame):
    W, H = 6 * T, 6 * T
    bg = Image.new("RGBA", (W, H))
    for ty in range(6):
        for tx in range(6):
            bg.alpha_composite(fsp("carpet_a" if (tx + ty) % 2 == 0 else "carpet_b"), (tx * T, ty * T))
    tx, ty = 2 * T, 2 * T                       # table at tiles (2,2)-(3,3)
    seats = {"N": ("boy", (int(2.5 * T), 1 * T), "chair_green_N"),
             "S": ("girl", (int(2.5 * T), 4 * T), "chair_red_S"),
             "W": ("girl", (1 * T, int(2.5 * T)), "chair_blue_W"),
             "E": ("boy", (4 * T, int(2.5 * T)), "chair_white_E")}
    # back row first so overlaps look right: N, then W/E, table, then S
    for sd in ["N", "W", "E"]:
        char, (cx, cy), ch = seats[sd]
        bg.alpha_composite(fsp(ch), (cx, cy))
        dx, dy, _ = PLACE[sd]
        bg.alpha_composite(sprites[f"{char}_seat_{sd}_{frame}"], (cx + dx, cy + dy))
    bg.alpha_composite(fsp("table_square"), (tx, ty))
    char, (cx, cy), ch = seats["S"]
    dx, dy, _ = PLACE["S"]
    bg.alpha_composite(sprites[f"{char}_seat_S_{frame}"], (cx + dx, cy + dy))
    bg.alpha_composite(fsp(ch), (cx, cy))
    return bg


frames = []
for i in range(8):
    fr = "read1" if (i // 2) % 2 == 0 else "read2"
    frames.append(scene(fr).resize((6 * T * 6, 6 * T * 6), Image.NEAREST).convert("RGB"))
frames[0].save("students_seated_preview.gif", save_all=True, append_images=frames[1:], duration=250, loop=0)
scene("read1").resize((6 * T * 6, 6 * T * 6), Image.NEAREST).save("students_seated_scene_6x.png")
big = Image.new("RGBA", (sheet.width * 6, sheet.height * 6), (90, 90, 90, 255))
big.alpha_composite(sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST))
big.save("students_seated_sheet_6x.png")
print("ok:", len(sprites), "seated sprites, each <= 3 NES colors")
