from PIL import Image, ImageDraw, ImageFont

C, M, N = 32, 36, 24
W = M * 2 + N * C
COL = "ABCDEFGHIJKLMNOPQRSTUVWX"
F = "/usr/share/fonts/truetype/dejavu/"
font = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 12)
axisf = ImageFont.truetype(F + "DejaVuSans.ttf", 13)

shelves = [(0, 0, 3, 24), (3, 0, 15, 1), (3, 23, 15, 1), (15, 1, 2, 7), (18, 14, 2, 9)]
walls = [(18, 0, 6, 1), (23, 1, 1, 1), (22, 2, 2, 22), (18, 23, 4, 1)]
tables = [("Long", 9, 2, 2, 6), ("T1", 5, 10, 2, 2), ("T2", 11, 10, 2, 2), ("T3", 18, 9, 1, 1),
          ("T4", 6, 16, 2, 2), ("T5", 15, 14, 2, 2), ("T6", 10, 18, 2, 2), ("T7", 15, 19, 2, 2)]
desks = [(19, 3, 1, 4), (20, 9, 1, 3), (21, 8, 1, 1), (21, 12, 1, 1)]
board = [(6, 19), (7, 20), (8, 21)]
chairs = [(8, 2.5), (8, 4.5), (8, 6.5), (11, 2.5), (11, 4.5), (11, 6.5), (5.5, 9), (5.5, 12), (4, 10.5), (7, 10.5),
          (11.5, 9), (11.5, 12), (10, 10.5), (13, 10.5), (18, 8), (17, 9), (19, 9), (6.5, 15), (5, 16.5), (8, 16.5),
          (15.5, 13), (14, 14.5), (17, 14.5), (10.5, 17), (10.5, 20), (9, 18.5), (12, 18.5), (15.5, 18), (15.5, 21),
          (14, 19.5), (17, 19.5)]
CC = ["#3CBCFC", "#F8F8F8", "#B8F818", "#F83800"]

img = Image.new("RGB", (W, W), "#FFFFFF")
d = ImageDraw.Draw(img)


def P(x, y):
    return (M + x * C, M + y * C)


def R(x, y, w, h, fill, outline=None, width=2):
    d.rectangle([P(x, y), (M + (x + w) * C - 1, M + (y + h) * C - 1)], fill=fill, outline=outline, width=width if outline else 0)


def T(s, x, y, col):
    d.text(P(x, y), s, fill=col, font=font, anchor="mm")


R(0, 0, N, N, "#BCBCBC")
for r in shelves: R(*r, "#AC7C00", "#503000")
for r in walls: R(*r, "#7C7C7C", "#000000")
for t in tables: R(*t[1:], "#F8F8F8", "#000000")
for r in desks: R(*r, "#FCA044", "#AC7C00")
for b in board: R(b[0], b[1], 1, 1, "#A4E4FC")
d.polygon([P(6.05, 19.4), P(6.4, 19.05), P(8.95, 21.6), P(8.6, 21.95)], fill="#F8F8F8", outline="#000000", width=2)
for i, (x, y) in enumerate(chairs): R(x + .12, y + .12, .76, .76, CC[i % 4], "#000000")
R(21, 1, 1, 1, "#0058F8", "#000000")
cx, cy = P(7.5, 21.5); r = C * .42
d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#000000")

# grid lines on top so every tile shows
grid = Image.new("RGBA", img.size, (0, 0, 0, 0)); g = ImageDraw.Draw(grid)
for i in range(N + 1):
    g.line([P(i, 0), P(i, N)], fill=(0, 0, 0, 70), width=1)
    g.line([P(0, i), P(N, i)], fill=(0, 0, 0, 70), width=1)
img = Image.alpha_composite(img.convert("RGBA"), grid); d = ImageDraw.Draw(img)

T("P", 21.5, 1.5, "#FFFFFF"); T("X", 7.5, 21.5, "#FFFFFF")
for t in tables: T(t[0], t[1] + t[3] / 2, t[2] + t[4] / 2, "#000000")
T("D1", 19.5, 5, "#000000"); T("D2", 20.5, 10.5, "#000000")
T("S1", 16, 4.5, "#F8F8F8"); T("S2", 19, 18.5, "#F8F8F8"); T("Shelf", 1.5, 12, "#F8F8F8")
T("WB", 5.3, 20.6, "#000000")
for i in range(N):
    p = M + i * C + C / 2
    for (x, y) in [(p, M / 2), (p, W - M / 2)]: d.text((x, y), COL[i], fill="#444444", font=axisf, anchor="mm")
    for (x, y) in [(M / 2, p), (W - M / 2, p)]: d.text((x, y), str(i + 1), fill="#444444", font=axisf, anchor="mm")
img.convert("RGB").save("elsc_stage_layout.png")
print(img.size)
