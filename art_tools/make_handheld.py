"""ELSC Game - the 'ELSC Study Pocket' v2: an original handheld shell for the phone version.

Pencil-yellow body, equal round corners, a thin black bezel so the game screen is as big as the
phone allows, a slide pad on the left, a big OK and a BACK button on the right, small PAUSE and
SOUND buttons, a status light and a dot speaker. Our own design (not a copy of any real console).

It comes in three pieces so it fits every phone:
  top    (268 x 280): bezel, status light, labels and the 256 x 240 screen hole at (6, 22)
  filler (268 x 1)  : plain body, repeated to fill any extra height on tall phones
  bottom (268 x 212): slide pad and buttons
"""
import json
import math
import os

exec(open("make_menus.py").read().split("# ---------------------------------------------------------------- sprites")[0])

W = 268
TOP_H, BOT_H = 280, 212
SCREEN = (6, 22, 256, 240)
BODY, BODY_HI, BODY_SH, BODY_DK = "F8B800", "F8D878", "AC7C00", "503000"

# bottom-part layout (coordinates inside the bottom piece)
PAD = (12, 14, 128, 128)                   # x, y, w, h
BTN = {                                    # name: (cx, cy, r, colors main/dark/light, label)
    "ok":    (212, 50, 24, ("00A800", "005800", "58D854"), "OK"),
    "back":  (194, 112, 15, ("7C7C7C", "000000", "BCBCBC"), "BACK"),
    "pause": (104, 172, 11, ("F83800", "A81000", "F87858"), "PAUSE"),
    "sound": (164, 172, 11, ("7C7C7C", "000000", "BCBCBC"), "SOUND"),
}
LED = (12, 12)                             # inside the top piece


def D(img):
    return ImageDraw.Draw(img)


def body_columns(img, y0, y1):
    """The body's left highlight / right shadow edges, for any rows."""
    d = D(img)
    d.rectangle([0, y0, 0, y1], fill=rgb("000000"))
    d.rectangle([W - 1, y0, W - 1, y1], fill=rgb("000000"))
    d.rectangle([1, y0, 2, y1], fill=rgb(BODY_HI))
    d.rectangle([W - 4, y0, W - 2, y1], fill=rgb(BODY_SH))
    d.rectangle([3, y0, W - 5, y1], fill=rgb(BODY))


def top_piece(screen_text=None, led="off"):
    img = Image.new("RGBA", (W, TOP_H), (0, 0, 0, 0))
    d = D(img)
    d.rounded_rectangle([0, 0, W - 1, TOP_H + 30], radius=20, fill=rgb("000000"))
    d.rounded_rectangle([1, 1, W - 2, TOP_H + 30], radius=19, fill=rgb(BODY_SH))
    d.rounded_rectangle([1, 1, W - 4, TOP_H + 30], radius=19, fill=rgb(BODY_HI))
    d.rounded_rectangle([3, 3, W - 5, TOP_H + 30], radius=17, fill=rgb(BODY))
    img = img.crop((0, 0, W, TOP_H))
    d = D(img)
    d.rectangle([200, 0, 226, 2], fill=rgb("000000"))                       # power switch on the top edge
    d.rectangle([203, 1, 211, 1], fill=rgb("7C7C7C"))
    d.rounded_rectangle([3, 4, W - 5, TOP_H - 3], radius=8, fill=rgb("000000"))   # bezel
    x, y, w, h = SCREEN
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=rgb("7C7C7C"))
    text(img, "STUDY POCKET", 22, 9, GRAY)
    text(img, "ELSC", W - 36, 9, YELLOW)
    text(img, "BEAT THE NOISE. PASS THE TEST.", 0, y + h + 4, DGRAY, center=W // 2)
    led_dot(img, LED, led)
    if screen_text:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=rgb("000000"))
        for i, (t, col, sc) in enumerate(screen_text):
            text(img, t, 0, y + 92 + i * 24, col, scale=sc, center=W // 2)
    else:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=(0, 0, 0, 0))        # the game shows through here
    return img


def filler():
    img = Image.new("RGBA", (W, 1), (0, 0, 0, 0))
    body_columns(img, 0, 0)
    return img


def bottom_piece():
    img = Image.new("RGBA", (W, BOT_H), (0, 0, 0, 0))
    d = D(img)
    d.rounded_rectangle([0, -30, W - 1, BOT_H - 1], radius=20, fill=rgb("000000"))
    d.rounded_rectangle([1, -30, W - 2, BOT_H - 2], radius=19, fill=rgb(BODY_SH))
    d.rounded_rectangle([1, -30, W - 4, BOT_H - 4], radius=19, fill=rgb(BODY_HI))
    d.rounded_rectangle([3, -30, W - 5, BOT_H - 5], radius=17, fill=rgb(BODY))
    # slide pad
    x, y, w, h = PAD
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=18, fill=rgb(BODY_HI))
    d.rounded_rectangle([x, y, x + w - 2, y + h - 2], radius=18, fill=rgb(BODY_DK))
    d.rounded_rectangle([x + 3, y + 3, x + w - 2, y + h - 2], radius=16, fill=rgb(BODY_SH))
    cx, cy = x + w // 2, y + h // 2 - 4
    for r in (14, 28, 42):
        n = int(2 * math.pi * r)
        for i in range(0, n, 3):
            a = 2 * math.pi * i / n
            d.point((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))), fill=rgb(BODY_DK))
    for (ax, ay, pts) in [(cx, cy - 50, [(0, -4), (-4, 2), (4, 2)]), (cx, cy + 50, [(0, 4), (-4, -2), (4, -2)]),
                          (cx - 54, cy, [(-4, 0), (2, -4), (2, 4)]), (cx + 54, cy, [(4, 0), (-2, -4), (-2, 4)])]:
        d.polygon([(ax + p[0], ay + p[1]) for p in pts], fill=rgb(BODY_DK))
    text(img, "SLIDE", 0, y + h + 4, BODY_DK, center=cx)
    # buttons
    for name, (bx, by, r, cols, label) in BTN.items():
        img.alpha_composite(button(name, False), (bx - r - 2, by - r - 2))
        if name != "ok":                                # OK already says OK on the button
            text(img, label, 0, by + r + 5, BODY_DK, center=bx)
    # dot speaker (bottom right) and screws
    for row in range(3):
        for col in range(4):
            sx, sy = 214 + col * 9 + (4 if row == 1 else 0), 168 + row * 8
            if not (row == 1 and col == 3):
                d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=rgb(BODY_DK))
    for sx in (16, 40):
        d.ellipse([sx - 3, 196 - 3, sx + 3, 196 + 3], fill=rgb(BODY_SH))
        d.line([(sx - 2, 196), (sx + 2, 196)], fill=rgb(BODY_DK))
    return img


def button(name, pressed):
    bx, by, r, (main, dark, light), label = BTN[name]
    s = r * 2 + 5
    b = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = D(b)
    c = r + 2
    off = 1 if pressed else 0
    d.ellipse([c - r, c - r + 2, c + r, c + r + 2], fill=rgb(BODY_DK))
    d.ellipse([c - r, c - r + off, c + r, c + r + off], fill=rgb(dark))
    d.ellipse([c - r + 1, c - r + off, c + r - 1, c + r - 2 + off], fill=rgb(dark if pressed else main))
    if not pressed:
        d.arc([c - r + 3, c - r + 2, c + r - 3, c + r - 4], 200, 290, fill=rgb(light), width=2)
    ic = "FCFCFC"
    if name == "ok":
        text(b, "OK", c - 5, c - 3 + off, ic)
    elif name == "back":
        d.polygon([(c - 6, c + off), (c - 1, c - 5 + off), (c - 1, c + 5 + off)], fill=rgb(ic))
        d.rectangle([c - 1, c - 2 + off, c + 5, c + 2 + off], fill=rgb(ic))
    elif name == "pause":
        d.rectangle([c - 4, c - 4 + off, c - 2, c + 3 + off], fill=rgb(ic))
        d.rectangle([c + 1, c - 4 + off, c + 3, c + 3 + off], fill=rgb(ic))
    else:                                                                   # sound: a little note
        d.rectangle([c + 1, c - 5 + off, c + 2, c + 2 + off], fill=rgb(ic))
        d.ellipse([c - 3, c + off, c + 2, c + 4 + off], fill=rgb(ic))
        d.polygon([(c + 2, c - 5 + off), (c + 5, c - 3 + off), (c + 2, c - 2 + off)], fill=rgb(ic))
    return b


def sound_off_mark():
    r = BTN["sound"][2]
    s = r * 2 + 5
    b = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    c = r + 2
    D(b).line([(c - 7, c - 7), (c + 7, c + 7)], fill=rgb("F83800"), width=3)
    return b


def led_dot(img, pos, state):
    d = D(img)
    col = {"green": "58D854", "red": "F83800", "off": "503000"}[state]
    x, y = pos
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=rgb("000000"))
    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=rgb(col))
    if state != "off":
        d.point((x - 1, y - 1), fill=rgb("FCFCFC"))


def led_sprite(state):
    i = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    led_dot(i, (4, 4), state)
    return i


def brand_plate():
    """'ELSC' with a red underline, centered in the filler gap on tall phones."""
    b = Image.new("RGBA", (54, 20), (0, 0, 0, 0))
    text(b, "ELSC", 2, 1, "000000", scale=2)
    D(b).line([(2, 17), (47, 17)], fill=rgb("F83800"), width=2)
    return b


def assemble(top, height):
    """How the game puts the pieces together for a given skin height (>= TOP_H + BOT_H)."""
    img = Image.new("RGBA", (W, height), (0, 0, 0, 0))
    img.alpha_composite(top, (0, 0))
    f = filler()
    for y in range(TOP_H, height - BOT_H):
        img.alpha_composite(f, (0, y))
    img.alpha_composite(bottom_piece(), (0, height - BOT_H))
    gap = height - TOP_H - BOT_H
    if gap >= 30:
        bp = brand_plate()
        img.alpha_composite(bp, ((W - bp.width) // 2, TOP_H + (gap - bp.height) // 2))
    return img


if __name__ == "__main__":
    os.makedirs("handheld", exist_ok=True)
    for old in os.listdir("handheld"):
        if old.endswith(".png") or old.endswith(".json"):
            os.remove(os.path.join("handheld", old))
    top_piece().save("handheld/handheld_top.png")
    filler().save("handheld/handheld_filler.png")
    bottom_piece().save("handheld/handheld_bottom.png")
    loading_top = top_piece([("LOADING...", WHITE, 2), ("PLEASE WAIT", DGRAY, 1)], led="red")
    assemble(loading_top, 580).save("handheld/handheld_loading.png")          # one picture for the web page
    parts = {}
    for n in BTN:
        parts[f"{n}_up"] = button(n, False)
        parts[f"{n}_down"] = button(n, True)
    parts["sound_off_mark"] = sound_off_mark()
    parts["brand_plate"] = brand_plate()
    for s in ("green", "red", "off"):
        parts[f"led_{s}"] = led_sprite(s)
    sheet = Image.new("RGBA", (sum(p.width for p in parts.values()) + 2 * len(parts), 56), (0, 0, 0, 0))
    atlas, x = {}, 0
    for n, p in parts.items():
        sheet.alpha_composite(p, (x, 0))
        atlas[n] = {"x": x, "y": 0, "w": p.width, "h": p.height}
        x += p.width + 2
    sheet.save("handheld/handheld_parts.png")
    json.dump({
        "width": W,
        "pieces": {"top": "handheld_top.png", "filler": "handheld_filler.png", "bottom": "handheld_bottom.png"},
        "top_height": TOP_H, "bottom_height": BOT_H, "min_height": TOP_H + BOT_H,
        "layout": "Skin height = phone height x (268 / phone width), but at least min_height. Draw top at y 0, "
                  "repeat the filler row from top_height down to (height - bottom_height), and the bottom piece "
                  "at y = height - bottom_height. Then scale the whole skin to the phone's width (nearest-neighbor). "
                  "If the phone is too short for min_height, scale to fit the height instead and center it on black.",
        "screen": {"x": SCREEN[0], "y": SCREEN[1], "w": SCREEN[2], "h": SCREEN[3], "piece": "top"},
        "status_light": {"cx": LED[0], "cy": LED[1], "piece": "top", "sprite_offset": [-4, -4],
                         "running": "led_green", "paused": "led_off", "offline_or_loading": "led_red"},
        "slide_pad": {"x": PAD[0], "y": PAD[1], "w": PAD[2], "h": PAD[3], "piece": "bottom"},
        "buttons": {n: {"cx": b[0], "cy": b[1], "r": b[2], "piece": "bottom", "up": f"{n}_up", "down": f"{n}_down",
                        "touch_r": b[2] + 6} for n, b in BTN.items()},
        "sound_muted_mark": "sound_off_mark",
        "brand_plate": {"sprite": "brand_plate", "rule": "if the filler gap is 30 or more, draw it centered in the gap"},
        "button_sprite_offset": "draw a button sprite at (cx - r - 2, cy - r - 2)",
        "body_color": "#" + BODY,
        "parts_sheet": "handheld_parts.png",
        "parts": atlas,
    }, open("handheld/handheld_skin.json", "w"), indent=1)
    print("ok: study pocket v2")
