"""ELSC Game - phone mockups (portrait) and the Add-to-Home-Screen icons."""
import json
import os

exec(open("make_v2_mockups.py").read().split("SCREENS = [")[0])

PHONE_W, PHONE_H = 512, 1108         # a phone screen (portrait, about 9 : 19.5), the game drawn 2x across its width
SCALE = 1                            # mockups drawn at game scale inside the phone, then enlarged
_cache = {}


def room_c(**kw):
    key = tuple(sorted(kw.items()))
    if key not in _cache:
        _cache[key] = room(**kw)
    return _cache[key]


def in_phone(game_img, extra=None, game_y=110):
    """Put the 256 x 240 game (scaled to the phone's width) into a portrait phone screen."""
    ph = Image.new("RGBA", (PHONE_W, PHONE_H), rgb(BLACK))
    g = game_img.resize((PHONE_W, int(240 * PHONE_W / 256)), Image.NEAREST)
    ph.alpha_composite(g, (0, game_y))
    if extra:
        extra(ph, game_y + g.height)
    return ph


def frame(ph, label):
    """Draw a simple phone body around the screen, enlarged 3x for viewing."""
    s = 1
    big = ph.resize((ph.width * s, ph.height * s), Image.NEAREST)
    pad = 18
    out = Image.new("RGBA", (big.width + pad * 2, big.height + pad * 2 + 40), (40, 40, 40, 255))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, big.width + pad * 2 - 1, big.height + pad * 2 - 1], radius=48, fill=(20, 20, 20, 255),
                        outline=(90, 90, 90, 255), width=4)
    out.alpha_composite(big, (pad, pad))
    lab = Image.new("RGBA", (len(label) * 6 + 2, 9), (0, 0, 0, 0))
    text(lab, label, 1, 1, WHITE)
    lab = lab.resize((lab.width * 3, lab.height * 3), Image.NEAREST)
    out.alpha_composite(lab, ((out.width - lab.width) // 2, big.height + pad * 2 + 8))
    return out


def ring(img, cx, cy, r, color=WHITE):
    """A dotted NES-style ring (every other pixel), so it never hides the game."""
    import math
    d = ImageDraw.Draw(img)
    n = int(2 * math.pi * r)
    for i in range(0, n, 2):
        a = 2 * math.pi * i / n
        d.point((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))), fill=rgb(color))


def stick(img, ax, ay, tx, ty):
    ring(img, ax, ay, 14)
    d = ImageDraw.Draw(img)
    d.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], outline=rgb(WHITE))
    d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=rgb(GRAY))


# ------------------------------------------------------------ 1. tap to play
def tap_to_play():
    g = screen()
    text(g, "ELSC", 0, 70, YELLOW, scale=5, center=True, shadow="A81000")
    text(g, "GAME", 0, 112, WHITE, scale=3, center=True)
    text(g, "TAP TO PLAY", 0, 170, WHITE, scale=2, center=True)
    return in_phone(g, game_y=380)


# ------------------------------------------------------------ 2. playing: thumb in the empty space under the game
def playing():
    global STAGE
    cam = (48, 96)
    STAGE = room_c()
    g = world(cam)
    img_sx, img_sy = S(cam, 9.4, 13.3)
    g.alpha_composite(sp(STU, SA, "boy_right_walk1"), (img_sx, img_sy))
    g.alpha_composite(tornado(2, 3), S(cam, 5.2, 13.6))
    g.alpha_composite(eff("bubble_lol"), S(cam, 5.8, 12.4))
    hud_v2(g, 2, 3, 27, 0.48)

    def extra(ph, y0):
        big = Image.new("RGBA", (256, 300), (0, 0, 0, 0))
        stick(big, 128, 150, 148, 142)                   # thumb slid to the right (and a bit up)
        text(big, "SLIDE ANYWHERE TO MOVE", 0, 40, DGRAY, center=128)
        text(big, "LIFT TO STOP AND SIT", 0, 54, DGRAY, center=128)
        text(big, "TAP THE TOP BAR TO PAUSE", 0, 260, DGRAY, center=128)
        ph.alpha_composite(big.resize((512, 600), Image.NEAREST), (0, y0 + 20))
    return in_phone(g, extra)


# ------------------------------------------------------------ 3. name entry: the letter grid
GRID = ["ABCDEFGH", "IJKLMNOP", "QRSTUVWX", "YZ012345", "6789"]


def letter_grid(typed="MIKE", sel=None, codes=False):
    g = screen()
    text(g, "NEW HIGH SCORE!", 0, 10, GREEN, center=True)
    text(g, "12340", 0, 24, YELLOW, scale=2, center=True)
    box(g, 48, 46, 160, 22)
    for i in range(10):
        x = 60 + i * 14
        if i < len(typed):
            text(g, typed[i], x, 53, YELLOW)
        ImageDraw.Draw(g).line([(x, 62), (x + 4, 62)], fill=rgb(WHITE if i == len(typed) else DGRAY))
    cw, ch, x0, y0 = 28, 22, 16, 76
    for r, row in enumerate(GRID):
        for c, letter in enumerate(row):
            x, y = x0 + c * cw, y0 + r * ch
            on = sel == letter
            box(g, x, y, cw - 4, ch - 4, border=YELLOW if on else DGRAY, fill="503000" if on else BLACK, thick=1)
            text(g, letter, x + (cw - 4) // 2 - 2, y + 5, YELLOW if on else WHITE)
    # bottom row of the grid: SPACE, DEL, OK
    for label, cx, wdt, col in [("SPACE", 16 + 4 * 28, 52, WHITE), ("DEL", 16 + 6 * 28, 52, RED)]:
        box(g, cx, y0 + 4 * ch, wdt, ch - 4, border=DGRAY, fill=BLACK, thick=1)
        text(g, label, cx + 4, y0 + 4 * ch + 5, col)
    box(g, 40, 200, 176, 26, border=GREEN, fill=BLACK, thick=2)
    text(g, "OK - SAVE", 0, 209, GREEN, center=True)
    return in_phone(g, game_y=300)


# ------------------------------------------------------------ 4. a menu: tap what you want
def tap_menu():
    g = level_select(1)
    ImageDraw.Draw(g).rectangle([0, 206, SW - 1, SH - 1], fill=rgb(BLACK))
    text(g, "TAP A LEVEL", 0, 216, GRAY, center=True)

    def extra(ph, y0):
        d = ImageDraw.Draw(ph)
        fx, fy = 300, 110 + 2 * 128                      # a fingertip on LEVEL 2
        d.ellipse([fx - 18, fy - 18, fx + 18, fy + 18], outline=rgb(WHITE), width=3)
    return in_phone(g, extra)


os.makedirs("mobile", exist_ok=True)
shots = [("01_tap_to_play", tap_to_play(), "TAP TO PLAY"), ("02_playing", playing(), "SLIDE ANYWHERE"),
         ("03_tap_menus", tap_menu(), "TAP MENUS"), ("04_name_grid", letter_grid(sel="E"), "TAP LETTERS")]
framed = []
for name, ph, label in shots:
    f = frame(ph, label)
    f.save(f"mobile/{name}.png")
    framed.append(f)
W = sum(f.width for f in framed) + 30 * (len(framed) - 1)
row = Image.new("RGBA", (W, framed[0].height), (40, 40, 40, 255))
x = 0
for f in framed:
    row.alpha_composite(f, (x, 0))
    x += f.width + 30
row.save("mobile/phone_mockups_all.png")

# ------------------------------------------------------------ Add to Home Screen icons
def icon(size):
    base = Image.new("RGBA", (64, 64), rgb(BLACK))
    for ty in range(4):
        for tx in range(4):
            base.alpha_composite(sp(FURN, FA, "carpet_a" if (tx + ty) % 2 == 0 else "carpet_b"), (tx * 16, ty * 16))
    base.alpha_composite(tornado(2, 2), (8, 2))
    base.alpha_composite(sp(STU, SA, "boy_down_stand"), (40, 40))
    band = ImageDraw.Draw(base)
    band.rectangle([0, 46, 39, 63], fill=rgb(BLACK))
    text(base, "ELSC", 4, 51, YELLOW)
    return base.resize((size, size), Image.NEAREST).convert("RGB")


for s in (180, 192, 512):
    icon(s).save(f"mobile/icon-{s}.png")
json.dump({
    "name": "ELSC Game",
    "short_name": "ELSC Game",
    "start_url": "./",
    "display": "fullscreen",
    "orientation": "portrait",
    "background_color": "#000000",
    "theme_color": "#000000",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}]
}, open("mobile/manifest.webmanifest", "w"), indent=2)
print("ok: phone mockups + icons")
