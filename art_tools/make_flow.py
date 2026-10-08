"""ELSC Game - the whole game, screen by screen, in the order a player sees it (mockups, 256 x 240)."""
import json
import os

exec(open("make_menus.py").read())          # font, HUD helpers, menu screens, sprite loaders

EFF = Image.open("effects_sheet.png").convert("RGBA")
EA = json.load(open("effects_sheet.json"))
TORN = {n: Image.open(f"noise_tornado_stage{n}.png").convert("RGBA") for n in (1, 2, 3)}
TSZ = {1: 32, 2: 48, 3: 64}
FLASH_1 = {"000000": "FCFCFC", "F0D0B0": "000000", "00A844": "F83800"}


def eff(name):
    return sp(EFF, EA["sprites"], name)


def tornado(stage, frame=0):
    s = TSZ[stage]
    return TORN[stage].crop((frame * s, 0, frame * s + s, s))


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


def hud_game(img, stage, secs, frac, bar_col=YELLOW, who="boy"):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SW - 1, HUD_H - 1], fill=rgb(BLACK))
    text(img, f"STAGE {stage}", 10, 14, WHITE)
    img.alpha_composite(sp(STU, SA, f"{who}_down_stand"), (14, 30))
    text(img, who.upper(), 34, 36, GRAY)
    text(img, "TIME", 0, 8, GRAY, center=True)
    text(img, f"{secs // 60}:{secs % 60:02d}", 0, 22, RED if secs <= 10 else WHITE, scale=3, center=True)
    text(img, "STUDY", 172, 14, GRAY)
    d.rectangle([172, 28, 247, 41], fill=rgb(WHITE))
    d.rectangle([174, 30, 245, 39], fill=rgb("503000"))
    fw = int(72 * frac)
    if fw:
        d.rectangle([174, 30, 173 + fw, 39], fill=rgb(bar_col))
    for tx in range(182, 245, 8):
        d.line([(tx, 30), (tx, 39)], fill=rgb("AC7C00" if tx <= 173 + fw else BLACK))
    d.line([(0, HUD_H - 1), (SW - 1, HUD_H - 1)], fill=rgb(DGRAY))


def world(cam):
    img = screen()
    img.alpha_composite(STAGE.crop((cam[0], cam[1], cam[0] + SW, cam[1] + SH - HUD_H)), (0, HUD_H))
    return img


def on_screen(cam, tx, ty):
    return int(tx * 16) - cam[0], int(ty * 16) - cam[1] + HUD_H


def seat(img, cam, chair_tile, side, who="boy", frame="read1"):
    x, y = on_screen(cam, *chair_tile)
    q = SEA[f"{who}_seat_{side}_{frame}"]
    img.alpha_composite(sp(SEAT, SEA, f"{who}_seat_{side}_{frame}"), (x + q["offset_from_chair"][0], y + q["offset_from_chair"][1]))
    return x, y


def stage1_play():
    cam = (48, 96)
    img = world(cam)
    x, y = seat(img, cam, (5.5, 9), "N")                      # T1's GREEN chair
    img.alpha_composite(eff("plus_3"), (x + 3, y - 26))
    img.alpha_composite(tornado(1, 2), (176, 134))
    img.alpha_composite(eff("bubble_ha"), (192, 118))
    hud_game(img, 1, 52, 0.38, bar_col=GOLD)                  # bar flashing while charging
    return img


def stage1_hit():
    cam = (48, 96)
    img = world(cam)
    img.alpha_composite(tornado(1, 4), (150, 124))
    img.alpha_composite(eff("bubble_curse"), (164, 106))
    img.alpha_composite(recolor(sp(STU, SA, "boy_right_stand"), FLASH_1), (120, 138))
    hud_game(img, 1, 31, 0.44)
    return img


def stage2_play():
    cam = (128, 176)                                          # camera stops at the room edge
    img = world(cam)
    x, y = seat(img, cam, (15.5, 18), "N")                    # T7's RED chair
    img.alpha_composite(eff("plus_2"), (x + 3, y - 26))
    img.alpha_composite(tornado(2, 1), (6, 128))              # it noticed you: lunge + bubble burst
    for i, b in enumerate(["bubble_bang", "bubble_huh", "bubble_lol"]):
        img.alpha_composite(eff(b), (10 + i * 16, 104 - i * 6))
    hud_game(img, 2, 40, 0.52, bar_col="FCE0A8")
    return img


def stage3_play():
    cam = (48, 16)
    img = world(cam)
    img.alpha_composite(sp(STU, SA, "boy_right_walk1"), (134, 150))       # running to another table
    img.alpha_composite(tornado(3, 3), (56, 118))
    for i, b in enumerate(["bubble_dots", "bubble_blah"]):
        img.alpha_composite(eff(b), (70 + i * 26, 100 - i * 4))
    hud_game(img, 3, 8, 0.61)
    return img


def over(img_fn, draw):
    img = img_fn()
    draw(img)
    return img


def pause_over(base):
    img = base.copy()
    box(img, 58, 84, 140, 112)
    text(img, "PAUSED", 0, 96, YELLOW, scale=2, center=True)
    for i, item in enumerate(["CONTINUE", "RESTART", "SOUND", "QUIT TO TITLE"]):
        y = 124 + i * 16
        if i == 0:
            text(img, ">", 72, y, YELLOW)
        text(img, item, 84, y, YELLOW if i == 0 else WHITE)
    return img


def times_up_over(base, stage, frac):
    img = base.copy()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 124, SW - 1, 168], fill=rgb(BLACK))
    d.line([(0, 124), (SW - 1, 124)], fill=rgb(WHITE))
    d.line([(0, 168), (SW - 1, 168)], fill=rgb(WHITE))
    text(img, "TIME'S UP!", 0, 136, RED, scale=3, center=True, shadow="A81000")
    hud_game(img, stage, 0, frac)
    return img


FLOW = [
    ("title", title(), "Title screen: Start / Options / Stage Code"),
    ("options", options(), "Options: music and sound FX volume"),
    ("character_select", character_select(), "Character select: boy or girl"),
    ("stage1_intro", stage_intro(1), "Stage 1 intro"),
    ("stage1_play", stage1_play(), "Stage 1: studying on a green chair (+3), bar flashing, small tornado laughing nearby"),
    ("stage1_hit", stage1_hit(), "Stage 1: hit! Knocked back and flashing (color swap)"),
    ("stage1_pause", pause_over(stage1_play()), "Esc: pause menu"),
    ("stage1_times_up", times_up_over(stage1_play(), 1, 0.58), "Stage 1: time's up, everything freezes"),
    ("stage1_results", results(True, 1), "The test: PASSED, on to Stage 2"),
    ("stage2_intro", stage_intro(2), "Stage 2 intro"),
    ("stage2_play", stage2_play(), "Stage 2: red chair (+2). The 3 x 3 tornado noticed you: bubble burst + lunge"),
    ("stage2_results", results(True, 2), "The test: PASSED, on to Stage 3"),
    ("stage3_intro", stage_intro(3), "Stage 3 intro"),
    ("stage3_play", stage3_play(), "Stage 3: 8 seconds left, running from the 4 x 4 tornado to another table"),
    ("stage3_failed", results(False, 3, "COMPUTERSCIENCECLASS"), "Failed Stage 3 (5th time): the stage code appears"),
    ("stage_code", stage_code("COMPUTERSCIENCECL"), "Title > Stage Code: typing it in"),
    ("stage_code_wrong", stage_code("HOMEWORK", wrong=True), "A wrong code"),
    ("course_complete", course_complete(), "Passed Stage 3: YOU PASSED THE COURSE!!!"),
]

os.makedirs("flow", exist_ok=True)
for i, (name, im, cap) in enumerate(FLOW, 1):
    im.resize((SW * 3, SH * 3), Image.NEAREST).save(f"flow/{i:02d}_{name}.png")
json.dump([{"n": i, "file": f"{i:02d}_{n}.png", "caption": c} for i, (n, _, c) in enumerate(FLOW, 1)],
          open("flow/flow.json", "w"), indent=2)
print("ok:", len(FLOW), "screens")
