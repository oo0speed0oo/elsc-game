"""ELSC Game - menu and UI screens, NES style (256 x 240, the real NES screen size).

Uses a hand-made 5x7 pixel font and the approved sprites. Colors come from the NES palette.
Screens: title, character select, stage intro, gameplay HUD, pause, options, stage code,
time's up, results (passed / failed), course complete.
"""
import json
import random
from PIL import Image, ImageDraw

SW, SH = 256, 240
HUD_H = 64                 # Zelda-style HUD strip on top; the 16 x 11 tile play square sits below it
BLACK, WHITE, GRAY, DGRAY = "000000", "FCFCFC", "BCBCBC", "7C7C7C"
YELLOW, GOLD, GREEN, RED, SKY = "F8B800", "F8D878", "00A800", "F83800", "3CBCFC"


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


# ---------------------------------------------------------------- 5 x 7 pixel font
F = {
    "A": ".###.#...##...#######...##...##...#", "B": "####.#...##...#####.#...##...#####.",
    "C": ".#####....#....#....#....#.....####", "D": "####.#...##...##...##...##...#####.",
    "E": "######....#....####.#....#....#####", "F": "######....#....####.#....#....#....",
    "G": ".#####....#....#.####...##...#.####", "H": "#...##...##...#######...##...##...#",
    "I": "#####..#....#....#....#....#..#####", "J": "..###...#....#....#....##..#..##...",
    "K": "#...##..#.#.#..##...#.#..#..#.#...#", "L": "#....#....#....#....#....#....#####",
    "M": "#...###.###.#.##.#.##...##...##...#", "N": "#...###..##.#.##..###...##...##...#",
    "O": ".###.#...##...##...##...##...#.###.", "P": "####.#...##...#####.#....#....#....",
    "Q": ".###.#...##...##...##.#.##..#..##.#", "R": "####.#...##...#####.#.#..#..#.#...#",
    "S": ".#####....#.....###.....#....#####.", "T": "#####..#....#....#....#....#....#..",
    "U": "#...##...##...##...##...##...#.###.", "V": "#...##...##...##...##...#.#.#...#..",
    "W": "#...##...##...##.#.##.#.###.###...#", "X": "#...##...#.#.#...#...#.#.#...##...#",
    "Y": "#...##...#.#.#...#....#....#....#..", "Z": "#####....#...#...#...#...#....#####",
    "0": ".###.#...##..###.#.###..##...#.###.", "1": "..#...##....#....#....#....#...###.",
    "2": ".###.#...#....#...#...#...#...#####", "3": "####.....#....#.###.....#....#####.",
    "4": "...#...##..#.#.#..#.#####...#....#.", "5": "######....####.....#....##...#.###.",
    "6": ".###.#....#....####.#...##...#.###.", "7": "#####....#...#...#...#....#....#...",
    "8": ".###.#...##...#.###.#...##...#.###.", "9": ".###.#...##...#.####....#....#.###.",
    "!": "..#....#....#....#....#.........#..", "?": ".###.#...#....#...#...#.........#..",
    ".": "................................#..", ",": ".........................#...#.....",
    ":": ".......#...................#.......", "'": "..#....#...#.......................",
    "-": "...............###.................", "_": "..............................#####",
    "/": "....#....#...#...#...#...#....#....", ">": "#....##...###..####.###..##...#....",
    "(": "...#...#...#....#....#.....#.....#.", ")": ".#.....#.....#....#....#...#...#...",
    "+": ".......#....#..#####..#....#.......",
    "=": "..........#####.....#####..........", " ": "." * 35,
    ';': ".......#..............#...#........",
    '"': ".#.#..#.#..........................",
    '#': ".#.#.#####.#.#..#.#..#.#.#####.#.#.",
    '@': ".###.#...##.####.#.##.####.....###.",
    '%': "##..###..#...#...#...#...#..###..##",
    '*': ".....#.#.#.###.#####.###.#.#.#.....",
    '&': ".##..#..#.#.#...#...#.#.##..#..##.#",
    '<': "....#...##..###.####..###...##....#",
    '[': ".###..#....#....#....#....#....###.",
    ']': ".###....#....#....#....#....#..###.",
}


def text(img, s, x, y, color=WHITE, scale=1, center=False, shadow=None):
    s = s.upper()
    w = len(s) * 6 * scale - scale
    if center:
        x = (SW - w) // 2 if center is True else center - w // 2
    d = ImageDraw.Draw(img)
    for layer in ([(shadow, scale)] if shadow else []) + [(color, 0)]:
        col, off = layer
        for i, ch in enumerate(s):
            g = F.get(ch, F["?"])
            for gy in range(7):
                for gx in range(5):
                    if g[gy * 5 + gx] == "#":
                        px, py = x + (i * 6 + gx) * scale + off, y + gy * scale + off
                        d.rectangle([px, py, px + scale - 1, py + scale - 1], fill=rgb(col))
    return w


def screen(color=BLACK):
    return Image.new("RGBA", (SW, SH), rgb(color))


def box(img, x, y, w, h, border=WHITE, fill=BLACK, thick=2):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=rgb(border))
    d.rectangle([x + thick, y + thick, x + w - 1 - thick, y + h - 1 - thick], fill=rgb(fill))


def study_bar(img, x, y, w, h, fill_frac, label=True):
    """Fighting-game style bar: white frame, dark inside, yellow fill with segment ticks. No numbers."""
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=rgb(WHITE))
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], fill=rgb("503000"))
    fw = int((w - 4) * fill_frac)
    if fw > 0:
        d.rectangle([x + 2, y + 2, x + 1 + fw, y + h - 3], fill=rgb(YELLOW))
        d.rectangle([x + 2, y + 2, x + 1 + fw, y + 3], fill=rgb(GOLD))          # shine
    for tx in range(x + 2 + 8, x + w - 3, 8):
        d.line([(tx, y + 2), (tx, y + h - 3)], fill=rgb("AC7C00" if tx <= x + 1 + fw else BLACK))


# ---------------------------------------------------------------- sprites
def atlas(png, js):
    return Image.open(png).convert("RGBA"), json.load(open(js))["sprites"]


FURN, FA = atlas("elsc_furniture_sheet.png", "elsc_furniture_sheet.json")
STU, SA = atlas("students_sheet.png", "students_sheet.json")
SEAT, SEA = atlas("students_seated_sheet.png", "students_seated_sheet.json")
CLOUD = Image.open("noise_tornado_stage1.png").convert("RGBA")
STAGE = Image.open("preview_stage_1x.png").convert("RGBA")


def sp(sheet, at, name, scale=1):
    q = at[name]
    im = sheet.crop((q["x"], q["y"], q["x"] + q["w"], q["y"] + q["h"]))
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST) if scale > 1 else im


def cloud(i=0, scale=1):
    im = CLOUD.crop((i * 32, 0, i * 32 + 32, 32))
    return im.resize((32 * scale, 32 * scale), Image.NEAREST) if scale > 1 else im


def carpet_strip(img, y, rows):
    for ty in range(rows):
        for tx in range(SW // 16):
            img.alpha_composite(sp(FURN, FA, "carpet_a" if (tx + ty) % 2 == 0 else "carpet_b"), (tx * 16, y + ty * 16))


def play_area(img, cam_x=48, cam_y=96, extras=True):
    """The 16 x 11 tile play square under the HUD, cut from the real stage."""
    img.alpha_composite(STAGE.crop((cam_x, cam_y, cam_x + SW, cam_y + SH - HUD_H)), (0, HUD_H))
    if extras:
        # boy studying on T1's top chair (tile 5.5, 9), tornado drifting in from the right
        cx, cy = int(5.5 * 16) - cam_x, 9 * 16 - cam_y + HUD_H
        q = SEA["boy_seat_N_read1"]
        img.alpha_composite(sp(SEAT, SEA, "boy_seat_N_read1"), (cx + q["offset_from_chair"][0], cy + q["offset_from_chair"][1]))
        img.alpha_composite(cloud(2), (196, 150))


def hud(img, stage=1, seconds=47, fill=0.62):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SW - 1, HUD_H - 1], fill=rgb(BLACK))
    text(img, f"STAGE {stage}", 10, 14, WHITE)
    img.alpha_composite(sp(STU, SA, "boy_down_stand"), (14, 30))
    text(img, "BOY", 34, 36, GRAY)
    t = f"{seconds // 60}:{seconds % 60:02d}"
    text(img, "TIME", 0, 8, GRAY, center=True)
    text(img, t, 0, 22, RED if seconds <= 10 else WHITE, scale=3, center=True)
    text(img, "STUDY", 172, 14, GRAY)
    study_bar(img, 172, 28, 76, 14, fill)
    d.line([(0, HUD_H - 1), (SW - 1, HUD_H - 1)], fill=rgb(DGRAY))


# ---------------------------------------------------------------- the screens
def title():
    img = screen()
    text(img, "ELSC", 0, 18, YELLOW, scale=5, center=True, shadow="A81000")
    text(img, "GAME", 0, 62, WHITE, scale=2, center=True)
    text(img, "BEAT THE NOISE. PASS THE TEST.", 0, 88, SKY, center=True)
    carpet_strip(img, 104, 3)
    img.alpha_composite(sp(FURN, FA, "chair_green_N"), (72, 104))
    img.alpha_composite(sp(SEAT, SEA, "boy_seat_N_read1"), (72, 97))
    img.alpha_composite(sp(FURN, FA, "table_square"), (64, 120))
    img.alpha_composite(sp(FURN, FA, "chair_blue_W"), (48, 128))
    img.alpha_composite(sp(SEAT, SEA, "girl_seat_W_read1"), (49, 122))
    img.alpha_composite(cloud(3), (170, 108))
    for i, item in enumerate(["START", "OPTIONS", "STAGE CODE"]):
        y = 166 + i * 16
        if i == 0:
            text(img, ">", 82, y, YELLOW)
        text(img, item, 96, y, YELLOW if i == 0 else WHITE)
    text(img, "(C) 2026 ELSC", 0, 222, DGRAY, center=True)
    return img


def character_select():
    img = screen()
    text(img, "CHOOSE YOUR", 0, 20, WHITE, scale=2, center=True)
    text(img, "STUDENT", 0, 40, YELLOW, scale=2, center=True)
    for i, (who, col) in enumerate([("boy", YELLOW), ("girl", WHITE)]):
        x = 40 + i * 96
        box(img, x, 70, 80, 100, border=col, fill=SKY, thick=3 if i == 0 else 2)
        img.alpha_composite(sp(STU, SA, f"{who}_down_stand", 4), (x + 8, 88))
        text(img, who.upper(), 0, 176, col, scale=2, center=x + 40)
    text(img, ">", 26, 116, YELLOW, scale=2)
    text(img, "LEFT / RIGHT TO CHOOSE", 0, 206, GRAY, center=True)
    text(img, "ENTER TO START", 0, 220, GRAY, center=True)
    return img


def stage_intro(n=1):
    img = screen()
    text(img, f"STAGE {n}", 0, 60, WHITE, scale=4, center=True)
    text(img, "READY,", 0, 112, GRAY, scale=2, center=True)
    text(img, "SET,", 0, 132, GRAY, scale=2, center=True)
    text(img, "STUDY!", 0, 156, YELLOW, scale=3, center=True, shadow="A81000")
    text(img, "PASS MARK: ???", 0, 206, DGRAY, center=True)
    return img


def gameplay():
    img = screen()
    play_area(img)
    hud(img)
    return img


def pause():
    img = gameplay()
    box(img, 58, 84, 140, 112)
    text(img, "PAUSED", 0, 96, YELLOW, scale=2, center=True)
    for i, item in enumerate(["CONTINUE", "RESTART", "SOUND", "QUIT TO TITLE"]):
        y = 124 + i * 16
        if i == 0:
            text(img, ">", 72, y, YELLOW)
        text(img, item, 84, y, YELLOW if i == 0 else WHITE)
    return img


def options():
    img = screen()
    text(img, "OPTIONS", 0, 30, WHITE, scale=2, center=True)
    d = ImageDraw.Draw(img)
    for i, (label, val) in enumerate([("MUSIC", 7), ("SOUND FX", 5)]):
        y = 84 + i * 36
        if i == 0:
            text(img, ">", 18, y, YELLOW)
        text(img, label, 30, y, YELLOW if i == 0 else WHITE)
        for b in range(10):
            bx = 110 + b * 10
            d.rectangle([bx, y - 1, bx + 7, y + 7], fill=rgb(YELLOW if b < val else DGRAY))
        text(img, str(val), 216, y, WHITE)
    text(img, "BACK", 30, 164, WHITE)
    text(img, "UP / DOWN TO SELECT", 0, 206, GRAY, center=True)
    text(img, "LEFT / RIGHT TO CHANGE", 0, 220, GRAY, center=True)
    return img


def stage_code(typed="MATHCLAS", wrong=False):
    img = screen()
    text(img, "STAGE CODE", 0, 40, WHITE, scale=2, center=True)
    text(img, "TYPE YOUR CODE", 0, 70, GRAY, center=True)
    box(img, 24, 92, 208, 34)
    shown = (typed + "_")[:24]
    text(img, shown, 36, 105, YELLOW)
    if wrong:
        text(img, "WRONG CODE!", 0, 142, RED, scale=2, center=True)
    text(img, "ENTER = GO", 0, 196, GRAY, center=True)
    text(img, "ESC = BACK", 0, 210, GRAY, center=True)
    return img


def times_up():
    img = gameplay()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 124, SW - 1, 168], fill=rgb(BLACK))
    d.line([(0, 124), (SW - 1, 124)], fill=rgb(WHITE))
    d.line([(0, 168), (SW - 1, 168)], fill=rgb(WHITE))
    text(img, "TIME'S UP!", 0, 136, RED, scale=3, center=True, shadow="A81000")
    hud(img, seconds=0)
    return img


def results(passed=True, stage=1, code=None):
    img = screen()
    text(img, "THE TEST", 0, 26, GRAY, scale=2, center=True)
    text(img, "YOUR STUDY", 0, 62, WHITE, center=True)
    study_bar(img, 48, 76, 160, 18, 0.64 if passed else 0.41)
    text(img, "DID YOU PASS?", 0, 110, WHITE, scale=2, center=True)
    if passed:
        text(img, "PASSED!", 0, 140, GREEN, scale=4, center=True, shadow="005800")
        text(img, f"ON TO STAGE {stage + 1}...", 0, 196, GRAY, center=True)
    else:
        text(img, "FAILED...", 0, 140, RED, scale=3, center=True, shadow="881400")
        if code:
            text(img, "STAGE CODE:", 0, 184, GRAY, center=True)
            text(img, code, 0, 198, YELLOW, center=True)
        text(img, "BACK TO THE TITLE", 0, 220, DGRAY, center=True)
    return img


def course_complete():
    img = screen()
    r = random.Random(4)
    d = ImageDraw.Draw(img)
    for _ in range(90):                                   # confetti
        x, y = r.randint(0, SW - 3), r.randint(0, SH - 3)
        d.rectangle([x, y, x + 1, y + 1], fill=rgb(r.choice([YELLOW, SKY, GREEN, RED, "F878F8", WHITE])))
    box(img, 20, 30, 216, 84, border=YELLOW)
    text(img, "YOU PASSED", 0, 46, WHITE, scale=3, center=True)
    text(img, "THE COURSE!!!", 0, 80, YELLOW, scale=2, center=True, shadow="A81000")
    carpet_strip(img, 124, 5)
    img.alpha_composite(sp(STU, SA, "boy_down_stand", 4), (60, 132))
    img.alpha_composite(sp(STU, SA, "girl_down_stand", 4), (132, 132))
    text(img, "PRESS ENTER", 0, 210, WHITE, center=True)
    return img


SCREENS = [
    ("01_title", title()),
    ("02_character_select", character_select()),
    ("03_stage_intro", stage_intro(1)),
    ("04_gameplay_hud", gameplay()),
    ("05_pause", pause()),
    ("06_options", options()),
    ("07_stage_code", stage_code("COMPUTERSCIENCECL")),
    ("08_stage_code_wrong", stage_code("HOMEWORK", wrong=True)),
    ("09_times_up", times_up()),
    ("10_results_passed", results(True, 1)),
    ("11_results_failed_code", results(False, 2, "MATHCLASS")),
    ("12_course_complete", course_complete()),
]

import os
os.makedirs("menus", exist_ok=True)
for name, im in SCREENS:
    im.save(f"menus/{name}.png")                                              # real NES size
    im.resize((SW * 3, SH * 3), Image.NEAREST).save(f"menus/{name}_3x.png")   # monitor size

# overview board: 3 across, 2x zoom, with labels
Z, GAP, LAB = 2, 16, 18
cols, rows = 3, (len(SCREENS) + 2) // 3
board = Image.new("RGBA", (cols * SW * Z + (cols + 1) * GAP, rows * (SH * Z + LAB) + (rows + 1) * GAP), rgb("383838"))
for i, (name, im) in enumerate(SCREENS):
    cx, cy = i % cols, i // cols
    x, y = GAP + cx * (SW * Z + GAP), GAP + cy * (SH * Z + LAB + GAP)
    lab = Image.new("RGBA", (SW, 9), (0, 0, 0, 0))
    text(lab, name[3:].replace("_", " "), 0, 1, WHITE)
    board.alpha_composite(lab.resize((SW * 2, 18), Image.NEAREST), (x, y))
    board.alpha_composite(im.resize((SW * Z, SH * Z), Image.NEAREST), (x, y + LAB))
board.save("menus/all_screens_board.png")
print("ok:", len(SCREENS), "screens")
