# ELSC Game — the letter grid for typing on phones (GAME_SPEC §19.5).
# In touch mode the name entry and the stage code screen show a grid of
# letters to tap, instead of needing a keyboard. Positions and colors are
# copied from the mockup docs/art/mobile/04_name_grid.png.

import pygame

import settings
from font import BLACK, DARK_BROWN, DARK_GRAY, GREEN, RED, WHITE, YELLOW
from menus import draw_box

ROWS = ["ABCDEFGH", "IJKLMNOP", "QRSTUVWX", "YZ012345", "6789"]
STEP_X, STEP_Y = 28, 22         # from one cell to the next
CELL_W, CELL_H = 24, 18         # a cell (big enough for a thumb)
LEFT, TOP = 16, 76              # the top left cell
OK_AREA = pygame.Rect(40, 200, 176, 26)


def cells(codes=False):
    """Every cell: (value, label, area, enabled, label color). value is the
    letter, " " for SPACE, "DEL" or "OK". Stage codes are letters only, so
    the numbers and SPACE are greyed out there."""
    found = []
    for r, row in enumerate(ROWS):
        for c, letter in enumerate(row):
            area = pygame.Rect(LEFT + c * STEP_X, TOP + r * STEP_Y, CELL_W, CELL_H)
            found.append((letter, letter, area, not (codes and letter.isdigit()), WHITE))
    last_row = TOP + 4 * STEP_Y
    found.append((" ", "SPACE", pygame.Rect(LEFT + 4 * STEP_X, last_row, 52, CELL_H), not codes, WHITE))
    found.append(("DEL", "DEL", pygame.Rect(LEFT + 6 * STEP_X, last_row, 52, CELL_H), True, RED))
    found.append(("OK", "OK", OK_AREA, True, GREEN))
    return found


def tapped(pos, codes=False):
    """The value of the cell at pos (game pixels), or None (also for greyed-out cells)."""
    for value, label, area, enabled, color in cells(codes):
        if enabled and area.collidepoint(pos):
            return value
    return None


def move(index, key, codes=False):
    """The Study Pocket's slide pad moves a cursor over the grid (§19.8): from
    cell number `index`, which cell is next in the arrow key's direction?
    Greyed-out cells are skipped. Stays put at the edge."""
    grid = [c for c in cells(codes)]
    here = grid[index][2]
    best, best_score = index, None
    for i, (value, label, area, enabled, color) in enumerate(grid):
        if not enabled or i == index:
            continue
        dx, dy = area.centerx - here.centerx, area.centery - here.centery
        if key == pygame.K_LEFT and area.centery == here.centery and dx < 0:
            score = -dx
        elif key == pygame.K_RIGHT and area.centery == here.centery and dx > 0:
            score = dx
        elif key == pygame.K_UP and dy < 0:
            score = -dy * 1000 + abs(dx)        # the nearest row first, then the nearest cell in it
        elif key == pygame.K_DOWN and dy > 0:
            score = dy * 1000 + abs(dx)
        else:
            continue
        if best_score is None or score < best_score:
            best, best_score = i, score
    return best


def value_at(index, codes=False):
    """The value of cell number `index` ("A", " ", "DEL", "OK"...)."""
    return cells(codes)[index][0]


def draw_grid(screen, font, ok_text, flash=None, codes=False, cursor=None):
    """The grid and the big OK button. flash = the value of the cell that was
    just tapped or typed (filled yellow for a moment); cursor = the number of
    the cell the slide pad is on (Study Pocket only), or None."""
    for i, (value, label, area, enabled, color) in enumerate(cells(codes)):
        lit = value == flash
        here = i == cursor
        if value == "OK":
            draw_box(screen, *area, border=YELLOW if lit or here else GREEN,
                     fill=YELLOW if lit else (DARK_BROWN if here else BLACK), thick=2)
            font.draw(screen, ok_text, 0, area.y + 9, BLACK if lit else (YELLOW if here else GREEN), center=True)
            continue
        draw_box(screen, *area, border=YELLOW if lit or here else DARK_GRAY,
                 fill=YELLOW if lit else (DARK_BROWN if here else BLACK), thick=1)
        if not enabled:
            color = DARK_GRAY
        elif lit:
            color = BLACK
        elif here:
            color = YELLOW
        if len(label) == 1:
            font.draw(screen, label, area.x + CELL_W // 2 - 2, area.y + 5, color)
        else:
            font.draw(screen, label, area.x + 4, area.y + 5, color)


def draw_name_entry(screen, font, score, name, flash=None, cursor=None):
    """The touch-mode name entry (docs/art/mobile/04_name_grid.png)."""
    screen.fill(BLACK)
    font.draw(screen, "NEW HIGH SCORE!", 0, 10, GREEN, center=True)
    font.draw(screen, str(score), 0, 24, YELLOW, scale=2, center=True)
    draw_box(screen, 48, 46, 160, 22)
    for i in range(settings.NAME_MAX_LETTERS):
        x = 60 + i * 14
        if i < len(name):
            font.draw(screen, name[i], x, 53, YELLOW)
        pygame.draw.line(screen, WHITE if i == len(name) else DARK_GRAY, (x, 62), (x + 4, 62))
    draw_grid(screen, font, "OK - SAVE", flash, cursor=cursor)


def draw_code_entry(screen, font, typed, wrong, flash=None, cursor=None):
    """The touch-mode stage code screen: the same grid, letters only."""
    screen.fill(BLACK)
    font.draw(screen, "STAGE CODE", 0, 8, WHITE, scale=2, center=True)
    draw_box(screen, 24, 32, 208, 26)
    font.draw(screen, typed + "_", 36, 41, YELLOW)
    if wrong:
        font.draw(screen, "WRONG CODE!", 0, 63, RED, center=True)
    draw_grid(screen, font, "OK - GO", flash, codes=True, cursor=cursor)
