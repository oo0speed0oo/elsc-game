# ELSC Game — the screens around a round: the "TIME'S UP!" banner, the
# test results, and "YOU PASSED THE COURSE!!!" (GAME_SPEC §9 and §11).
# Positions and colors are copied from the mockups in docs/art/flow/.

import random

import pygame

import settings
from font import (BLACK, DARK_GRAY, DARK_GREEN, DARK_RED, DARKER_RED, GOLD, GRAY, GREEN, PINK,
                  RED, SKY, WHITE, YELLOW)
from letter_grid import draw_name_entry

BAR_INSIDE = (0x50, 0x30, 0x00)      # the dark inside of the study bar
BAR_TICK_FILLED = (0xAC, 0x7C, 0x00) # segment ticks over the filled part
CONFETTI_COLORS = [YELLOW, SKY, GREEN, RED, PINK, WHITE]
GO_ON = {"keyboard": "PRESS ENTER", "touch": "TAP TO CONTINUE", "shell": "PRESS OK"}   # "carry on" hints


def draw_times_up(screen, font):
    """The banner across the frozen play view (docs/art/flow/08)."""
    pygame.draw.rect(screen, BLACK, (0, 124, settings.NES_WIDTH, 45))
    pygame.draw.line(screen, WHITE, (0, 124), (settings.NES_WIDTH - 1, 124))
    pygame.draw.line(screen, WHITE, (0, 168), (settings.NES_WIDTH - 1, 168))
    font.draw(screen, "TIME'S UP!", 0, 136, RED, scale=3, center=True, shadow=DARK_RED)


def draw_deadline_extended(screen, font, sprites):
    """The laptop box over the frozen game (docs/art/v2/04_deadline_extended.png)."""
    pygame.draw.rect(screen, WHITE, (40, 74, 176, 64))
    pygame.draw.rect(screen, BLACK, (42, 76, 172, 60))
    screen.blit(sprites["item_laptop"], (52, 86))
    font.draw(screen, "DEADLINE", 76, 86, YELLOW, scale=2)
    font.draw(screen, "EXTENDED!", 76, 104, YELLOW, scale=2)
    font.draw(screen, f"+{settings.LAPTOP_EXTRA_SECONDS} SEC", 0, 124, WHITE, center=True)


def draw_big_study_bar(screen, x, y, width, height, fraction):
    """The results screen's study bar: white frame, dark inside, yellow fill
    with a gold shine and segment ticks. No numbers, no pass line."""
    pygame.draw.rect(screen, WHITE, (x, y, width, height))
    pygame.draw.rect(screen, BAR_INSIDE, (x + 2, y + 2, width - 4, height - 4))
    fill_width = int((width - 4) * fraction)
    if fill_width > 0:
        pygame.draw.rect(screen, YELLOW, (x + 2, y + 2, fill_width, height - 4))
        pygame.draw.rect(screen, GOLD, (x + 2, y + 2, fill_width, 2))   # shine
    for tick_x in range(x + 10, x + width - 3, 8):
        filled = tick_x <= x + 1 + fill_width
        pygame.draw.line(screen, BAR_TICK_FILLED if filled else BLACK,
                         (tick_x, y + 2), (tick_x, y + height - 3))


def draw_portrait(screen, sprites, name, x, y, scale=1):
    """A 32 x 32 portrait on a light-blue card (a 2 px white frame filled with sky
    blue), so Haruna's black hair shows on the black screen."""
    size = 32 * scale
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, size + 4, size + 4))
    pygame.draw.rect(screen, SKY, (x, y, size, size))
    picture = sprites[name]
    if scale != 1:
        picture = pygame.transform.scale(picture, (size, size))
    screen.blit(picture, (x, y))


def draw_left_tail_bubble(screen, font, sprites, lines, x, y):
    """A speech bubble at (x, y) with its tail on the left side, pointing left."""
    width = max(font.width(line) for line in lines) + 10
    height = len(lines) * 10 + 5
    pygame.draw.rect(screen, BLACK, (x, y, width, height))
    pygame.draw.rect(screen, WHITE, (x + 1, y + 1, width - 2, height - 2))
    for i, line in enumerate(lines):
        font.draw(screen, line, x + 4, y + 3 + i * 10, BLACK)
    tail = pygame.transform.rotate(sprites["bubble_tail"], -90)    # the tail points down; turn it to point left
    screen.blit(tail, (x - 3, y + height // 2 - 4))


def results_lines(passed, stage, last_stage, code=None, score=None):
    """What Hitomi says in her box: (text, color, scale, shadow, y) for each line."""
    lines = []
    if passed:
        lines.append(("YOU PASSED!", GREEN, 2, DARK_GREEN, 150))
        if stage < last_stage:
            lines.append((f"ON TO STAGE {stage + 1}...", GRAY, 1, None, 176))
        else:
            lines.append(("COURSE COMPLETE!", GRAY, 1, None, 176))
        if score is not None:
            lines.append((f"SCORE +{score}", YELLOW, 1, None, 200))
    else:
        lines.append(("YOU FAILED...", RED, 2, DARKER_RED, 150))
        lines.append(("SEE YOUR SCORE", GRAY, 1, None, 176))
        if code:
            if len(f"STAGE CODE: {code}") * 6 <= 180:
                lines.append((f"STAGE CODE: {code}", YELLOW, 1, None, 200))
            else:
                # A long code doesn't fit on one line: put it under the label.
                lines.append(("STAGE CODE:", YELLOW, 1, None, 200))
                lines.append((code, YELLOW, 1, None, 212))
    return lines


def letters_typed(seconds):
    """How many letters of Hitomi's answer have typed out so far."""
    if seconds < settings.RESULTS_VERDICT_AT:
        return 0
    return int((seconds - settings.RESULTS_VERDICT_AT) * settings.RESULTS_TYPING_LETTERS_PER_SECOND)


def draw_results(screen, font, sprites, stage, last_stage, meter, passed, seconds, code=None, score=None):
    """The test with Haruna and Hitomi (docs/art/v2/07_results_passed.png and 08).
    `seconds` = how long this screen has been showing:
      from the start           THE TEST and your bar (no numbers, no pass line)
      RESULTS_QUESTION_AT      Haruna asks "DID YOU PASS?" (the drumroll)
      RESULTS_VERDICT_AT       Hitomi answers; her box types out letter by letter"""
    screen.fill(BLACK)
    font.draw(screen, "THE TEST", 0, 12, GRAY, scale=2, center=True)
    draw_big_study_bar(screen, 48, 34, 160, 14, meter / settings.BAR_MAX_POINTS)

    frame = int(seconds * settings.PORTRAIT_FRAMES_PER_SECOND) % 2
    asking = settings.RESULTS_QUESTION_AT <= seconds < settings.RESULTS_VERDICT_AT
    answered = seconds >= settings.RESULTS_VERDICT_AT

    # Haruna (left): talks while she asks, smiles otherwise.
    haruna = "portrait_haruna_talk" if asking and frame == 0 else "portrait_haruna_smile"
    draw_portrait(screen, sprites, haruna, 14, 60, 2)
    if seconds >= settings.RESULTS_QUESTION_AT:
        draw_left_tail_bubble(screen, font, sprites, ["DID YOU", "PASS?"], 88, 66)

    # Hitomi (right): smiles and waits, then cheers or shakes her head.
    mood = "cheer" if passed else "sorry"
    if answered:
        hitomi_big = f"portrait_hitomi_{mood}{2 - frame}"
        hitomi_small = f"portrait_hitomi_{mood}{1 + frame}"
    else:
        hitomi_big = "portrait_hitomi_smile"
    draw_portrait(screen, sprites, hitomi_big, 178, 60, 2)

    # Her answer in a Zelda-style dialogue box, typing out letter by letter.
    if answered:
        pygame.draw.rect(screen, WHITE, (8, 136, 240, 96))
        pygame.draw.rect(screen, BLACK, (10, 138, 236, 92))
        draw_portrait(screen, sprites, hitomi_small, 20, 150)
        letters_left = letters_typed(seconds)
        for text, color, scale, shadow, y in results_lines(passed, stage, last_stage, code, score):
            shown = text[:max(0, letters_left)]
            letters_left -= len(text)
            if shown:
                font.draw(screen, shown, 58, y, color, scale=scale, shadow=shadow)


def draw_score(screen, font, sprites, level, score, level_complete, new_high, name, phase,
               announced, saved_here=False, controls="keyboard", flash=None, cursor=None):
    """After every run: YOU SCORED, and the name entry if it's a new high score
    (docs/art/v2/09_score_entry.png). `phase` is where the score screen is:
      "checking"        asking the score server for the top 10 (nothing shown yet)
      "decided"         NEW HIGH SCORE! and the name entry, or PRESS ENTER
      "saving"          SAVING...
      "could_not_save"  COULD NOT SAVE (saved_here: it was saved on this computer instead)
    `announced` = NEW HIGH SCORE! may show now. controls = "keyboard", "touch"
    or "shell" (the Study Pocket); on phones the name is typed on the letter grid
    (flash = the cell just typed, cursor = the slide pad's cell)."""
    if controls != "keyboard" and phase == "decided" and new_high and announced:
        draw_name_entry(screen, font, score, name, flash, cursor)
        return
    go_on = GO_ON[controls]
    screen.fill(BLACK)
    if level_complete:
        font.draw(screen, f"LEVEL {level} COMPLETE!", 0, 22, YELLOW, center=True)
    font.draw(screen, "YOU SCORED", 0, 44, WHITE, scale=2, center=True)
    font.draw(screen, str(score), 0, 70, YELLOW, scale=4, center=True, shadow=DARK_RED)
    draw_portrait(screen, sprites, "portrait_haruna_smile", 34, 112)
    draw_portrait(screen, sprites, "portrait_hitomi_cheer2" if level_complete else "portrait_hitomi_smile", 190, 112)

    if phase == "saving":
        font.draw(screen, "NEW HIGH SCORE!", 0, 124, GREEN, center=True)
        font.draw(screen, "SAVING...", 0, 176, WHITE, center=True)
    elif phase == "could_not_save":
        font.draw(screen, "COULD NOT SAVE", 0, 156, RED, scale=2, center=True)
        if saved_here:
            font.draw(screen, "SAVED ON THIS COMPUTER", 0, 180, GRAY, center=True)
        font.draw(screen, go_on, 0, 212, GRAY, center=True)
    elif phase != "decided":
        pass                                     # still asking the server
    elif new_high and announced:
        font.draw(screen, "NEW HIGH SCORE!", 0, 124, GREEN, center=True)
        font.draw(screen, "TYPE YOUR NAME", 0, 156, GRAY, center=True)
        pygame.draw.rect(screen, WHITE, (58, 168, 140, 26))
        pygame.draw.rect(screen, BLACK, (60, 170, 136, 22))
        for i in range(settings.NAME_MAX_LETTERS):
            x = 70 + i * 12
            if i < len(name):
                font.draw(screen, name[i], x, 177, YELLOW)
            line_color = WHITE if i == len(name) else DARK_GRAY    # the white line = where the next letter goes
            pygame.draw.line(screen, line_color, (x, 187), (x + 4, 187))
        font.draw(screen, "ENTER = SAVE", 0, 212, GRAY, center=True)
        font.draw(screen, f"UP TO {settings.NAME_MAX_LETTERS} LETTERS", 0, 224, DARK_GRAY, center=True)
    elif not new_high:
        font.draw(screen, go_on, 0, 212, GRAY, center=True)


def draw_high_scores(screen, font, level, entries, status="local", saved_rank=None, controls="keyboard"):
    """The top 10 of one level (docs/art/v2/10_high_scores.png). `status`:
      "local"    the list on this computer (no score server set up)
      "loading"  LOADING... (asking the score server)
      "online"   the shared list from the score server
      "offline"  the server couldn't be reached: OFFLINE, and the list on this computer
    saved_rank = the place (1-10) of a score that was just saved: the screen then
    says SAVED! and that score is yellow (the screen after typing your name)."""
    screen.fill(BLACK)
    if saved_rank is None:
        font.draw(screen, "HIGH SCORES", 0, 14, WHITE, scale=2, center=True)
        font.draw(screen, f"<  LEVEL {level}  >", 0, 40, YELLOW, center=True)
    else:
        font.draw(screen, "SAVED!", 0, 14, GREEN, scale=2, center=True)
        font.draw(screen, f"LEVEL {level}", 0, 40, YELLOW, center=True)
    if status == "offline":
        font.draw(screen, "OFFLINE", 0, 50, RED, center=True)

    if status == "loading":
        font.draw(screen, "LOADING...", 0, 120, WHITE, center=True)
    else:
        for i in range(settings.HIGH_SCORES_KEPT):
            y = 60 + i * 14
            if saved_rank is not None:
                color = YELLOW if i == saved_rank - 1 else (WHITE if i < 3 else GRAY)
            else:
                color = YELLOW if i == 0 else (WHITE if i < 3 else GRAY)
            font.draw(screen, f"{i + 1:>2}.", 28, y, color)
            if i < len(entries):
                font.draw(screen, entries[i]["name"], 58, y, color)
                font.draw(screen, f"{entries[i]['score']:>6}", 170, y, color)
            else:
                font.draw(screen, "---", 58, y, DARK_GRAY)

    if saved_rank is None and controls == "shell":
        font.draw(screen, "SLIDE LEFT / RIGHT = LEVEL", 0, 212, GRAY, center=True)
        font.draw(screen, "BACK = BACK", 0, 224, GRAY, center=True)
    elif saved_rank is None and controls == "touch":
        font.draw(screen, "TAP < > = LEVEL", 0, 212, GRAY, center=True)
        font.draw(screen, "TAP ANYWHERE ELSE = BACK", 0, 224, GRAY, center=True)
    elif saved_rank is None:
        font.draw(screen, "LEFT / RIGHT = LEVEL", 0, 212, GRAY, center=True)
        font.draw(screen, "ESC = BACK", 0, 224, GRAY, center=True)
    else:
        font.draw(screen, GO_ON[controls], 0, 224, GRAY, center=True)


def high_scores_arrow_areas():
    """Where to tap "<" and ">" on HIGH SCORES (generous, for fingers)."""
    return pygame.Rect(40, 30, 60, 26), pygame.Rect(156, 30, 60, 26)


def make_confetti():
    """Random confetti for the course complete screen: (x, y, color) each."""
    return [(random.randint(0, settings.NES_WIDTH - 3), random.randint(0, settings.NES_HEIGHT - 3),
             random.choice(CONFETTI_COLORS)) for _ in range(settings.CONFETTI_PIECES)]


def draw_course_complete(screen, font, sprites, confetti, controls="keyboard"):
    """YOU PASSED THE COURSE!!! (docs/art/flow/18)."""
    screen.fill(BLACK)
    for x, y, color in confetti:
        pygame.draw.rect(screen, color, (x, y, 2, 2))

    # Yellow box with the big words
    pygame.draw.rect(screen, YELLOW, (20, 30, 216, 84))
    pygame.draw.rect(screen, BLACK, (22, 32, 212, 80))
    font.draw(screen, "YOU PASSED", 0, 46, WHITE, scale=3, center=True)
    font.draw(screen, "THE COURSE!!!", 0, 80, YELLOW, scale=2, center=True, shadow=DARK_RED)

    # A strip of carpet with both students, 4x size
    tile = settings.TILE_SIZE
    for row in range(5):
        for col in range(settings.NES_WIDTH // tile):
            name = "carpet_a" if (col + row) % 2 == 0 else "carpet_b"
            screen.blit(sprites[name], (col * tile, 124 + row * tile))
    for character, x in (("boy", 60), ("girl", 132)):
        picture = sprites[f"{character}_down_stand"]
        big = pygame.transform.scale(picture, (picture.get_width() * 4, picture.get_height() * 4))
        screen.blit(big, (x, 132))

    font.draw(screen, GO_ON[controls], 0, 210, WHITE, center=True)
