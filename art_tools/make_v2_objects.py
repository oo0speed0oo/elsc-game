"""ELSC Game v2 - desks, office chair, coffee station, power-ups and the book, NES style.

Same rule as all the other art: every layer uses at most 3 NES colors; bigger or more colorful
things are stacked from 2-3 layers (the NES trick). The sheet stores them already stacked.
"""
import json
from PIL import Image

exec(open("make_v2_people.py").read().split("# =================================================================== HITOMI")[0])


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [["."] * w for _ in range(h)]

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):          # inclusive
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def rows(self, y0, lines, x0=0):
        for dy, line in enumerate(lines):
            for dx, c in enumerate(line):
                if c != ".":
                    self.px(x0 + dx, y0 + dy, c)

    def out(self):
        return ["".join(r) for r in self.g]


def paint(rows, pal, name):
    """pal: letter -> (layer, color)"""
    w = len(rows[0])
    assert all(len(r) == w for r in rows), name
    im = Image.new("RGBA", (w, len(rows)), (0, 0, 0, 0))
    p = im.load()
    layers = {}
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == ".":
                continue
            layer, col = pal[c]
            layers.setdefault(layer, set()).add(col)
            p[x, y] = rgb(col)
    for layer, cols in layers.items():
        assert len(cols) <= 3, (name, layer, cols)
        assert cols <= NES, (name, cols - NES)
    return im, {k: sorted(v) for k, v in layers.items()}


def flip_v(rows):
    return rows[::-1]


OUT = {}   # name -> (image, layers, note)

# =================================================================== desks (light wood top, white work surface)
DESK = {"A": (1, "FCA044"), "a": (1, "AC7C00"), "w": (1, "FCFCFC"),
        "K": (2, "000000"), "G": (2, "7C7C7C"), "L": (2, "BCBCBC")}


def haruna_desk(part, prop=None):
    """Haruna's straight desk: white work surface on the west (her side), tall wood counter on the east."""
    c = Canvas(16, 16)
    for y in range(16):
        c.px(0, y, "a")
        c.rect(1, y, 8, y, "w")
        c.px(9, y, "a")
        c.rect(10, y, 14, y, "A")
        c.px(15, y, "a")
    for y in (4, 11):
        c.px(12, y, "a")                           # wood grain
    if part == "top":
        c.rect(0, 0, 15, 0, "a")
        c.rect(1, 1, 14, 2, "A")
        c.rect(0, 3, 8, 3, "a")
        c.px(0, 1, "a"); c.px(0, 2, "a"); c.px(15, 1, "a"); c.px(15, 2, "a")
        c.px(0, 0, "."); c.px(15, 0, ".")
    if part == "bottom":
        c.rect(0, 15, 15, 15, "a")
        c.rect(1, 13, 14, 14, "A")
        c.rect(0, 12, 8, 12, "a")
        c.px(0, 13, "a"); c.px(0, 14, "a"); c.px(15, 13, "a"); c.px(15, 14, "a")
        c.px(0, 15, "."); c.px(15, 15, ".")
    if prop == "monitor":                          # thin monitor seen from above, screen toward her (west)
        c.rect(5, 2, 6, 13, "K")
        c.rect(7, 6, 8, 9, "G")
        c.rect(2, 4, 3, 11, "L")                   # keyboard
        for y in (5, 7, 9):
            c.px(3, y, "G")
    if prop == "phone":
        c.rect(2, 6, 6, 10, "K")
        c.rect(3, 7, 5, 9, "L")
        c.px(7, 8, "G")
    if prop == "papers":
        c.rect(2, 3, 7, 9, "L")
        for y in (5, 7):
            c.rect(3, y, 6, y, "G")
        c.rect(3, 11, 5, 13, "K")                  # pen cup
        c.px(3, 10, "G"); c.px(5, 10, "L")
    return c.out(), None


for part, prop, name in [("top", "phone", "haruna_desk_top"), ("mid", "monitor", "haruna_desk_monitor"),
                         ("mid", "papers", "haruna_desk_papers"), ("bottom", None, "haruna_desk_bottom")]:
    rows, _ = haruna_desk(part, prop)
    im, ly = paint(rows, DESK, name)
    OUT[name] = (im, ly, "")


def hitomi_desk_side(prop=None):
    """U11: straight piece, wood rim on the west (room side), white work surface inside (east)."""
    c = Canvas(16, 16)
    for y in range(16):
        c.px(0, y, "a")
        c.rect(1, y, 5, y, "A")
        c.px(6, y, "a")
        c.rect(7, y, 14, y, "w")
        c.px(15, y, "a")
    c.px(3, 5, "a"); c.px(3, 12, "a")
    if prop == "monitor":                          # screen toward her (east)
        c.rect(9, 2, 10, 13, "K")
        c.rect(7, 6, 8, 9, "G")
        c.rect(12, 4, 13, 11, "L")
        for y in (5, 7, 9):
            c.px(12, y, "G")
    if prop == "phone":
        c.rect(9, 5, 13, 9, "K")
        c.rect(10, 6, 12, 8, "L")
        c.rect(9, 11, 11, 13, "G")                 # pen cup
        c.px(9, 10, "K"); c.px(11, 10, "L")
    return c.out()


def hitomi_desk_curve_u():
    """U10: the rim bends from the west side up toward the top-right corner (joins V9)."""
    c = Canvas(16, 16)
    for y in range(16):
        x0 = max(0, 9 - y)                         # rim slides left as it goes down
        c.px(x0, y, "a")
        c.rect(x0 + 1, y, x0 + 5, y, "A")
        c.px(x0 + 6, y, "a")
        c.rect(x0 + 7, y, 14, y, "w")
        c.px(15, y, "a")
    for y in range(0, 3):
        c.rect(max(0, 9 - y) + 7, y, 15, y, "w")
    c.px(15, 0, "a")
    return c.out()


def hitomi_desk_curve_v(prop=None):
    """V9: the rim runs from the bottom-left corner (joins U10) to the wall on the right; inside is below it."""
    c = Canvas(16, 16)
    for x in range(16):
        y0 = max(1, 9 - x // 2)                    # rim rises toward the wall
        c.px(x, y0, "a")
        c.rect(x, y0 + 1, x, y0 + 5, "A")
        c.px(x, y0 + 6, "a")
        c.rect(x, y0 + 7, x, 15, "w")
    if prop == "printer":
        c.rect(7, 10, 14, 15, "K")
        c.rect(8, 11, 13, 12, "G")
        c.rect(9, 14, 12, 15, "L")
    return c.out()


def gate_open():
    """V13 swung open: only the hinged piece folded against the wall is left."""
    c = Canvas(16, 16)
    for y in range(0, 12):
        c.px(10, y, "a")
        c.rect(11, y, 14, y, "A")
        c.px(15, y, "a")
    c.rect(10, 12, 15, 12, "a")
    return c.out()


pieces = {
    "hitomi_desk_top_end": hitomi_desk_curve_v("printer"),          # V9
    "hitomi_desk_upper": hitomi_desk_curve_u(),                     # U10
    "hitomi_desk_monitor": hitomi_desk_side("monitor"),             # U11
    "hitomi_desk_lower": flip_v(hitomi_desk_curve_u()),             # U12
    "hitomi_desk_gate_closed": flip_v(hitomi_desk_curve_v()),       # V13
    "hitomi_desk_gate_open": gate_open(),                           # V13 while she walks through
    "hitomi_desk_side_phone": hitomi_desk_side("phone"),            # spare straight piece
}
for name, rows in pieces.items():
    im, ly = paint(rows, DESK, name)
    OUT[name] = (im, ly, "")

# =================================================================== office chair (black mesh), top-down
CHAIR = {"K": (1, "000000"), "G": (1, "7C7C7C"), "L": (1, "BCBCBC")}
office_chair = [
    "................",
    ".....GGGGGG.....",
    "....GKKKKKKG....",
    "...GKKGKKGKKG...",
    "...GKKKKKKKKG...",
    "....GGGGGGGG....",
    "...GKKKKKKKKG...",
    "..GKKKKKKKKKKG..",
    "..GKKKKKKKKKKG..",
    "..GKKKKKKKKKKG..",
    "...GKKKKKKKKG...",
    "....GGGKKGGG....",
    "..L....GG....L..",
    "...GGGGGGGGGG...",
    "..L....GG....L..",
    ".......LL.......",
]
OUT["office_chair"] = (*paint(office_chair, CHAIR, "office_chair"), "")

# =================================================================== coffee station (2 x 2 tiles, against the top shelf)
cs = Canvas(32, 32)
# layer 1: grey cabinet
cs.rect(0, 13, 31, 15, "l")                         # counter top
cs.rect(0, 16, 31, 16, "k")
cs.rect(0, 17, 31, 31, "g")
cs.rect(0, 17, 0, 31, "k"); cs.rect(31, 17, 31, 31, "k")
cs.rect(15, 18, 16, 30, "k")                        # two doors
cs.rect(1, 31, 30, 31, "k")
cs.rect(12, 22, 13, 25, "l"); cs.rect(18, 22, 19, 25, "l")   # handles
cs.rect(2, 18, 13, 18, "l"); cs.rect(18, 18, 29, 18, "l")    # door top highlight
# layer 2: white microwave + white electric kettle
cs.rect(1, 3, 20, 13, "W")
cs.rect(1, 3, 20, 3, "M")
cs.rect(1, 13, 20, 13, "M")
cs.rect(3, 5, 13, 11, "K")                          # window
cs.rect(4, 6, 6, 7, "M")                            # glass shine
cs.rect(15, 5, 19, 11, "M")                         # control panel
for y in (6, 8, 10):
    cs.px(16, y, "K"); cs.px(18, y, "K")
cs.rect(23, 6, 29, 13, "W")                         # kettle
cs.rect(24, 5, 28, 5, "W")
cs.rect(25, 4, 27, 4, "K")                          # lid knob
cs.rect(30, 7, 30, 11, "K"); cs.px(29, 7, "K"); cs.px(29, 11, "K")  # handle
cs.rect(22, 8, 22, 9, "K")                          # spout
cs.rect(23, 13, 29, 13, "M")
# layer 3: the little red heart on the microwave, coffee cups on the counter
cs.rows(0, [".RR.RR.", "RRRRRRR", ".RRRRR.", "..RRR..", "...R..."], x0=7)
for x0 in (2, 22):
    cs.rows(12, ["wwww", "wCCw", "wwww"], x0=x0)
    cs.px(x0 + 4, 13, "w")
COFFEE_PAL = {"g": (1, "7C7C7C"), "l": (1, "BCBCBC"), "k": (1, "000000"),
              "W": (2, "FCFCFC"), "K": (2, "000000"), "M": (2, "7C7C7C"),
              "R": (3, "F83800"), "C": (3, "881400"), "w": (3, "FCFCFC")}
OUT["coffee_station"] = (*paint(cs.out(), COFFEE_PAL, "coffee_station"), "2 x 2 tiles, solid")

# =================================================================== power-ups (16 x 16, pop out onto the floor Zelda-style)
coffee_cup = [
    "......W...W.....",
    ".....W...W......",
    "......W...W.....",
    ".....W...W......",
    "................",
    "...KKKKKKKKK....",
    "...KCCCCCCCK....",
    "...KWCCCCCWKKK..",
    "...KWWWWWWWK.K..",
    "...KWWWWWWWK.K..",
    "...KWWWWWWWKKK..",
    "...KWWWWWWWK....",
    "...KWWWWWWWK....",
    "....KWWWWWK.....",
    ".....KKKKK......",
    "................",
]
OUT["item_coffee"] = (*paint(coffee_cup, {"W": (1, "FCFCFC"), "C": (1, "881400"), "K": (1, "000000")}, "coffee"), "")

headphones = [
    "................",
    ".....KKKKKK.....",
    "....KK....KK....",
    "...KK......KK...",
    "..KK........KK..",
    "..K..........K..",
    "..K..........K..",
    ".GGG........GGG.",
    "GKKKG......GKKKG",
    "GKBKG......GKBKG",
    "GKBKG......GKBKG",
    "GKBKG......GKBKG",
    "GKKKG......GKKKG",
    ".GGG........GGG.",
    "................",
    "................",
]
OUT["item_headphones"] = (*paint(headphones, {"K": (1, "000000"), "G": (1, "7C7C7C"), "B": (1, "3CBCFC")}, "hp"), "")

laptop = [
    "................",
    "..GGGGGGGGGGGG..",
    "..GSSSSSSSSSSG..",
    "..GSLSSSSSSSSG..",
    "..GSSSSSSSSSSG..",
    "..GSSSSSSSSSSG..",
    "..GSSSSSSSSSSG..",
    "..GGGGGGGGGGGG..",
    ".GLLLLLLLLLLLLG.",
    ".GLGLGLGLGLGLLG.",
    ".GLLGLGLGLGLGLG.",
    ".GLGLGLGLGLGLLG.",
    ".GLLLLGGGGLLLLG.",
    ".GLLLLGLLGLLLLG.",
    ".GGGGGGGGGGGGGG.",
    "................",
]
OUT["item_laptop"] = (*paint(laptop, {"G": (1, "7C7C7C"), "S": (1, "3CBCFC"), "L": (1, "BCBCBC")}, "laptop"),
                      "drawn on its table")

highlighter = [
    "................",
    "...........KK...",
    "..........KDDK..",
    ".........KDDDDK.",
    "........KNDDDK..",
    ".......KNNNDK...",
    "......KNNNNK....",
    ".....KNNNNK.....",
    "....KNNNNK......",
    "...KNNNNK.......",
    "..KNNNNK........",
    "..KDNNK.........",
    ".KDDKK..........",
    ".KDK............",
    "..K.............",
    "................",
]
OUT["item_highlighter"] = (*paint(highlighter, {"K": (1, "000000"), "N": (1, "B8F818"), "D": (1, "007800")}, "hl"),
                           "drawn on its table")

pizza_box = [
    "................",
    "................",
    ".aaaaaaaaaaaaaa.",
    ".aYYYYYYYYYYYYa.",
    ".aYYYRRRRRRYYYa.",
    ".aYYYRaRRaRYYYa.",
    ".aYYYYRRRRYYYYa.",
    ".aYYYYRaRRYYYYa.",
    ".aYYYYYRRYYYYYa.",
    ".aYYYYYRRYYYYYa.",
    ".aYYYYYYYYYYYYa.",
    ".aYYYYYYYYYYYYa.",
    ".aaaaaaaaaaaaaa.",
    ".aaaaaaaaaaaaaa.",
    "................",
    "................",
]
PBOX = {"Y": (1, "FCE0A8"), "a": (1, "AC7C00"), "R": (1, "F83800")}
OUT["item_pizza_box"] = (*paint(pizza_box, PBOX, "pizza_box"), "sits on the bookshelf; the same box falls")

pz = Canvas(16, 16)
pz.rect(0, 1, 15, 3, "a")                           # open lid behind
pz.rect(1, 2, 14, 2, "Y")
pz.rect(0, 4, 15, 15, "a")
pz.rect(1, 5, 14, 14, "Y")
pz.rows(5, ["...cccccc...", "..cCCCCCCc..", ".cCCPCCCCPc.", ".cCCCCCPCCc.", ".cPCCCCCCCc.",
            ".cCCCPCCCCc.", ".cCCCCCCPCc.", "..cCPCCCCc..", "...cccccc..."], x0=2)
PIZZA = {"Y": (1, "FCE0A8"), "a": (1, "AC7C00"),
         "c": (2, "FCA044"), "C": (2, "F8B800"), "P": (2, "F83800")}
OUT["item_pizza_open"] = (*paint(pz.out(), PIZZA, "pizza_open"), "on the floor; the clouds crowd around it")

# =================================================================== the book (drawn over the seated student)
BOOK = {"W": (1, "FCFCFC"), "L": (1, "BCBCBC"), "K": (1, "000000")}
BOOK_G = {"W": (1, "B8F818"), "L": (1, "58D854"), "K": (1, "000000")}
book_N = ["................"] * 10 + [
    "....WWWWKWWWW...",
    "....WLLWKWLLW...",
    "....WWWWKWWWW...",
] + ["................"] * 3
book_S = ["................"] * 1 + [                   # lies on the table above the student's head
    "....KKKKKKKK....",
    "....KWWWKWWK....",
    "....KWLLKLWK....",
    "....KWWWKWWK....",
    "....KKKKKKKK....",
] + ["................"] * 10
book_W = ["................"] * 9 + [
    "...........WWK..",
    "...........WLK..",
    "...........WLK..",
    "...........WWK..",
] + ["................"] * 3
BOOK_OFFSET = {"N": [0, 0], "S": [0, -6], "W": [0, 0], "E": [0, 0]}
for side, rows in [("N", book_N), ("S", book_S), ("W", book_W), ("E", mirror(book_W))]:
    OUT[f"book_{side}"] = (*paint(rows, BOOK, "book"), "")
    OUT[f"book_{side}_green"] = (*paint(rows, BOOK_G, "bookg"), "")

# =================================================================== speech bubble tail (the bubble box is drawn in code)
tail = [
    "KWWWWWWK",
    ".KWWWWK.",
    "..KWWK..",
    "...KK...",
]
OUT["bubble_tail"] = (*paint(tail, {"W": (1, "FCFCFC"), "K": (1, "000000")}, "tail"), "")

# =================================================================== pack
names = list(OUT)
small = [n for n in names if OUT[n][0].size == (16, 16)]
other = [n for n in names if n not in small]
COLS = 8
H = ((len(small) + COLS - 1) // COLS) * 16
sheet = Image.new("RGBA", (COLS * 16, H + 32), (0, 0, 0, 0))
atlas = {}
for i, n in enumerate(small):
    x, y = (i % COLS) * 16, (i // COLS) * 16
    sheet.paste(OUT[n][0], (x, y))
    atlas[n] = {"x": x, "y": y, "w": 16, "h": 16}
x = 0
for n in other:
    im = OUT[n][0]
    sheet.paste(im, (x, H))
    atlas[n] = {"x": x, "y": H, "w": im.width, "h": im.height}
    x += im.width
for n in names:
    atlas[n]["layers"] = OUT[n][1]
    if OUT[n][2]:
        atlas[n]["note"] = OUT[n][2]
for side in "NSWE":
    atlas[f"book_{side}"]["offset_from_seated"] = BOOK_OFFSET[side]
    atlas[f"book_{side}_green"]["offset_from_seated"] = BOOK_OFFSET[side]
sheet.save("objects_v2_sheet.png")
json.dump({"sheet": "objects_v2_sheet.png", "sprites": atlas}, open("objects_v2_sheet.json", "w"), indent=1)
print("ok:", len(OUT), "object sprites; every layer <= 3 NES colors")
