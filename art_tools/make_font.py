"""ELSC Game - NES-style bitmap font sheet (the same letters used in all the menu mockups).

Writes font.png (white letters on transparent, 8 x 8 cells, 16 per row) + font.json + a preview.
In the game: tint the letters to any color, draw each character at x += 6 (6 px per letter),
and scale by 2, 3 or 4 with nearest-neighbor for big titles.
"""
import json
from PIL import Image

exec(open("make_menus.py").read().split("def text")[0])      # F = the 5 x 7 glyphs

ORDER = " !\"#%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]_"
CELL, COLS = 8, 16
rows = (len(ORDER) + COLS - 1) // COLS
sheet = Image.new("RGBA", (COLS * CELL, rows * CELL), (0, 0, 0, 0))
chars = {}
for i, ch in enumerate(ORDER):
    g = F[ch]
    cx, cy = (i % COLS) * CELL, (i // COLS) * CELL
    for gy in range(7):
        for gx in range(5):
            if g[gy * 5 + gx] == "#":
                sheet.putpixel((cx + gx, cy + gy), (252, 252, 252, 255))
    chars[ch] = {"x": cx, "y": cy}
sheet.save("font.png")
json.dump({"sheet": "font.png", "cell": [CELL, CELL], "glyph": [5, 7], "advance": 6, "line_height": 10,
           "color": "white (FCFCFC) - tint to any NES color in code", "uppercase_only": True,
           "note": "Lowercase letters are drawn as uppercase. Unknown characters show as '?'.",
           "chars": chars}, open("font.json", "w"), indent=2)

# preview: the whole character set + a sample, in the game's text colors
PV = Image.new("RGBA", (256, 150), (0, 0, 0, 255))
def draw(s, x, y, col, scale=1):
    s = s.upper()
    for i, ch in enumerate(s):
        q = chars.get(ch, chars["?"])
        glyph = sheet.crop((q["x"], q["y"], q["x"] + 5, q["y"] + 7))
        tint = Image.new("RGBA", glyph.size, tuple(int(col[k:k + 2], 16) for k in (0, 2, 4)) + (255,))
        glyph = Image.composite(tint, glyph, glyph)
        if scale > 1:
            glyph = glyph.resize((5 * scale, 7 * scale), Image.NEAREST)
        PV.alpha_composite(glyph, (x + i * 6 * scale, y))
draw("ELSC GAME FONT", 8, 6, "F8B800", 2)
for r in range(0, len(ORDER), 32):
    draw(ORDER[r:r + 32].replace(" ", "."), 8, 34 + (r // 32) * 12, "FCFCFC")
draw("BEAT THE NOISE. PASS THE TEST.", 8, 70, "3CBCFC")
draw("TIME'S UP!", 8, 86, "F83800", 2)
draw("PASSED!", 8, 110, "00A800", 2)
draw("STAGE CODE: MATHCLASS", 8, 134, "BCBCBC")
PV.resize((256 * 4, 150 * 4), Image.NEAREST).save("font_preview_4x.png")
sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save("font_sheet_6x.png")
print("ok:", len(ORDER), "characters")
