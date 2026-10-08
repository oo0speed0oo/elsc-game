"""ELSC Game v2 - Haruna (receptionist) and Hitomi (walking teacher), NES style.

Each sprite is drawn as up to 3 stacked NES layers (the NES trick of stacking sprites),
and every layer keeps the strict rule: at most 3 colors, all from the NES palette.
The sheet stores each sprite already stacked, so the game just draws one image.

In-room sprites are 16 x 16 (one tile, same size as the students).
Results-screen portraits are 32 x 32 (head and shoulders).
"""
import json
from PIL import Image

NES = set("""7C7C7C 0000FC 0000BC 4428BC 940084 A80020 A81000 881400 503000 007800 006800 005800 004058 000000
BCBCBC 0078F8 0058F8 6844FC D800CC E40058 F83800 E45C10 AC7C00 00B800 00A800 00A844 008888 F8F8F8 3CBCFC
6888FC 9878F8 F878F8 F85898 F87858 FCA044 F8B800 B8F818 58D854 58F898 00E8D8 787878 FCFCFC A4E4FC B8B8F8
D8B8F8 F8B8F8 F8A4C0 F0D0B0 FCE0A8 F8D878 D8F878 B8F8B8 B8F8D8 00FCFC F8D8F8""".split())

# letter -> (layer, color)
PAL = {
    "haruna": {"D": (1, "000000"), "K": (1, "000000"), "S": (1, "F0D0B0"), "M": (1, "F87858"),
               "B": (2, "AC7C00"), "W": (2, "FCFCFC"), "L": (2, "0058F8")},
    "hitomi": {"D": (1, "503000"), "S": (1, "F0D0B0"), "K": (1, "000000"),
               "B": (2, "F8D878"), "L": (2, "0058F8"), "Y": (2, "F8B800"),
               "W": (3, "FCFCFC"), "H": (3, "881400"), "M": (3, "F87858")},
}


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def render(rows, who, name):
    w = len(rows[0])
    assert all(len(r) == w for r in rows), (name, [len(r) for r in rows])
    im = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    px = im.load()
    layers = {}
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == ".":
                continue
            layer, col = PAL[who][c]
            layers.setdefault(layer, set()).add(col)
            px[x, y] = rgb(col)
    for layer, cols in layers.items():
        assert len(cols) <= 3, (name, layer, cols)
        assert cols <= NES, (name, cols - NES)
    return im, {k: sorted(v) for k, v in layers.items()}


def mirror(rows):
    return [r[::-1] for r in rows]


def edit(rows, changes):
    """changes: {row: string} replaces whole rows."""
    rows = list(rows)
    for y, s in changes.items():
        rows[y] = s
    return rows


# =================================================================== HITOMI (walks around)
# long straight dark-brown hair, side-swept bangs, gold hoop earring, beige jacket, blue lanyard
HIT_TOP = {
    "down": [
        "................",
        ".....DDDDDD.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDDDDDDSSD...",
        "..DDDDDSSSSSDD..",
        "..DDSKSSSSKSDD..",
        "..DYSSSSSSSSDD..",
        "..DD.SSSSSS.DD..",
        "..DDBBLSSLBBDD..",
        "..DDBBBLLBBBDD..",
        "..SDBBBLLBBBDS..",
        "..SBBBBBBBBBBS..",
    ],
    "up": [
        "................",
        ".....DDDDDD.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDDDDDDDDD...",
        "..DDDDDDDDDDDD..",
        "..DDDDDDDDDDDD..",
        "..YDDDDDDDDDDD..",
        "..DDDDDDDDDDDD..",
        "..BDDDDDDDDDDB..",
        "..BBDDDDDDDDBB..",
        "..SBBDDDDDDBBS..",
        "..SBBBBBBBBBBS..",
    ],
    "right": [
        "................",
        "......DDDDD.....",
        "....DDDDDDDD....",
        "...DDDDDDDDDD...",
        "...DDDDDDDDSSD..",
        "..DDDDDDSSSSSS..",
        "..DDDDDYSSSKSS..",
        "..DDDDDDSSSSSS..",
        "..DDDDDDDSSSS...",
        "..DDDDDBBBBB....",
        "...DDDBBBBBLB...",
        "...DDDBBBBSBB...",
        "....DDBBBBBBB...",
    ],
}
LEGS = {
    "front": {
        "stand": ["....DDDDDDDD....", "....DDD..DDD....", "....KKK..KKK...."],
        "walk1": ["....DDDDDDDD....", "....DDD..DDD....", "....KKK........."],
        "walk2": ["....DDDDDDDD....", "....DDD..DDD....", ".........KKK...."],
    },
    "side": {
        "stand": [".....DDDDDD.....", ".....DD..DD.....", ".....KK..KK....."],
        "walk1": [".....DDDDDD.....", "....DD....DD....", "...KK......KK..."],
        "walk2": [".....DDDDDD.....", "......DDDD......", "......KKKK......"],
    },
}


def hitomi_walk(direction, frame):
    base = "right" if direction == "left" else direction
    top = [list(r) for r in HIT_TOP[base]]
    if base in ("down", "up") and frame != "stand":      # little arm swing
        col = 2 if frame == "walk1" else 13
        if top[12][col] == "S":
            top[12][col] = "."
            top[10][col] = "S"
    rows = ["".join(r) for r in top] + LEGS["side" if base == "right" else "front"][frame]
    return mirror(rows) if direction == "left" else rows


# "DID YOU STUDY?!" : facing you, finger pointing up and wagging, other hand on her hip
HIT_POINT1 = edit(HIT_TOP["down"], {
    7: "..DYSSSSSSSSDDS.",
    8: "..DD.SSSSSS.DDS.",
    9: "..DDBBLSSLBBDDB.",
    10: "..DDBBBLLBBBBBB.",
    11: ".SBDBBBLLBBBDD..",
    12: "..SBBBBBBBBBBB..",
}) + LEGS["front"]["stand"]
HIT_POINT2 = edit(HIT_TOP["down"], {
    5: "..DDDDDSSSSSDDS.",
    6: "..DDSKSSSSKSDDS.",
    7: "..DYSSSSSSSSDDB.",
    8: "..DD.SSSSSS.DDB.",
    9: "..DDBBLSSLBBDDB.",
    10: "..DDBBBLLBBBBB..",
    11: ".SBDBBBLLBBBDD..",
    12: "..SBBBBBBBBBBB..",
}) + LEGS["front"]["stand"]

# sitting at her desk (drawn facing right here, mirrored to face left when packed); the chair is drawn under her
HIT_SEAT_W = HIT_TOP["right"][:9] + [
    "..DDDDDBBBBB....",
    "...DDDBBBBBLB...",
    "...DDDBBBBSSKS..",      # hands on the keyboard
    "....DDBBBBSSKS..",
    ".....DDDDDDDDD..",
    "...........DD...",
    "...........KK...",
]
HIT_SEAT_W2 = HIT_TOP["right"][:9] + [
    "..DDDDDBBBBB....",
    "...DDDBBBBBLB...",
    "...DDDBBBBSKSS..",
    "....DDBBBBSSKS..",
    ".....DDDDDDDDD..",
    "...........DD...",
    "...........KK...",
]

# =================================================================== HARUNA (sits at her desk)
# short black pixie / bob hair with bangs parted in the middle, brown blazer, white tee, blue lanyard
HAR_RIGHT = [                      # facing right (toward her desk), typing
    "................",
    ".....DDDDDD.....",
    "....DDDDDDDD....",
    "...DDDDDDDDDD...",
    "...DDDDDDDDSD...",
    "...DDDDDSSSSSS..",
    "...DDDDSSSSKSS..",
    "...DDDDSSSSSSS..",
    "....DDDDSSSSS...",
    "....BBBBBWW.....",
    "...BBBBBBLWB....",
    "...BBBBBBSSSS...",
    "....BBBBBBBS....",
    ".....DDDDDDDD...",
    "...........DD...",
    "...........DD...",
]
HAR_RIGHT2 = edit(HAR_RIGHT, {11: "...BBBBBBBSS.S..", 12: "....BBBBBBSSS..."})

HAR_FRONT_HEAD = [
    "................",
    ".....DDDDDD.....",
    "....DDDDDDDD....",
    "...DDDDDDDDDD...",
    "...DDDDSDDDDD...",
    "...DDSSSSSSDD...",
    "...DSKSSSSKSD...",
    "...DSSSSSSSSD...",
    "...DDSSMMSSDD...",
]
# "BE QUIET PLEASE, PEOPLE ARE STUDYING!" : turns to the room, both hands up (2 frames)
HAR_CALL1 = [
    "................",
    ".....DDDDDD.....",
    "S...DDDDDDDD...S",
    "S..DDDDDDDDDD..S",
    "B..DDDDSDDDDD..B",
    "B..DDSSSSSSDD..B",
    "BB.DSKSSSSKSD.BB",
    ".B.DSSSSSSSSD.B.",
    ".BBDDSSMMSSDDBB.",
    "..BBBBBWWBBBBB..",
    "...BBBBLWLBBB...",
    "...BBBBWLWBBB...",
    "...BBBBBBBBBB...",
    "...DDDDDDDDDD...",
    "...DD......DD...",
    "...DD......DD...",
]
HAR_CALL2 = edit(HAR_CALL1, {
    2: "....DDDDDDDD....",
    3: "S..DDDDDDDDDD..S",
    4: "S..DDDDSDDDDD..S",
    5: "B..DDSSSSSSDD..B",
    6: "B..DSKSSSSKSD..B",
    7: "BB.DSSSSSSSSD.BB",
    8: ".BBDDSSMMSSDDBB.",
})
# drops the headphones: one arm stretched out toward the floor in front of her
HAR_TOSS = HAR_FRONT_HEAD + [
    "....BBBWWBBBBBB.",
    "...BBBBLWLBBBBSS",
    "..SBBBBWLWBBB...",
    "...BBBBBBBBBB...",
    "...DDDDDDDDDD...",
    "...DD......DD...",
    "...DD......DD...",
]

# =================================================================== PORTRAITS (32 x 32, results screen)
HAR_PORTRAIT = [
    "................................",
    "................................",
    "...........DDDDDDDDDD...........",
    ".........DDDDDDDDDDDDDD.........",
    "........DDDDDDDDDDDDDDDD........",
    ".......DDDDDDDDDDDDDDDDDD.......",
    ".......DDDDDDDDDDDDDDDDDD.......",
    "......DDDDDDDDDDSDDDDDDDDD......",
    "......DDDDDDDDDSSDDDDDDDDD......",
    "......DDDDDDDDSSSSDDDDDDDD......",
    "......DDDDDDDSSSSSSDDDDDDD......",
    "......DDDDDSSSSSSSSSSDDDDD......",
    "......DDDDSSSSSSSSSSSSDDDD......",
    "......DDDSSSSSSSSSSSSSSDDD......",
    "......DDDSSSSSSSSSSSSSSDDD......",
    "......DDSSSSKKSSSSKKSSSSDD......",
    "......DDSSSKSSKSSKSSKSSSDD......",
    "......DDSSSSSSSSSSSSSSSSDD......",
    "......DDSSMMSSSSSSSSMMSSDD......",
    "......DDSSSSSSSSSSSSSSSSDD......",
    "......DDDSSSSKKKKKKSSSSSDD......",
    "......DDDSSSSKWWWWKSSSSDDD......",
    ".......DDDSSSSKKKKSSSSDDD.......",
    "........DD.SSSSSSSSSS.DD........",
    "............SSSSSSSS............",
    ".............SSSSSS.............",
    "........BBBBBWWSSWWBBBBB........",
    "......BBBBBBBWWWWWWBBBBBBB......",
    "....BBBBBBBBLWWWWWWLBBBBBBBB....",
    "...BBBBBBBBBBLWWWWLBBBBBBBBBB...",
    "..BBBBBBBBBBBBLWWLBBBBBBBBBBBB..",
    "..BBBBBBBBBBBBBLLBBBBBBBBBBBBB..",
]
# the mouth teeth use K/W: W is in Haruna's layer 2 (white shirt), so the smile shares it
HAR_PORTRAIT_TALK = edit(HAR_PORTRAIT, {
    20: "......DDDSSSSSKKKKSSSSSSDD......",
    21: "......DDDSSSSKKMMKKSSSSDDD......",
    22: ".......DDDSSSSKKKKSSSSDDD.......",
})

HIT_PORTRAIT = [
    "................................",
    "..........DDDDDDDDDDD...........",
    "........DDDDDDDDDDDDDDD.........",
    ".......DDDDDDDDDDDDDDDDD........",
    "......DDDDDDDDDDDDDDDDDDD.......",
    "......DDDDDDDDDDDDDDDDDDD.......",
    ".....DDDDDDDDHDDDDDDDSSDDD......",
    ".....DDDDDDDDDHDDDDDSSSSDD......",
    ".....DDDDDDDDDDHDDSSSSSSDD......",
    ".....DDHDDDDDDDDSSSSSSSSDD......",
    ".....DDHDDDDDSSSSSSSSSSSDDD.....",
    ".....DDDDDSSSSSSSSSSSSSSSDD.....",
    ".....DDDDSSSSSSSSSSSSSSSSDD.....",
    ".....DDDSSSSSSSSSSSSSSSSSDD.....",
    ".....DDDSSKKKSSSSSSKKKSSSDD.....",
    ".....DDDSSKWKSSSSSSKWKSSSDD.....",
    ".....DDDSSKKKSSSSSSKKKSSSDD.....",
    ".....DDDSSSSSSSSSSSSSSSSSDD.....",
    "....DDDDSMMSSSSSSSSSSSMMSDDD....",
    "....DHDYSSSSSSSSSSSSSSSSSDHD....",
    "....DDDYSSSSKWWWWWWKSSSSSDDD....",
    "....DDDDSSSSSKWWWWKSSSSSSDDD....",
    "....DDHD.SSSSSKKKKSSSSS.DDDD....",
    "....DDDD...SSSSSSSSSS...DDHD....",
    "....DDDD.....SSSSSS.....DDDD....",
    "...DDHDD......SSSS......DDDDD...",
    "...DDDDDBBBBBBSSSSBBBBBBDDHDD...",
    "...DDDDBBBBBBBLSSLBBBBBBBDDDD...",
    "..DDDHBBBBBBBBBLLBBBBBBBBBDDDD..",
    "..DDDDBBBBBBBBBLLBBBBBBBBBBDDD..",
    "..DDDBBBBBBBBBBLLBBBBBBBBBBBDD..",
    "..DDBBBBBBBBBBBLLBBBBBBBBBBBBD..",
]


def hit_cheer(up):
    """YOU PASSED! : both fists up next to her head (up=True raises them one pixel higher)."""
    rows = [list(r) for r in HIT_PORTRAIT]
    top = 11 if up else 13
    fist = [".KKK.", "KSSSK", "KSSSK", "KSSSK", ".KBK."]
    for x0 in (0, 27):
        for dy, line in enumerate(fist):
            for dx, c in enumerate(line):
                if c != ".":
                    rows[top + dy][x0 + dx] = c
        for y in range(top + 5, 32):              # sleeves down to the shoulders
            for dx in range(1, 4):
                rows[y][x0 + dx] = "B"
            rows[y][x0] = "K"
            rows[y][x0 + 4] = "K"
    for x in range(12, 20):                       # bigger open smile
        rows[20][x] = "W" if 13 <= x <= 18 else "K"
    return ["".join(r) for r in rows]


def hit_sorry(shift):
    """YOU FAILED... : eyes closed, a small frown, head shaking (shift -1 / +1 px)."""
    rows = edit(HIT_PORTRAIT, {
        14: ".....DDDSSSSSSSSSSSSSSSSSDD.....",
        15: ".....DDDSSKKKSSSSSSKKKSSSDD.....",
        16: ".....DDDSSSSSSSSSSSSSSSSSDD.....",
        20: "....DDDYSSSSSSSSSSSSSSSSSDDD....",
        21: "....DDDDSSSSSSKKKKSSSSSSSDDD....",
        22: "....DDHD.SSSSKSSSSKSSSS.DDDD....",
    })
    if shift:
        rows = [(r[1:] + ".") if shift < 0 else ("." + r[:-1]) for r in rows[:26]] + rows[26:]
    return rows


# =================================================================== build the sheet
SPRITES = [
    # name, who, rows
    ("hitomi_point1", "hitomi", HIT_POINT1),
    ("hitomi_point2", "hitomi", HIT_POINT2),
    ("hitomi_desk_work1", "hitomi", mirror(HIT_SEAT_W)),
    ("hitomi_desk_work2", "hitomi", mirror(HIT_SEAT_W2)),
    ("haruna_type1", "haruna", HAR_RIGHT),
    ("haruna_type2", "haruna", HAR_RIGHT2),
    ("haruna_call1", "haruna", HAR_CALL1),
    ("haruna_call2", "haruna", HAR_CALL2),
    ("haruna_toss", "haruna", HAR_TOSS),
]
for d in ["down", "up", "left", "right"]:
    for f in ["stand", "walk1", "walk2"]:
        SPRITES.append((f"hitomi_{d}_{f}", "hitomi", hitomi_walk(d, f)))

PORTRAITS = [
    ("portrait_haruna_smile", "haruna", HAR_PORTRAIT),
    ("portrait_haruna_talk", "haruna", HAR_PORTRAIT_TALK),
    ("portrait_hitomi_smile", "hitomi", HIT_PORTRAIT),
    ("portrait_hitomi_cheer1", "hitomi", hit_cheer(False)),
    ("portrait_hitomi_cheer2", "hitomi", hit_cheer(True)),
    ("portrait_hitomi_sorry1", "hitomi", hit_sorry(-1)),
    ("portrait_hitomi_sorry2", "hitomi", hit_sorry(1)),
]

images, layers_used = {}, {}
for name, who, rows in SPRITES + PORTRAITS:
    images[name], layers_used[name] = render(rows, who, name)

order_small = [n for n, _, _ in SPRITES]
order_big = [n for n, _, _ in PORTRAITS]
COLS = 12
rows_small = (len(order_small) + COLS - 1) // COLS
sheet = Image.new("RGBA", (COLS * 16, rows_small * 16 + 32), (0, 0, 0, 0))
atlas = {}
for i, n in enumerate(order_small):
    x, y = (i % COLS) * 16, (i // COLS) * 16
    sheet.paste(images[n], (x, y))
    atlas[n] = {"x": x, "y": y, "w": 16, "h": 16}
sheet_big = Image.new("RGBA", (len(order_big) * 32, 32), (0, 0, 0, 0))
for i, n in enumerate(order_big):
    sheet_big.paste(images[n], (i * 32, 0))
full = Image.new("RGBA", (max(sheet.width, sheet_big.width), rows_small * 16 + 32), (0, 0, 0, 0))
full.paste(sheet.crop((0, 0, sheet.width, rows_small * 16)), (0, 0))
full.paste(sheet_big, (0, rows_small * 16))
for i, n in enumerate(order_big):
    atlas[n] = {"x": i * 32, "y": rows_small * 16, "w": 32, "h": 32}
full.save("people_v2_sheet.png")
json.dump({
    "sheet": "people_v2_sheet.png",
    "note": "Each sprite is already stacked from up to 3 NES layers (each layer <= 3 NES colors).",
    "hitomi_walk": "hitomi_<down|up|left|right>_<stand|walk1|walk2>, walk1/walk2 about 8 changes per second",
    "hitomi_point": "'DID YOU STUDY?!' pose: loop point1/point2 at about 4 per second",
    "hitomi_desk": "hitomi_desk_work1/2: sitting at her desk facing left (toward her monitor and the room): loop work1/work2 at 2 per second, drawn over office_chair",
    "haruna": "type1/type2 at her desk (facing right, toward her desk, 2 per second); call1/call2 when she calls out "
              "(4 per second); toss when she drops the headphones (0.4 s)",
    "portraits": "results screen: haruna smile/talk ('DID YOU PASS?'), hitomi cheer1/cheer2 (PASSED), "
                 "sorry1/sorry2 (FAILED), each pair loops at 4 per second",
    "sprites": atlas,
    "layers": layers_used,
}, open("people_v2_sheet.json", "w"), indent=1)
print("ok:", len(images), "people sprites; every layer <= 3 NES colors")
