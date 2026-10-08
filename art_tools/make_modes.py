"""ELSC Game - difficulty modes: the mode select screen and what Normal / Hard look like in play."""
exec(open("make_flow.py").read())            # screens, HUD, sprites (also re-renders the flow folder)

MODES = [("EASY", "1 NOISE CLOUD", GREEN), ("NORMAL", "2 NOISE CLOUDS", YELLOW), ("HARD", "3 NOISE CLOUDS", RED)]


def mode_select(sel=1):
    img = screen()
    text(img, "CHOOSE", 0, 22, WHITE, scale=2, center=True)
    text(img, "YOUR MODE", 0, 42, YELLOW, scale=2, center=True)
    for i, (name, desc, col) in enumerate(MODES):
        y = 76 + i * 44
        box(img, 32, y, 192, 38, border=col if i == sel else DGRAY, thick=3 if i == sel else 2)
        text(img, name, 44, y + 8, col, scale=2)
        text(img, desc, 44, y + 26, WHITE if i == sel else GRAY)
        for k in range(i + 1):                                 # little clouds show how many
            img.alpha_composite(tornado(1, (k * 2) % 6).resize((20, 20), Image.NEAREST), (196 - k * 18, y + 9))
        if i == sel:
            text(img, ">", 20, y + 14, YELLOW)
    text(img, "UP / DOWN TO CHOOSE", 0, 212, GRAY, center=True)
    text(img, "ENTER TO START", 0, 224, GRAY, center=True)
    return img


def hud_mode(img, stage, secs, frac, mode, col, bar_col=YELLOW):
    hud_game(img, stage, secs, frac, bar_col)
    text(img, mode, 58, 14, col)


def stage_intro_mode(n, mode, col):
    img = stage_intro(n)
    text(img, f"{mode} MODE", 0, 34, col, scale=1, center=True)
    return img


def normal_stage1():
    cam = (48, 96)
    img = world(cam)
    x, y = seat(img, cam, (5.5, 9), "N")
    img.alpha_composite(eff("plus_3"), (x + 3, y - 26))
    img.alpha_composite(tornado(1, 2), (176, 134))
    img.alpha_composite(eff("bubble_ha"), (192, 118))
    img.alpha_composite(tornado(1, 5), (104, 190))              # cloud number 2
    img.alpha_composite(eff("bubble_huh"), (118, 174))
    hud_mode(img, 1, 50, 0.36, "NORMAL", YELLOW, bar_col=GOLD)
    return img


def hard_stage2():
    cam = (48, 96)
    img = world(cam)
    img.alpha_composite(sp(STU, SA, "boy_left_walk1"), (120, 150))
    img.alpha_composite(tornado(2, 1), (18, 120))
    img.alpha_composite(tornado(2, 3), (172, 92))
    img.alpha_composite(tornado(2, 5), (150, 180))
    for (b, x, y) in [("bubble_bang", 30, 104), ("bubble_curse", 186, 76), ("bubble_lol", 166, 164)]:
        img.alpha_composite(eff(b), (x, y))
    hud_mode(img, 2, 33, 0.47, "HARD", RED)
    return img


OUT = [
    ("mode_select", mode_select(1)),
    ("stage1_intro_normal", stage_intro_mode(1, "NORMAL", YELLOW)),
    ("stage1_play_normal", normal_stage1()),
    ("stage2_play_hard", hard_stage2()),
]
os.makedirs("modes", exist_ok=True)
for name, im in OUT:
    im.resize((SW * 3, SH * 3), Image.NEAREST).save(f"modes/{name}.png")
print("ok:", len(OUT), "mode screens")
