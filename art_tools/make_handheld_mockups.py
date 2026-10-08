"""ELSC Study Pocket v2 - phone mockups (a tall phone and a shorter phone)."""
import json
import math
exec(open("make_v2_mockups.py").read().split("SCREENS = [")[0])
exec(open("make_handheld.py").read().split('if __name__ == "__main__":')[0])

HS = json.load(open("handheld/handheld_skin.json"))
PARTS = Image.open("handheld/handheld_parts.png").convert("RGBA")


def part(n):
    q = HS["parts"][n]
    return PARTS.crop((q["x"], q["y"], q["x"] + q["w"], q["y"] + q["h"]))


def device(game, height, led="led_green", pressed=(), muted=False, thumb=None, top=None):
    skin = assemble(top or top_piece(), height)
    out = Image.new("RGBA", skin.size, (0, 0, 0, 0))
    s = HS["screen"]
    if game is not None:
        out.alpha_composite(game, (s["x"], s["y"]))
    out.alpha_composite(skin)
    L = HS["status_light"]
    out.alpha_composite(part(led), (L["cx"] - 4, L["cy"] - 4))
    by = height - HS["bottom_height"]
    for n, b in HS["buttons"].items():
        if n in pressed:
            out.alpha_composite(part(b["down"]), (b["cx"] - b["r"] - 2, by + b["cy"] - b["r"] - 2))
    if muted:
        b = HS["buttons"]["sound"]
        out.alpha_composite(part("sound_off_mark"), (b["cx"] - b["r"] - 2, by + b["cy"] - b["r"] - 2))
    if thumb:
        (ax, ay), (tx, ty) = [(x, y + by) for x, y in thumb]
        d = ImageDraw.Draw(out)
        n = int(2 * math.pi * 14)
        for i in range(0, n, 2):
            a = 2 * math.pi * i / n
            d.point((int(ax + 14 * math.cos(a)), int(ay + 14 * math.sin(a))), fill=rgb(WHITE))
        d.ellipse([tx - 10, ty - 10, tx + 10, ty + 10], fill=(240, 208, 176, 170), outline=rgb("503000"))
    if "ok" in pressed and thumb is None:
        b = HS["buttons"]["ok"]
        d = ImageDraw.Draw(out)
        d.ellipse([b["cx"] - 12, by + b["cy"] - 14, b["cx"] + 12, by + b["cy"] + 10], fill=(240, 208, 176, 150),
                  outline=rgb("503000"))
    return out


def phone(dev, label, phone_h):
    s = 2
    big = dev.resize((dev.width * s, dev.height * s), Image.NEAREST)
    pad = 14
    screen_h = phone_h * s
    o = Image.new("RGBA", (big.width + pad * 2, screen_h + pad * 2 + 44), (40, 40, 40, 255))
    d = ImageDraw.Draw(o)
    d.rounded_rectangle([0, 0, big.width + pad * 2 - 1, screen_h + pad * 2 - 1], radius=50, fill=(20, 20, 20, 255),
                        outline=(90, 90, 90, 255), width=4)
    d.rectangle([pad, pad, pad + big.width - 1, pad + screen_h - 1], fill=(0, 0, 0, 255))
    o.alpha_composite(big, (pad, pad + (screen_h - big.height) // 2))
    lab = Image.new("RGBA", (len(label) * 6 + 2, 9), (0, 0, 0, 0))
    text(lab, label, 1, 1, WHITE)
    lab = lab.resize((lab.width * 3, lab.height * 3), Image.NEAREST)
    o.alpha_composite(lab, ((o.width - lab.width) // 2, screen_h + pad * 2 + 10))
    return o


TALL = round(W * 19.5 / 9)          # a modern phone (about 9 : 19.5) -> 581
SHORT = round(W * 16 / 9)           # an older phone (16 : 9) -> 476: shorter than min_height, so it scales down

# game pictures
g_title = screen()
text(g_title, "ELSC", 0, 70, YELLOW, scale=5, center=True, shadow="A81000")
text(g_title, "GAME", 0, 112, WHITE, scale=3, center=True)
text(g_title, "TAP TO PLAY", 0, 170, WHITE, scale=2, center=True)
STAGE = room()
cam = (48, 96)
g_play = world(cam)
g_play.alpha_composite(sp(STU, SA, "boy_right_walk1"), S(cam, 9.4, 13.3))
g_play.alpha_composite(tornado(2, 3), S(cam, 5.2, 13.6))
g_play.alpha_composite(eff("bubble_lol"), S(cam, 5.8, 12.4))
hud_v2(g_play, 2, 3, 27, 0.48)
g_menu = level_select(1)

pad = HS["slide_pad"]
pcx, pcy = pad["x"] + pad["w"] // 2, pad["y"] + pad["h"] // 2 - 4
shots = [
    ("01_loading", device(None, TALL, led="led_red", top=top_piece([("LOADING...", WHITE, 2), ("PLEASE WAIT", DGRAY, 1)], led="red")), "LOADING", TALL),
    ("02_menu_ok", device(g_menu, TALL, pressed=("ok",)), "SLIDE + OK FOR MENUS", TALL),
    ("03_playing", device(g_play, TALL, thumb=((pcx - 8, pcy + 4), (pcx + 14, pcy - 6))), "SLIDE TO MOVE", TALL),
    ("04_short_phone", device(g_play, HS["min_height"], muted=True), "OLDER PHONE", SHORT),
]
os.makedirs("handheld/mockups", exist_ok=True)
imgs = []
for name, dev, label, ph in shots:
    if dev.height > ph:                                  # too tall: scale down to fit the phone's height
        k = ph / dev.height
        dev = dev.resize((round(dev.width * k), ph), Image.NEAREST)
    im = phone(dev, label, ph)
    im.save(f"handheld/mockups/{name}.png")
    imgs.append(im)
Hm = max(i.height for i in imgs)
row = Image.new("RGBA", (sum(i.width for i in imgs) + 30 * 3, Hm), (40, 40, 40, 255))
x = 0
for i in imgs:
    row.alpha_composite(i, (x, (Hm - i.height) // 2))
    x += i.width + 30
row.save("handheld/mockups/handheld_all.png")
row.resize((row.width // 2, row.height // 2), Image.LANCZOS).save("/tmp/claude-0/handheld2_small.png")
print("ok", TALL, SHORT, HS["min_height"])
