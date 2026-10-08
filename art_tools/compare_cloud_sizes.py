"""Level 3 idea: 5 clouds at 2x2 vs 5 clouds at 4x4, same camera view."""
exec(open("make_flow.py").read())

POS = [(20, 110), (150, 84), (180, 170), (64, 196), (104, 130)]
def view(stage, label, col):
    cam = (48, 96)
    img = world(cam)
    img.alpha_composite(sp(STU, SA, "boy_left_walk1"), (132, 206))
    off = {1: 0, 2: -8, 3: -16}[stage]
    for i, (x, y) in enumerate(POS):
        img.alpha_composite(tornado(stage, i % 6), (x + off, y + off))
    hud_game(img, 5, 41, 0.4, RED)
    text(img, label, 58, 14, col)
    return img
a = view(1, "2X2", GREEN); b = view(3, "4X4", RED)
out = Image.new("RGBA", (SW * 2 + 8, SH), (0, 0, 0, 255))
out.alpha_composite(a, (0, 0)); out.alpha_composite(b, (SW + 8, 0))
out.resize((out.width * 3, out.height * 3), Image.NEAREST).save("level3_5clouds_2x2_vs_4x4.png")
print("ok")
