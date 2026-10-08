"""ELSC Game - NES-style sprite sheet (furniture + floor).

Every sprite follows the strict NES rule: colors come only from the NES palette,
and each sprite uses at most 3 colors plus transparent.
Tile size: 16 x 16 pixels (one game tile).
"""
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- NES palette
NES = ["7C7C7C", "0000FC", "0000BC", "4428BC", "940084", "A80020", "A81000", "881400", "503000", "007800",
       "006800", "005800", "004058", "000000", "BCBCBC", "0078F8", "0058F8", "6844FC", "D800CC", "E40058",
       "F83800", "E45C10", "AC7C00", "00B800", "00A800", "00A844", "008888", "F8F8F8", "3CBCFC", "6888FC",
       "9878F8", "F878F8", "F85898", "F87858", "FCA044", "F8B800", "B8F818", "58D854", "58F898", "00E8D8",
       "787878", "FCFCFC", "A4E4FC", "B8B8F8", "D8B8F8", "F8B8F8", "F8A4C0", "F0D0B0", "FCE0A8", "F8D878",
       "D8F878", "B8F8B8", "B8F8D8", "00FCFC", "F8D8F8"]
NES = set(NES)
T = 16


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def to_img(grid, pal):
    """grid: 2D array of palette keys ('' = transparent); pal: key -> hex."""
    h, w = len(grid), len(grid[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            k = grid[y][x]
            if k:
                px[x, y] = rgb(pal[k])
    return im


def colors_in(im):
    a = np.array(im)
    a = a[a[:, :, 3] > 0][:, :3]
    return {"%02X%02X%02X" % tuple(c) for c in np.unique(a, axis=0)}


# ---------------------------------------------------------------- shading
def shade(mask, dark=None):
    """Light from the top-left: edges facing up/left get L, down/right get D."""
    h, w = mask.shape
    g = [["" for _ in range(w)] for _ in range(h)]
    def on(y, x):
        return 0 <= y < h and 0 <= x < w and mask[y, x]
    for y in range(h):
        for x in range(w):
            if not mask[y, x]:
                continue
            if dark is not None and dark[y, x]:
                g[y][x] = "D"
            elif not on(y + 1, x) or not on(y, x + 1):
                g[y][x] = "D"
            elif not on(y - 1, x) or not on(y, x - 1):
                g[y][x] = "L"
            else:
                g[y][x] = "M"
    return g


# ---------------------------------------------------------------- carpet
CARPET = {"D": "503000", "M": "7C7C7C", "L": "BCBCBC"}


def carpet(vertical, seed):
    """Quarter-turned carpet tiles: dark ribs every 3 pixels, a few light fibers."""
    r = random.Random(seed)
    g = [["M"] * T for _ in range(T)]
    for y in range(T):
        for x in range(T):
            a = x if vertical else y
            if a % 3 == 1 and r.random() > 0.3:
                g[y][x] = "D"            # dark brown rib
            elif a % 3 == 2 and r.random() < 0.07:
                g[y][x] = "L"            # light fiber
    return to_img(g, CARPET)


# ---------------------------------------------------------------- tables
TABLE = {"L": "FCFCFC", "M": "FCFCFC", "D": "BCBCBC", "K": "7C7C7C"}


def table(w_tiles, h_tiles):
    """Rounded 'squircle' white tabletop with a visible front edge (Zelda-style tilt)."""
    W, H = w_tiles * T, h_tiles * T
    edge = 3 if h_tiles > 1 else 2
    top_h = H - edge
    cx, cy = (W - 1) / 2, (top_h - 1) / 2
    a, b = W / 2, top_h / 2
    n = 5 if w_tiles == h_tiles else 7
    top = np.zeros((H, W), bool)
    for y in range(top_h):
        for x in range(W):
            if abs((x - cx) / a) ** n + abs((y - cy) / b) ** n <= 1:
                top[y, x] = True
    g = [["" for _ in range(W)] for _ in range(H)]
    for y in range(top_h):
        for x in range(W):
            if not top[y, x]:
                continue
            right_edge = x + 1 >= W or not top[y, x + 1]
            g[y][x] = "D" if right_edge else "L"
    # front edge: the table's thickness seen from the tilted camera
    for x in range(W):
        ys = [y for y in range(top_h) if top[y, x]]
        if not ys:
            continue
        bottom = max(ys)
        for k in range(1, edge + 1):
            yy = bottom + k
            if yy < H:
                g[yy][x] = "K" if k == edge else "D"
    return to_img(g, TABLE)


# ---------------------------------------------------------------- chairs
# Hand-drawn 16x16 chairs that fill the tile: shell backrest, seat and legs,
# like NES furniture. L = highlight, M = main color, D = shade + legs.
CHAIR_ART = {
    # above a table, facing down toward it: we see the front (backrest behind the seat)
    "N": [
        "...LLLLLLLLLL...",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "..DDDDDDDDDDDD..",
        ".LLLLLLLLLLLLLL.",
        ".LMMMMMMMMMMMMD.",
        ".LMMMMMMMMMMMMD.",
        ".DMMMMMMMMMMMMD.",
        "..DDDDDDDDDDDD..",
        "..D..........D..",
        "..D.D......D.D..",
        "..D.D......D.D..",
        "..D..........D..",
    ],
    # below a table, facing up toward it: we see the back of the shell, the seat peeks out above
    "S": [
        "................",
        "...LLLLLLLLLL...",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "..LMMMMMMMMMMD..",
        "...DMMMMMMMMD...",
        "....DMMMMMMD....",
        ".LLLLLLLLLLLLLL.",
        ".DMMMMMMMMMMMMD.",
        "..DDDDDDDDDDDD..",
        "..D..........D..",
        "..D.D......D.D..",
        "..D.D......D.D..",
        "..D..........D..",
        "..D..........D..",
    ],
    # left of a table, facing right toward it: side view, backrest on the left
    "W": [
        ".LLL............",
        ".LMD............",
        ".LMD............",
        ".LMD............",
        ".LMD............",
        ".LMD............",
        ".LMD............",
        ".LMLLLLLLLLLLL..",
        ".LMMMMMMMMMMMMD.",
        ".DDDDDDDDDDDDDD.",
        "..D..........D..",
        "..D.D.....D..D..",
        "..D.D.....D..D..",
        "..D..........D..",
        "..D..........D..",
        "................",
    ],
}


def chair(side, pal):
    if side in ("W", "E"):   # left/right of a table: the front-view chair rotated so its back faces away
        k = 1 if side == "W" else -1
        rows = ["".join(r) for r in np.rot90(np.array([list(r) for r in CHAIR_ART["N"]]), k)]
    else:
        rows = CHAIR_ART[side]
    grid = [["" if c == "." else c for c in r] for r in rows]
    return to_img(grid, pal)


CHAIRS = {
    "red":   {"L": "F87858", "M": "F83800", "D": "A81000"},
    "green": {"L": "D8F878", "M": "B8F818", "D": "00A800"},
    "blue":  {"L": "FCFCFC", "M": "A4E4FC", "D": "3CBCFC"},
    "white": {"L": "FCFCFC", "M": "FCFCFC", "D": "BCBCBC"},
}
CHAIR_ORDER = ["blue", "white", "green", "red"]   # same color cycle as the approved map


# ---------------------------------------------------------------- bookshelf
BOOK_COLORS = {"red": "F83800", "blue": "0058F8", "yellow": "F8B800", "teal": "008888"}


def shelf_front(book, seed):
    """Shelf seen from the front: wood top, white shelving, one color of books.
    Colors: wood, white, one book color (3 total)."""
    r = random.Random(seed)
    g = [["F"] * T for _ in range(T)]
    for y in range(3):                              # golden oak top board
        for x in range(T):
            g[y][x] = "W"
    for top, bot in ((4, 8), (10, 14)):
        x = 1 + r.randint(0, 1)
        while x < T:
            w = r.choice([1, 2, 2])
            hgt = r.randint(3, bot - top + 1)
            if r.random() < 0.1:                     # the odd gap on the shelf
                x += 2
                continue
            for xx in range(x, min(x + w, T)):
                for y in range(bot - hgt + 1, bot + 1):
                    g[y][xx] = "B"
            x += w + 1                               # white gap between books
    return to_img(g, {"W": "FCA044", "F": "FCFCFC", "B": BOOK_COLORS[book]})


def shelf_top():
    """Top board of a shelf seen from above (for the back rows of the thick left shelf)."""
    g = [["F"] * T for _ in range(T)]
    for y in range(T):
        g[y][T - 1] = "D"
        if y % 8 == 7:
            for x in range(T):
                g[y][x] = "D"
    for x in range(T):
        g[0][x] = "L" if g[0][x] == "F" else g[0][x]
    return to_img(g, {"F": "FCFCFC", "L": "FCFCFC", "D": "BCBCBC"})


def rotate(im, k):
    return Image.fromarray(np.rot90(np.array(im), k))


# ---------------------------------------------------------------- whiteboard
def whiteboard():
    """Diagonal mobile whiteboard across 3 tiles (G20 -> I22): black frame, white face, blue marker."""
    S = 3 * T
    g = [["" for _ in range(S)] for _ in range(S)]
    p0, p1 = np.array([4.0, 4.0]), np.array([S - 5.0, S - 5.0])
    d = p1 - p0
    L2 = d @ d
    for y in range(S):
        for x in range(S):
            p = np.array([x, y], float)
            t = np.clip(((p - p0) @ d) / L2, 0, 1)
            dist = np.linalg.norm(p - (p0 + t * d))
            if dist <= 4.2:
                g[y][x] = "K" if (dist > 3.0 or t in (0.0, 1.0)) else "W"
    # marker scribbles along the board
    for i in range(10, 36, 2):
        y = i + (1 if (i // 2) % 2 else -1)
        x = i
        if g[y][x] == "W":
            g[y][x] = "B"
    for i in range(14, 30, 3):
        if g[i + 1][i - 1] == "W":
            g[i + 1][i - 1] = "B"
    # feet of the stand at both ends
    for (fx, fy) in [(1, 8), (8, 1), (S - 9, S - 2), (S - 2, S - 9)]:
        g[fy][fx] = "K"
    return to_img(g, {"K": "000000", "W": "FCFCFC", "B": "0058F8"})


# ---------------------------------------------------------------- placeholders (no photo yet)
def wall():
    g = [["M"] * T for _ in range(T)]
    for i in range(T):
        g[0][i] = "L"
        g[i][0] = "L"
        g[T - 1][i] = "D"
        g[i][T - 1] = "D"
    return to_img(g, {"L": "BCBCBC", "M": "7C7C7C", "D": "000000"})


def desk():
    g = [["M"] * T for _ in range(T)]
    for i in range(T):
        g[0][i] = "L"
        g[T - 1][i] = "D"
        g[T - 2][i] = "D"
    return to_img(g, {"L": "FCE0A8", "M": "FCA044", "D": "AC7C00"})


# ---------------------------------------------------------------- build everything
sprites = {}
sprites["carpet_a"] = carpet(True, 11)
sprites["carpet_b"] = carpet(False, 23)
sprites["table_square"] = table(2, 2)
sprites["table_long"] = table(2, 6)
sprites["table_small"] = table(1, 1)
for c in CHAIR_ORDER:
    for s in "NSWE":
        sprites[f"chair_{c}_{s}"] = chair(s, CHAIRS[c])
for i, b in enumerate(BOOK_COLORS):
    f = shelf_front(b, 100 + i)
    sprites[f"shelf_front_{b}"] = f           # faces down (top wall)
    sprites[f"shelf_east_{b}"] = rotate(f, 1)  # faces right (left wall, right side of inner shelves)
    sprites[f"shelf_west_{b}"] = rotate(f, -1) # faces left (left side of inner shelves)
    sprites[f"shelf_north_{b}"] = rotate(f, 2) # faces up (bottom wall)
sprites["shelf_top"] = shelf_top()
sprites["whiteboard"] = whiteboard()
sprites["wall_placeholder"] = wall()
sprites["desk_placeholder"] = desk()

# NES rule check
for name, im in sprites.items():
    cs = colors_in(im)
    assert len(cs) <= 3, (name, cs)
    assert cs <= NES, (name, cs - NES)
print("NES check passed:", len(sprites), "sprites, all <= 3 colors from the NES palette")

# ---------------------------------------------------------------- pack the sheet (8 tiles wide)
COLS = 8
occupied = set()
atlas = {}
order = sorted(sprites, key=lambda n: -(sprites[n].size[0] * sprites[n].size[1]))
for name in order:
    w, h = sprites[name].size[0] // T, sprites[name].size[1] // T
    y = 0
    placed = False
    while not placed:
        for x in range(COLS - w + 1):
            cells = {(x + i, y + j) for i in range(w) for j in range(h)}
            if not cells & occupied:
                occupied |= cells
                atlas[name] = {"x": x * T, "y": y * T, "w": w * T, "h": h * T}
                placed = True
                break
        y += 1
rows = max(v["y"] + v["h"] for v in atlas.values()) // T
sheet = Image.new("RGBA", (COLS * T, rows * T), (0, 0, 0, 0))
for n, r_ in atlas.items():
    sheet.paste(sprites[n], (r_["x"], r_["y"]), sprites[n])
sheet.save("elsc_furniture_sheet.png")
with open("elsc_furniture_sheet.json", "w") as f:
    json.dump({"tile_size": T, "sheet": "elsc_furniture_sheet.png",
               "sprites": dict(sorted(atlas.items()))}, f, indent=2)
print("sheet", sheet.size, "->", len(atlas), "sprites")

# ---------------------------------------------------------------- labeled preview of the sheet
Z = 5
F = "/usr/share/fonts/truetype/dejavu/"
font = ImageFont.truetype(F + "DejaVuSans.ttf", 12)
big = sheet.resize((sheet.width * Z, sheet.height * Z), Image.NEAREST)
prev = Image.new("RGBA", (big.width + 40, big.height + 40), (60, 60, 60, 255))
chk = Image.new("RGBA", big.size)
cd = ImageDraw.Draw(chk)
for y in range(0, big.height, 8 * Z // 2):
    for x in range(0, big.width, 8 * Z // 2):
        cd.rectangle([x, y, x + 20, y + 20], fill=(90, 90, 90, 255) if (x // 20 + y // 20) % 2 else (75, 75, 75, 255))
prev.paste(chk, (20, 20))
prev.alpha_composite(big, (20, 20))
d = ImageDraw.Draw(prev)
for i in range(COLS + 1):
    d.line([(20 + i * T * Z, 20), (20 + i * T * Z, 20 + big.height)], fill=(255, 255, 255, 60))
for j in range(rows + 1):
    d.line([(20, 20 + j * T * Z), (20 + big.width, 20 + j * T * Z)], fill=(255, 255, 255, 60))
prev.save("preview_sheet_5x.png")

# ---------------------------------------------------------------- render the approved stage with the sprites
shelves_front = [(3, 0, 15, 1)]
shelves_north = [(3, 23, 15, 1)]
walls = [(18, 0, 6, 1), (23, 1, 1, 1), (22, 2, 2, 22), (18, 23, 4, 1)]
tables = [("table_long", 9, 2), ("table_square", 5, 10), ("table_square", 11, 10), ("table_small", 18, 9),
          ("table_square", 6, 16), ("table_square", 15, 14), ("table_square", 10, 18), ("table_square", 15, 19)]
table_rects = [(9, 2, 2, 6), (5, 10, 2, 2), (11, 10, 2, 2), (18, 9, 1, 1), (6, 16, 2, 2), (15, 14, 2, 2),
               (10, 18, 2, 2), (15, 19, 2, 2)]
desks = [(19, 3, 1, 4), (20, 9, 1, 3), (21, 8, 1, 1), (21, 12, 1, 1)]
chairs = [(8, 2.5, 0), (8, 4.5, 0), (8, 6.5, 0), (11, 2.5, 0), (11, 4.5, 0), (11, 6.5, 0), (5.5, 9, 1), (5.5, 12, 1),
          (4, 10.5, 1), (7, 10.5, 1), (11.5, 9, 2), (11.5, 12, 2), (10, 10.5, 2), (13, 10.5, 2), (18, 8, 3), (17, 9, 3),
          (19, 9, 3), (6.5, 15, 4), (5, 16.5, 4), (8, 16.5, 4), (15.5, 13, 5), (14, 14.5, 5), (17, 14.5, 5),
          (10.5, 17, 6), (10.5, 20, 6), (9, 18.5, 6), (12, 18.5, 6), (15.5, 18, 7), (15.5, 21, 7), (14, 19.5, 7),
          (17, 19.5, 7)]
book_names = list(BOOK_COLORS)
N = 24
stage = Image.new("RGBA", (N * T, N * T), (0, 0, 0, 255))


def put(name, tx, ty):
    im = sprites[name]
    stage.alpha_composite(im, (int(round(tx * T)), int(round(ty * T))))


for y in range(N):
    for x in range(N):
        put("carpet_a" if (x + y) % 2 == 0 else "carpet_b", x, y)
# left thick shelf: the column facing the room shows books, the back columns show the top board
for y in range(N):
    for x in range(3):
        put(f"shelf_east_{book_names[(y * 3 + x * 2) % 4]}", x, y)
for (x0, y0, w, h) in shelves_front:
    for x in range(x0, x0 + w):
        put(f"shelf_front_{book_names[(x * 3 + 1) % 4]}", x, y0)
for (x0, y0, w, h) in shelves_north:
    for x in range(x0, x0 + w):
        put(f"shelf_north_{book_names[(x * 5 + 2) % 4]}", x, y0)
for (x0, y0, w, h) in [(15, 1, 2, 7), (18, 14, 2, 9)]:
    for y in range(y0, y0 + h):
        put(f"shelf_west_{book_names[(y * 3 + x0) % 4]}", x0, y)
        put(f"shelf_east_{book_names[(y * 7 + x0 + 1) % 4]}", x0 + 1, y)
for (x0, y0, w, h) in walls:
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put("wall_placeholder", x, y)
for (x0, y0, w, h) in desks:
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put("desk_placeholder", x, y)
for i, (cx, cy, ti) in enumerate(chairs):
    tx, ty, tw, th = table_rects[ti]
    mx, my = tx + tw / 2, ty + th / 2
    # which side of its table the chair is on: left/right if it's outside the table's columns
    if cx + 1 <= tx:
        side = "W"
    elif cx >= tx + tw:
        side = "E"
    else:
        side = "N" if cy < my else "S"
    put(f"chair_{CHAIR_ORDER[i % 4]}_{side}", cx, cy)
for (n, x, y) in tables:
    put(n, x, y)
put("whiteboard", 6, 19)
stage.save("preview_stage_1x.png")
stage.resize((N * T * 2, N * T * 2), Image.NEAREST).save("preview_stage_2x.png")
# one NES screen (16 x 11 tiles) around the middle tables, at 4x like a real monitor
crop = stage.crop((3 * T, 8 * T, 19 * T, 19 * T))
crop.resize((crop.width * 4, crop.height * 4), Image.NEAREST).save("preview_one_screen_4x.png")
print("previews saved")
