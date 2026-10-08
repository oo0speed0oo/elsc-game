"""ELSC Game v2 - mockups of the new room and screens (256 x 240 NES screens, saved at 3x)."""
import os
import re

exec(open("make_flow.py").read())               # screens, font, HUD, sprites, world(), seat(), tornado()

PEO, PA = atlas("people_v2_sheet.png", "people_v2_sheet.json")
OBJ, OA = atlas("objects_v2_sheet.png", "objects_v2_sheet.json")
BASE_ROOM = Image.open("preview_stage_1x.png").convert("RGBA")


def pp(name, scale=1):
    return sp(PEO, PA, name, scale)


def portrait(img, name, x, y, scale=1):
    """Portraits sit on a light-blue photo card so black hair shows on the black screen."""
    s = 32 * scale
    box(img, x - 2, y - 2, s + 4, s + 4, border=WHITE, fill=SKY, thick=2)
    img.alpha_composite(pp(name, scale), (x, y))


def ob(name):
    return sp(OBJ, OA, name)


def carpet(tx, ty):
    return sp(FURN, FA, "carpet_a" if (tx + ty) % 2 == 0 else "carpet_b")


CHAIRS = []
for line in open("/home/claude/elsc-game/docs/GAME_SPEC.md"):
    m = re.match(r"\| \d+ \| \w+ \| \(([\d.]+), ([\d.]+)\) \| ([NSWE]) \| (\w+) \|", line)
    if m:
        CHAIRS.append((float(m[1]), float(m[2]), m[3], m[4]))
assert len(CHAIRS) == 31


def room(gate="closed", hitomi_home=True, haruna="haruna_type1", coffee=True, laptop=True, highlighter=True,
         pizza="shelf", green_chairs=False, headphones_on_floor=False):
    r = BASE_ROOM.copy()
    for (tx, ty) in [(19, 3), (19, 4), (19, 5), (19, 6), (21, 8), (20, 9), (20, 10), (20, 11), (21, 12),
                     (21, 9), (21, 10), (21, 11)]:
        r.alpha_composite(carpet(tx, ty), (tx * 16, ty * 16))
    for ty, n in [(3, "haruna_desk_top"), (4, "haruna_desk_monitor"), (5, "haruna_desk_papers"), (6, "haruna_desk_bottom")]:
        r.alpha_composite(ob(n), (19 * 16, ty * 16))
    for (tx, ty), n in [((21, 8), "hitomi_desk_top_end"), ((20, 9), "hitomi_desk_upper"), ((20, 10), "hitomi_desk_monitor"),
                        ((20, 11), "hitomi_desk_lower"), ((21, 12), f"hitomi_desk_gate_{gate}")]:
        r.alpha_composite(ob(n), (tx * 16, ty * 16))
    r.alpha_composite(ob("office_chair"), (18 * 16, 4 * 16))
    r.alpha_composite(pp(haruna), (18 * 16, 4 * 16 - 4))
    r.alpha_composite(ob("office_chair"), (21 * 16, 10 * 16))
    if hitomi_home:
        r.alpha_composite(pp("hitomi_desk_work1"), (21 * 16, 10 * 16 - 4))
    r.alpha_composite(ob("coffee_station"), (4 * 16, 1 * 16))
    if coffee:
        r.alpha_composite(ob("item_coffee"), (int(4.5 * 16), 3 * 16))
    if laptop:
        r.alpha_composite(ob("item_laptop"), (6 * 16 + 8, 16 * 16 + 8))
    if highlighter:
        r.alpha_composite(ob("item_highlighter"), (15 * 16 + 8, 19 * 16 + 8))
    if pizza == "shelf":
        r.alpha_composite(ob("item_pizza_box"), (18 * 16 + 8, 14 * 16 - 3))
    elif pizza == "floor":
        r.alpha_composite(ob("item_pizza_open"), (int(20.5 * 16), 17 * 16))
    if headphones_on_floor:
        r.alpha_composite(ob("item_headphones"), (17 * 16, 6 * 16))
    if green_chairs:
        for x, y, side, _ in CHAIRS:
            r.alpha_composite(sp(FURN, FA, f"chair_green_{side}"), (int(x * 16), int(y * 16)))
    return r


def bubble(img, lines, x, y, tail_x, color=BLACK, tail="down"):
    w = max(len(s) for s in lines) * 6 + 7
    h = len(lines) * 10 + 5
    box(img, x, y, w, h, border=BLACK, fill=WHITE, thick=1)
    for i, s in enumerate(lines):
        text(img, s, x + 4, y + 3 + i * 10, color)
    t = ob("bubble_tail")
    if tail == "down":
        img.alpha_composite(t, (tail_x - 4, y + h - 1))
    else:                                          # "left": tail pointing left
        img.alpha_composite(t.rotate(-90, expand=True), (x - 3, y + h // 2 - 4))


def hud_v2(img, level, stage, secs, frac, bar_col=YELLOW, time_col=None):
    hud_game(img, stage, secs, frac, bar_col)
    lv_col = {1: GREEN, 2: YELLOW, 3: RED}[level]
    ImageDraw.Draw(img).rectangle([10, 12, 70, 22], fill=rgb(BLACK))
    text(img, f"LV{level}", 10, 14, lv_col)
    text(img, f"STAGE {stage}", 32, 14, WHITE)
    if time_col:
        ImageDraw.Draw(img).rectangle([90, 20, 166, 46], fill=rgb(BLACK))
        text(img, f"{secs // 60}:{secs % 60:02d}", 0, 22, time_col, scale=3, center=True)


def with_room(cam, **kw):
    global STAGE
    STAGE = room(**kw)
    return world(cam)


def S(cam, tx, ty):                                # tile -> screen pixel
    return int(tx * 16) - cam[0], int(ty * 16) - cam[1] + HUD_H


# ------------------------------------------------------------------ in-room moments
def haruna_calls():
    cam = (128, 0)
    img = with_room(cam, haruna="haruna_call1", headphones_on_floor=True)
    x, y = S(cam, 18, 4)
    bubble(img, ["BE QUIET PLEASE,", "PEOPLE ARE STUDYING!"], 70, y - 36, x + 8)
    sx, sy = seat(img, cam, (17, 9), "W", who="girl")
    img.alpha_composite(eff("plus_1"), (sx + 3, sy - 26))
    img.alpha_composite(ob("book_W"), (sx + 1, sy - 6))
    hud_v2(img, 2, 2, 22, 0.40)
    return img


def hitomi_out():
    cam = (128, 64)
    img = with_room(cam, gate="open", hitomi_home=False)
    x, y = S(cam, 13.5, 11.2)
    img.alpha_composite(pp("hitomi_point1"), (x, y))
    bubble(img, ["DID YOU STUDY?!"], x - 40, y - 24, x + 8)
    img.alpha_composite(sp(STU, SA, "boy_left_walk1"), S(cam, 15.2, 11.4))
    hud_v2(img, 2, 3, 29, 0.52)
    return img


def deadline():
    cam = (48, 176)
    img = with_room(cam, laptop=False)
    img.alpha_composite(sp(STU, SA, "boy_left_stand"), S(cam, 8, 16.5))
    box(img, 40, 74, 176, 64, border=WHITE, fill=BLACK)
    img.alpha_composite(ob("item_laptop"), (52, 86))
    text(img, "DEADLINE", 76, 86, YELLOW, scale=2)
    text(img, "EXTENDED!", 76, 104, YELLOW, scale=2)
    text(img, "+10 SEC", 0, 124, WHITE, center=True)
    hud_v2(img, 2, 4, 28, 0.47, time_col=YELLOW)
    return img


def highlighter_on():
    cam = (128, 176)
    img = with_room(cam, highlighter=False, green_chairs=True)
    x, y = seat(img, cam, (15.5, 18), "N")
    img.alpha_composite(ob("book_N_green"), (x, y - 7))
    img.alpha_composite(eff("plus_3"), (x + 3, y - 26))
    img.alpha_composite(tornado(2, 2), S(cam, 9.2, 14.5))
    hud_v2(img, 2, 5, 17, 0.63, bar_col=GOLD)
    return img


def pizza_lure():
    cam = (128, 176)
    img = with_room(cam, pizza="floor")
    x, y = seat(img, cam, (15.5, 13), "N", who="girl")
    img.alpha_composite(ob("book_N"), (x, y - 7))
    img.alpha_composite(eff("plus_1"), (x + 3, y - 26))
    for (tx, ty, f) in [(17.4, 15.6, 1), (19.4, 13.0, 3), (19.6, 18.3, 5)]:
        img.alpha_composite(tornado(3, f), S(cam, tx, ty))
    for i, b in enumerate(["bubble_lol", "bubble_ha", "bubble_dots"]):
        img.alpha_composite(eff(b), S(cam, 17.8 + i * 1.5, 12.6 + (i % 2) * 0.5))
    hud_v2(img, 3, 4, 34, 0.45)
    return img


# ------------------------------------------------------------------ results with Haruna and Hitomi
def results_v2(passed):
    img = screen()
    text(img, "THE TEST", 0, 12, GRAY, scale=2, center=True)
    study_bar(img, 48, 34, 160, 14, 0.66 if passed else 0.42)
    portrait(img, "portrait_haruna_talk", 14, 60, 2)
    bubble(img, ["DID YOU", "PASS?"], 88, 66, 0, tail="left")
    portrait(img, "portrait_hitomi_cheer2" if passed else "portrait_hitomi_sorry1", 178, 60, 2)
    box(img, 8, 136, 240, 96, border=WHITE, fill=BLACK)
    portrait(img, "portrait_hitomi_cheer1" if passed else "portrait_hitomi_sorry2", 20, 150)
    if passed:
        text(img, "YOU PASSED!", 58, 150, GREEN, scale=2, shadow="005800")
        text(img, "ON TO STAGE 3...", 58, 176, GRAY)
        text(img, "SCORE +1660", 58, 200, YELLOW)
    else:
        text(img, "YOU FAILED...", 58, 150, RED, scale=2, shadow="881400")
        text(img, "BACK TO THE TITLE", 58, 176, GRAY)
        text(img, "STAGE CODE: GRAMMAR", 58, 200, YELLOW)
    return img


# ------------------------------------------------------------------ level select, score, high scores
def level_select(sel=1):
    img = screen()
    text(img, "CHOOSE", 0, 18, WHITE, scale=2, center=True)
    text(img, "YOUR LEVEL", 0, 38, YELLOW, scale=2, center=True)
    rows = [("LEVEL 1", "EASY", "3 STAGES - 1 TO 3 CLOUDS", GREEN, 1),
            ("LEVEL 2", "NORMAL", "5 STAGES - 1 TO 5 CLOUDS", YELLOW, 2),
            ("LEVEL 3", "HARD", "5 STAGES - GIANT CLOUDS", RED, 3)]
    for i, (lv, name, desc, col, stage_look) in enumerate(rows):
        y = 70 + i * 44
        box(img, 20, y, 216, 38, border=col if i == sel else DGRAY, thick=3 if i == sel else 2)
        text(img, lv, 32, y + 8, col, scale=2)
        text(img, name, 128, y + 12, WHITE if i == sel else GRAY)
        text(img, desc, 32, y + 26, WHITE if i == sel else GRAY)
        c = tornado(stage_look, 2)
        c = c.resize((20, 20), Image.NEAREST)
        img.alpha_composite(c, (206, y + 8))
        if i == sel:
            text(img, ">", 10, y + 14, YELLOW)
    text(img, "UP / DOWN TO CHOOSE", 0, 212, GRAY, center=True)
    text(img, "ENTER TO START", 0, 224, GRAY, center=True)
    return img


def score_entry():
    img = screen()
    text(img, "LEVEL 2 COMPLETE!", 0, 22, YELLOW, center=True)
    text(img, "YOU SCORED", 0, 44, WHITE, scale=2, center=True)
    text(img, "12340", 0, 70, YELLOW, scale=4, center=True, shadow="A81000")
    portrait(img, "portrait_haruna_smile", 34, 112)
    portrait(img, "portrait_hitomi_cheer2", 190, 112)
    text(img, "NEW HIGH SCORE!", 0, 124, GREEN, center=True)
    text(img, "TYPE YOUR NAME", 0, 156, GRAY, center=True)
    box(img, 58, 168, 140, 26)
    name = "MIKE"
    for i in range(10):
        x = 70 + i * 12
        if i < len(name):
            text(img, name[i], x, 177, YELLOW)
        ImageDraw.Draw(img).line([(x, 187), (x + 4, 187)], fill=rgb(WHITE if i == len(name) else DGRAY))
    text(img, "ENTER = SAVE", 0, 212, GRAY, center=True)
    text(img, "UP TO 10 LETTERS", 0, 224, DGRAY, center=True)
    return img


def high_scores():
    img = screen()
    text(img, "HIGH SCORES", 0, 14, WHITE, scale=2, center=True)
    text(img, "<  LEVEL 2  >", 0, 40, YELLOW, center=True)
    rows = [("MIKE", 12340), ("HARUNA", 11020), ("HITOMI", 9870), ("KENTA", 8450), ("YUKI", 7310),
            ("SORA", 6200), ("AOI", 5560), ("RIKU", 4390), ("MEI", 3120), ("TAKU", 1980)]
    for i, (n, s) in enumerate(rows):
        y = 60 + i * 14
        col = YELLOW if i == 0 else (WHITE if i < 3 else GRAY)
        text(img, f"{i + 1:>2}.", 28, y, col)
        text(img, n, 58, y, col)
        text(img, f"{s:>6}", 170, y, col)
    text(img, "LEFT / RIGHT = LEVEL", 0, 212, GRAY, center=True)
    text(img, "ESC = BACK", 0, 224, GRAY, center=True)
    return img


SCREENS = [
    ("01_level_select", level_select(1), "Choose your level (the old mode select)"),
    ("02_haruna_calls", haruna_calls(), "Haruna calls out, with the headphones she dropped on the floor"),
    ("03_hitomi_out", hitomi_out(), "Hitomi walked out of her desk (gate open) and blocks the way"),
    ("04_deadline_extended", deadline(), "Laptop grabbed: the game pauses, DEADLINE EXTENDED, the timer ticks up +10"),
    ("05_highlighter", highlighter_on(), "Highlighter: every chair turns green and the book blinks green"),
    ("06_pizza_lure", pizza_lure(), "Level 3: the pizza fell behind the shelf and the giant clouds crowd around it"),
    ("07_results_passed", results_v2(True), "The test: Haruna asks, Hitomi cheers YOU PASSED!"),
    ("08_results_failed", results_v2(False), "The test: Hitomi shakes her head, YOU FAILED..."),
    ("09_score_entry", score_entry(), "After the run: your score and your name (up to 10 letters)"),
    ("10_high_scores", high_scores(), "High scores, top 10 per level"),
]
os.makedirs("v2", exist_ok=True)
for name, im, cap in SCREENS:
    im.resize((SW * 3, SH * 3), Image.NEAREST).save(f"v2/{name}.png")
room().resize((384 * 2, 384 * 2), Image.NEAREST).save("v2/00_room_v2.png")
json.dump([{"file": f"{n}.png", "caption": c} for n, _, c in SCREENS], open("v2/screens.json", "w"), indent=1)
print("ok:", len(SCREENS), "v2 screens")
