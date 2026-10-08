"""ELSC Game - effects: noise bubbles, the RPG-style "+" pop-up, plus previews of the
flashing study bar and the Zelda-style hit flash (those two are done in CODE, not sprites).

Sprites (strict NES: 3 colors each):
  bubble_*   speech bubbles that pop out of the Noise Tornado: white, black, red
  plus_1/2/3 the RPG-style "+1 / +2 / +3" that pops over the student while studying (chair bonus)
"""
import json
import math
from PIL import Image, ImageDraw

WHITE, BLACK, RED = "FCFCFC", "000000", "F83800"
GREEN, LGREEN = "00A800", "58D854"


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


# ---------------------------------------------------------------- tiny 3 x 5 font for bubbles
TINY = {
    "?": ["###", "..#", ".##", "...", ".#."], "!": [".#.", ".#.", ".#.", "...", ".#."],
    "#": ["#.#", "###", "#.#", "###", "#.#"], "@": [".#.", "#.#", "###", "#..", ".##"],
    "%": ["#.#", "..#", ".#.", "#..", "#.#"], "~": ["...", ".#.", "#.#", "..#", "..."],
    ".": ["...", "...", "...", "...", ".#."], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "L": ["#..", "#..", "#..", "#..", "###"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "N": ["#.#", "###", "###", "###", "#.#"],
    "*": ["#.#", ".#.", "###", ".#.", "#.#"],
    "NOTE": ["..##", "..#.", "..#.", "###.", "##.."],
}
BUBBLES = {
    "bubble_huh":   (["?", "!"], BLACK),
    "bubble_bang":  (["!", "!"], RED),
    "bubble_curse": (["#", "@", "%", "!"], RED),
    "bubble_music": (["NOTE"], BLACK),
    "bubble_dots":  ([".", ".", ".", "?"], BLACK),
    "bubble_ha":    (["H", "A", "H", "A"], BLACK),
    "bubble_lol":   (["L", "O", "L"], BLACK),
    "bubble_blah":  (["*", "~", "*"], BLACK),
}


def bubble(chars, text_color):
    glyphs = [TINY[c] for c in chars]
    tw = sum(len(g[0]) for g in glyphs) + (len(glyphs) - 1)
    w, h = tw + 6, 11
    H = h + 3                                      # + tail
    im = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=3, fill=rgb(WHITE), outline=rgb(BLACK))
    for i, p in enumerate([(2, h - 1), (3, h - 1), (2, h), (3, h), (2, h + 1), (1, h + 2)]):
        im.putpixel(p, rgb(WHITE if (i < 2 or p == (3, h)) else BLACK))
    im.putpixel((1, h), rgb(BLACK)); im.putpixel((4, h - 1), rgb(BLACK)); im.putpixel((3, h + 1), rgb(BLACK))
    x = 3
    for g in glyphs:
        for gy, row in enumerate(g):
            for gx, ch in enumerate(row):
                if ch == "#":
                    im.putpixel((x + gx, 3 + gy), rgb(text_color))
        x += len(g[0]) + 1
    return im


# ---------------------------------------------------------------- RPG "+1 / +2 / +3" pop-ups
PLUS_GLYPH = ["..#..", "..#..", "#####", "..#..", "..#.."]
DIGITS = {
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["##.", "..#", ".#.", "#..", "###"],
    "3": ["##.", "..#", ".#.", "..#", "##."],
}
POP_COLORS = {"1": "FCFCFC", "2": "F83800", "3": "58D854"}   # white, red, green: like the chair colors


def popup(n):
    """'+n' with a 1-pixel black outline so it reads on the carpet (2 colors)."""
    inner = [PLUS_GLYPH[y] + "." + DIGITS[n][y] for y in range(5)]
    w, h = len(inner[0]) + 2, 7
    fill = [[False] * w for _ in range(h)]
    for y, row in enumerate(inner):
        for x, ch in enumerate(row):
            if ch == "#":
                fill[y + 1][x + 1] = True
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            if fill[y][x]:
                im.putpixel((x, y), rgb(POP_COLORS[n]))
            elif any(0 <= y + dy < h and 0 <= x + dx < w and fill[y + dy][x + dx]
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                im.putpixel((x, y), rgb(BLACK))
    return im


def grid_img(rows, pal):
    im = Image.new("RGBA", (len(rows[0]), len(rows)), (0, 0, 0, 0))
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != ".":
                im.putpixel((x, y), rgb(pal[c]))
    return im


sprites = {n: bubble(c, col) for n, (c, col) in BUBBLES.items()}
for n in ("1", "2", "3"):
    sprites[f"plus_{n}"] = popup(n)
for n, im in sprites.items():
    a = [im.getpixel((x, y))[:3] for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3]]
    assert len(set(a)) <= 3, (n, set(a))

# pack into one sheet (one row per kind)
sheet_w = max(sum(sprites[n].width + 2 for n in BUBBLES), 40)
sheet = Image.new("RGBA", (sheet_w, 14 + 2 + 9), (0, 0, 0, 0))
atlas, x = {}, 0
for n in BUBBLES:
    im = sprites[n]
    sheet.paste(im, (x, 0), im)
    atlas[n] = {"x": x, "y": 0, "w": im.width, "h": im.height}
    x += im.width + 2
x = 0
for n in ("plus_1", "plus_2", "plus_3"):
    im = sprites[n]
    sheet.paste(im, (x, 16), im)
    atlas[n] = {"x": x, "y": 16, "w": im.width, "h": im.height}
    x += im.width + 2
sheet.save("effects_sheet.png")

HIT_FLASH = {   # color swaps cycled in code for 1 second after a hit (every 3 frames at 60 fps)
    "note": "Zelda-style hit flash, done in code: redraw the student sprite with its 3 colors swapped. "
            "Cycle normal -> flash_1 -> flash_2 -> normal ... for the 1 second of invincibility.",
    "normal": {"dark": "000000", "skin": "F0D0B0", "blazer": "(character's blazer)"},
    "flash_1": {"dark": "FCFCFC", "skin": "000000", "blazer": "F83800"},
    "flash_2": {"dark": "F83800", "skin": "FCFCFC", "blazer": "0058F8"},
    "switch_every_frames": 3,
}
STUDY_BAR_FLASH = {
    "note": "While the student is charging, the filled part of the study bar pulses (done in code).",
    "fill_colors_cycle": ["F8B800", "F8D878", "FCE0A8", "F8D878"], "switch_every_frames": 4,
}
PLUS_POPUP = {
    "note": "RPG-style '+1 / +2 / +3' over the student's head: once per second while charging, "
            "showing how much that second added. Use plus_3 for +3, plus_2 for +2, plus_1 for +1.",
    "motion": "appear, rise 12 px over 0.6 s with a 2 px bounce at the start, blink for 0.2 s, then gone",
    "start_offset_from_student": [3, -14],
}
CHAIR_BONUS = {
    "note": "Charging is counted in points. 1 point = 5% of the study bar (so +1 per second = the old 5% per second).",
    "base_points_per_second": 1,
    "bonus_points_per_second": {"green": 3, "red": 2, "white": 1, "blue": 1},
    "bonus_lasts_seconds": 2,
    "bonus_resets_only_at_a_different_table": True,
    "rule": "When you sit at a chair, you get that chair's bonus rate for the first 2 seconds, then +1 per second. "
            "The bonus only comes back when you sit at a DIFFERENT table than the one you last got a bonus from. "
            "Moving to another chair at the same table gives +1 only.",
}
BUBBLE_RULES = {
    "note": "Noise bubbles pop out of the top of the Noise Tornado.",
    "every_seconds": 0.7, "burst_on_lunge": 3,
    "motion": "float up 8 px over 0.6 s, blink twice, disappear. Pick a random bubble each time.",
}
json.dump({"sheet": "effects_sheet.png", "sprites": atlas, "hit_flash": HIT_FLASH, "study_bar_flash": STUDY_BAR_FLASH,
           "plus_popup": PLUS_POPUP, "chair_bonus": CHAIR_BONUS, "noise_bubbles": BUBBLE_RULES}, open("effects_sheet.json", "w"), indent=2)

# ---------------------------------------------------------------- previews
exec(open("make_menus.py").read().split("# ---------------------------------------------------------------- the screens")[0])


def bar(img, x, y, w, h, frac, fill_col):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=rgb(WHITE))
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], fill=rgb("503000"))
    fw = int((w - 4) * frac)
    if fw > 0:
        d.rectangle([x + 2, y + 2, x + 1 + fw, y + h - 3], fill=rgb(fill_col))
    for tx in range(x + 10, x + w - 3, 8):
        d.line([(tx, y + 2), (tx, y + h - 3)], fill=rgb("AC7C00" if tx <= x + 1 + fw else BLACK))


def hud2(img, secs, frac, charging, t):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SW - 1, HUD_H - 1], fill=rgb(BLACK))
    text(img, "STAGE 1", 10, 14, WHITE)
    img.alpha_composite(sp(STU, SA, "boy_down_stand"), (14, 30))
    text(img, "BOY", 34, 36, GRAY)
    text(img, "TIME", 0, 8, GRAY, center=True)
    text(img, f"0:{secs:02d}", 0, 22, WHITE, scale=3, center=True)
    text(img, "STUDY", 172, 14, GRAY)
    col = STUDY_BAR_FLASH["fill_colors_cycle"][(t // 1) % 4] if charging else YELLOW
    bar(img, 172, 28, 76, 14, frac, col)
    d.line([(0, HUD_H - 1), (SW - 1, HUD_H - 1)], fill=rgb(DGRAY))


def recolor(im, mapping):
    out = im.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = px[x, y]
            if c[3]:
                h = "%02X%02X%02X" % c[:3]
                if h in mapping:
                    px[x, y] = rgb(mapping[h])
    return out


CAM = (48, 96)
chair = (int(5.5 * 16) - CAM[0], 9 * 16 - CAM[1] + HUD_H)     # T1's top chair on screen
bubble_names = list(BUBBLES)
frames = []
N = 60
for t in range(N):                                             # 10 fps, 6 seconds
    img = screen()
    img.alpha_composite(STAGE.crop((CAM[0], CAM[1], CAM[0] + SW, CAM[1] + SH - HUD_H)), (0, HUD_H))
    # the tornado drifts around on the right, popping noise bubbles
    cx = 170 + int(18 * math.sin(t / 12))
    cy = 120 + int(10 * math.cos(t / 9))
    img.alpha_composite(cloud(t % 6), (cx, cy))
    for k in range(4):
        born = k * 7 + (t // 28) * 28
        age = t - born
        if 0 <= age < 8 and not (age >= 6 and age % 2):
            b = sprites[bubble_names[(born // 7 + k) % len(bubble_names)]]
            img.alpha_composite(b, (cx + 8 + (k * 9) % 20, cy - 10 - age))
    # the boy studies; "+" pops once per second
    r = "read1" if (t // 5) % 2 == 0 else "read2"
    q = SEA[f"boy_seat_N_{r}"]
    img.alpha_composite(sp(SEAT, SEA, f"boy_seat_N_{r}"), (chair[0] + q["offset_from_chair"][0], chair[1] + q["offset_from_chair"][1]))
    sec, age = t // 10, t % 10
    pts = 3 if sec < 2 else 1                                   # green chair: +3 for 2 seconds, then +1
    pop = sprites[f"plus_{pts}"]
    px_, py_ = chair[0] + 3, chair[1] - 21
    if age < 7:
        bounce = [0, -2, -1, 0, 0, 0, 0][age]
        img.alpha_composite(pop, (px_, py_ - age * 2 + bounce))
    elif age % 2 == 0:
        img.alpha_composite(pop, (px_, py_ - 13))
    total = 0.30 + 0.05 * (min(t, 20) / 10 * 3 + max(0, t - 20) / 10)
    hud2(img, 47 - t // 10, min(total, 1.0), True, t)
    frames.append(img.resize((SW * 3, SH * 3), Image.NEAREST).convert("RGB"))
frames[0].save("effects_charging_preview.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)

# hit flash preview: the boy gets hit, knocked back, and flashes (color swaps)
base = sp(STU, SA, "boy_right_stand")
pal_n = {"000000": "000000", "F0D0B0": "F0D0B0", "00A844": "00A844"}
flash = [pal_n,
         {"000000": HIT_FLASH["flash_1"]["dark"], "F0D0B0": HIT_FLASH["flash_1"]["skin"], "00A844": HIT_FLASH["flash_1"]["blazer"]},
         {"000000": HIT_FLASH["flash_2"]["dark"], "F0D0B0": HIT_FLASH["flash_2"]["skin"], "00A844": HIT_FLASH["flash_2"]["blazer"]}]
hf = []
for t in range(40):
    img = Image.new("RGBA", (128, 48))
    for tx in range(8):
        for ty in range(3):
            img.alpha_composite(sp(FURN, FA, "carpet_a" if (tx + ty) % 2 == 0 else "carpet_b"), (tx * 16, ty * 16))
    img.alpha_composite(cloud(t % 6), (84, 8))
    if t < 8:
        x = 40 + t * 3                                  # walks into the cloud
        img.alpha_composite(sp(STU, SA, f"boy_right_{'walk1' if t % 2 else 'walk2'}"), (x, 16))
    else:
        k = t - 8
        x = 64 - min(k, 2) * 16                          # knocked back 2 tiles
        c = flash[(k // 1) % 3] if k < 10 else pal_n     # 1 second of flashing
        img.alpha_composite(recolor(sp(STU, SA, "boy_right_stand"), c), (x, 16))
    hf.append(img.resize((128 * 5, 48 * 5), Image.NEAREST).convert("RGB"))
hf[0].save("effects_hitflash_preview.gif", save_all=True, append_images=hf[1:], duration=100, loop=0)

# close-up of the effect sprites
big = Image.new("RGBA", (sheet.width * 6, sheet.height * 6), (90, 90, 90, 255))
big.alpha_composite(sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST))
big.save("effects_sheet_6x.png")
print("ok:", len(sprites), "effect sprites, each <= 3 NES colors")
