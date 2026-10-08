"""ELSC Game - art inventory: every sprite on one labeled sheet, plus what's still missing."""
import json
from PIL import Image, ImageDraw

exec(open("make_menus.py").read().split("# ---------------------------------------------------------------- sprites")[0])

BG, PANEL = "303030", "484848"
Z = 3                  # sprite zoom on the sheet
W = 1280
MISSING = [
    ("V1 OK", "WALLS - GRAY PLACEHOLDER STAYS FOR V1 (DECIDED: NO REAL WALL SPRITES FOR NOW)"),
    ("V1 OK", "DESKS - ORANGE PLACEHOLDER STAYS FOR V1 UNLESS WE DECIDE OTHERWISE"),
    ("CODE", "HIT FLASH - COLOR SWAPS DONE IN CODE (COLORS ARE IN EFFECTS_SHEET.JSON)"),
    ("CODE", "STUDY BAR FLASH WHILE CHARGING - DONE IN CODE"),
    ("OPTIONAL", "ENTRANCE DOOR OR DOORMAT AT THE START TILE V2"),
    ("OPTIONAL", "WINDOW ICON FOR THE GAME (32 X 32)"),
    ("LATER", "SOUNDS + MUSIC (NOT ART): MUSIC, TORNADO NOISE, HIT, PASS, FAIL"),
]


def load(png, js):
    return Image.open(png).convert("RGBA"), json.load(open(js))


furn, fj = load("elsc_furniture_sheet.png", "elsc_furniture_sheet.json")
stu, sj = load("students_sheet.png", "students_sheet.json")
seat, tj = load("students_seated_sheet.png", "students_seated_sheet.json")


def crop(sheet, q):
    return sheet.crop((q["x"], q["y"], q["x"] + q["w"], q["y"] + q["h"]))


def group(names, sheet, atlas):
    return [(n, crop(sheet, atlas[n])) for n in names]


FA = fj["sprites"]
sections = [
    ("FLOOR", group(["carpet_a", "carpet_b"], furn, FA)),
    ("TABLES", group(["table_square", "table_long", "table_small"], furn, FA)),
    ("CHAIRS (4 COLORS X 4 SIDES)", group([f"chair_{c}_{s}" for c in ["blue", "white", "green", "red"] for s in "NSWE"], furn, FA)),
    ("BOOKSHELVES (4 BOOK COLORS X 4 FACINGS)", group([f"shelf_{d}_{b}" for d in ["front", "north", "east", "west"]
                                                      for b in ["red", "blue", "yellow", "teal"]] + ["shelf_top"], furn, FA)),
    ("WHITEBOARD", group(["whiteboard"], furn, FA)),
    ("PLACEHOLDERS - NEED PHOTOS", group(["wall_placeholder", "desk_placeholder"], furn, FA)),
]
for stage in (1, 2, 3):
    tj_ = json.load(open(f"noise_tornado_stage{stage}.json"))
    sh = Image.open(f"noise_tornado_stage{stage}.png").convert("RGBA")
    t = tj_["tiles"][0]
    sections.append((f"NOISE TORNADO - STAGE {stage} ({t} X {t} TILES, 6 FRAMES)",
                     [(f"frame {i}", crop(sh, q)) for i, q in enumerate(tj_["frames_xywh"])]))
SA, TA = sj["sprites"], tj["sprites"]
eff, ej = load("effects_sheet.png", "effects_sheet.json")
sections.append(("EFFECTS - NOISE BUBBLES + CHAIR BONUS POP-UPS", group(list(ej["sprites"]), eff, ej["sprites"])))
for who in ("boy", "girl"):
    sections.append((f"{who.upper()} - STAND + WALK (4 DIRECTIONS)",
                     group([f"{who}_{d}_{f}" for d in ["down", "up", "left", "right"] for f in ["stand", "walk1", "walk2"]], stu, SA)))
for who in ("boy", "girl"):
    sections.append((f"{who.upper()} - SEATED / STUDYING",
                     group([f"{who}_seat_{s}_{f}" for s in "NSWE" for f in ["read1", "read2"]], seat, TA)))

# ---- lay out
PAD, LAB = 10, 12
rows_out = []
y = 70
placements = []
for title, items in sections:
    placements.append(("title", title, None, 14, y))
    y += 20
    x = 14
    row_h = 0
    for name, im in items:
        sw, sh_ = im.width * Z, im.height * Z
        cw = max(sw, len(name) * 6 + 4) + PAD
        if x + cw > W - 14:
            x = 14
            y += row_h + PAD
            row_h = 0
        placements.append(("sprite", name, im, x, y))
        x += cw
        row_h = max(row_h, sh_ + LAB)
    y += row_h + 22
missing_y = y
H = missing_y + 40 + len(MISSING) * 16 + 30

sheet = Image.new("RGBA", (W, H), rgb(BG))
d = ImageDraw.Draw(sheet)
count = 0
for kind, name, im, x, y in placements:
    if kind == "title":
        d.rectangle([0, y - 4, W, y + 12], fill=rgb(PANEL))
        text(sheet, name, x, y, "F8D878")
    else:
        big = im.resize((im.width * Z, im.height * Z), Image.NEAREST)
        cw = max(big.width, len(name) * 6)
        # carpet behind each sprite so it's seen as in the game
        bgc = Image.new("RGBA", big.size)
        for ty in range(0, im.height, 16):
            for tx in range(0, im.width, 16):
                ctile = crop(furn, FA["carpet_a" if ((tx + ty) // 16) % 2 == 0 else "carpet_b"])
                bgc.alpha_composite(ctile.resize((16 * Z, 16 * Z), Image.NEAREST), (tx * Z, ty * Z))
        if not name.startswith("carpet"):
            sheet.alpha_composite(bgc, (x, y))
        sheet.alpha_composite(big, (x, y))
        text(sheet, name.replace("_", " "), x, y + big.height + 3, "BCBCBC")
        count += 1
text(sheet, "ELSC GAME - ART INVENTORY", 14, 16, "FCFCFC", scale=3)
text(sheet, f"{count} SPRITES + 12 MENU SCREENS. ALL STRICT NES (3 COLORS PER SPRITE / LAYER)", 14, 48, "BCBCBC")
d.rectangle([0, missing_y - 4, W, missing_y + 12], fill=rgb("881400"))
text(sheet, "STILL MISSING / NOTES", 14, missing_y, "FCFCFC")
for i, (tag, line) in enumerate(MISSING):
    yy = missing_y + 26 + i * 16
    col = {"NEEDED": "F83800", "OPTIONAL": "F8B800", "LATER": "3CBCFC", "V1 OK": "58D854", "CODE": "BCBCBC"}[tag]
    text(sheet, f"({tag})", 14, yy, col)
    text(sheet, line, 110, yy, "FCFCFC")
sheet.save("art_inventory.png")
print("inventory:", count, "sprites", sheet.size)
