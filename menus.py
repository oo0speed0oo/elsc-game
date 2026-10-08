# ELSC Game — the menu screens: title, character select, stage intro and
# the pause box (GAME_SPEC §11). Positions and colors are copied from the
# mockups in docs/art/flow/.

import pygame

import settings
from font import BLACK, DARK_GRAY, DARK_RED, GRAY, GREEN, RED, SKY, WHITE, YELLOW

TITLE_CHOICES = ["START", "HIGH SCORES", "OPTIONS", "STAGE CODE"]
PAUSE_CHOICES = ["CONTINUE", "RESTART", "SOUND", "QUIT TO TITLE"]
CHARACTERS = ["boy", "girl"]
CODE_MAX_LETTERS = 24     # the most letters that fit in the stage code box
OPTION_CHOICES = ["MUSIC", "SOUND FX", "BACK"]
LEVEL_COLORS = {1: GREEN, 2: YELLOW, 3: RED}
LEVEL_TEXT = {                # the two small lines in each level's box (docs/art/v2/01_level_select.png)
    1: ("EASY", "3 STAGES - 1 TO 3 CLOUDS"),
    2: ("NORMAL", "5 STAGES - 1 TO 5 CLOUDS"),
    3: ("HARD", "5 STAGES - GIANT CLOUDS"),
}


def draw_box(screen, x, y, width, height, border=WHITE, fill=BLACK, thick=2):
    """A filled box with a colored border."""
    pygame.draw.rect(screen, border, (x, y, width, height))
    pygame.draw.rect(screen, fill, (x + thick, y + thick, width - 2 * thick, height - 2 * thick))


def draw_choices(screen, font, choices, selected, x, y, cursor_x, spacing=16):
    """A list of menu choices, `spacing` px apart. The selected one is yellow with a '>'."""
    for i, choice in enumerate(choices):
        line_y = y + i * spacing
        if i == selected:
            font.draw(screen, ">", cursor_x, line_y, YELLOW)
        font.draw(screen, choice, x, line_y, YELLOW if i == selected else WHITE)


def big(picture, scale):
    """A sprite blown up with nearest-neighbor (stays blocky)."""
    return pygame.transform.scale(picture, (picture.get_width() * scale, picture.get_height() * scale))


def draw_carpet_strip(screen, sprites, y, rows):
    tile = settings.TILE_SIZE
    for row in range(rows):
        for col in range(settings.NES_WIDTH // tile):
            name = "carpet_a" if (col + row) % 2 == 0 else "carpet_b"
            screen.blit(sprites[name], (col * tile, y + row * tile))


def draw_title(screen, font, sprites, cloud_frames, selected, seconds):
    """docs/art/flow/01. `seconds` animates the little scene."""
    screen.fill(BLACK)
    font.draw(screen, "ELSC", 0, 18, YELLOW, scale=5, center=True, shadow=DARK_RED)
    font.draw(screen, "GAME", 0, 62, WHITE, scale=2, center=True)
    font.draw(screen, "BEAT THE NOISE. PASS THE TEST.", 0, 88, SKY, center=True)

    # The little scene: two students studying at a table, the tornado nearby.
    read = "read1" if int(seconds * settings.READ_FRAMES_PER_SECOND) % 2 == 0 else "read2"
    draw_carpet_strip(screen, sprites, 104, 3)
    screen.blit(sprites["chair_green_N"], (72, 104))
    screen.blit(sprites[f"boy_seat_N_{read}"], (72, 97))
    screen.blit(sprites["table_square"], (64, 120))
    screen.blit(sprites["chair_blue_W"], (48, 128))
    screen.blit(sprites[f"girl_seat_W_{read}"], (49, 122))
    frame = int(seconds * settings.TORNADO_FRAMES_PER_SECOND) % len(cloud_frames)
    screen.blit(cloud_frames[frame], (170, 108))

    # Four choices now (HIGH SCORES was added), so they sit a little closer together.
    draw_choices(screen, font, TITLE_CHOICES, selected, x=96, y=160, cursor_x=82, spacing=14)
    font.draw(screen, "(C) 2026 ELSC", 0, 222, DARK_GRAY, center=True)


def title_tap_areas():
    """Where each title choice can be tapped (GAME_SPEC §19.4), in game pixels."""
    return [pygame.Rect(60, 157 + i * 14, 136, 14) for i in range(len(TITLE_CHOICES))]


def draw_character_select(screen, font, sprites, selected, controls="keyboard"):
    """docs/art/flow/03. `selected` = 0 for the boy, 1 for the girl."""
    screen.fill(BLACK)
    font.draw(screen, "CHOOSE YOUR", 0, 20, WHITE, scale=2, center=True)
    font.draw(screen, "STUDENT", 0, 40, YELLOW, scale=2, center=True)
    for i, character in enumerate(CHARACTERS):
        x = 40 + i * 96
        chosen = i == selected
        color = YELLOW if chosen else WHITE
        draw_box(screen, x, 70, 80, 100, border=color, fill=SKY, thick=3 if chosen else 2)
        screen.blit(big(sprites[f"{character}_down_stand"], 4), (x + 8, 88))
        name = character.upper()
        name_x = x + 40 - font.width(name, 2) // 2
        font.draw(screen, name, name_x, 176, color, scale=2)
    font.draw(screen, ">", 26 + selected * 96, 116, YELLOW, scale=2)
    if controls == "shell":
        font.draw(screen, "SLIDE + OK", 0, 212, GRAY, center=True)
    elif controls == "touch":
        font.draw(screen, "TAP A STUDENT", 0, 212, GRAY, center=True)
    else:
        font.draw(screen, "LEFT / RIGHT TO CHOOSE", 0, 206, GRAY, center=True)
        font.draw(screen, "ENTER TO START", 0, 220, GRAY, center=True)


def character_tap_areas():
    """The boy's and the girl's boxes (with their names under them)."""
    return [pygame.Rect(40 + i * 96, 70, 80, 120) for i in range(len(CHARACTERS))]


def draw_level_select(screen, font, level_clouds, selected, controls="keyboard"):
    """docs/art/v2/01_level_select.png. `selected` = 0, 1 or 2 (Level 1, 2 or 3).
    `level_clouds` = {level: cloud animation frames} for the little cloud in each box."""
    screen.fill(BLACK)
    font.draw(screen, "CHOOSE", 0, 18, WHITE, scale=2, center=True)
    font.draw(screen, "YOUR LEVEL", 0, 38, YELLOW, scale=2, center=True)
    for i, level in enumerate(LEVEL_COLORS):
        y = 70 + i * 44
        chosen = i == selected
        color = LEVEL_COLORS[level]
        name, description = LEVEL_TEXT[level]
        draw_box(screen, 20, y, 216, 38, border=color if chosen else DARK_GRAY, thick=3 if chosen else 2)
        font.draw(screen, f"LEVEL {level}", 32, y + 8, color, scale=2)
        font.draw(screen, name, 128, y + 12, WHITE if chosen else GRAY)
        font.draw(screen, description, 32, y + 26, WHITE if chosen else GRAY)
        little = pygame.transform.scale(level_clouds[level][2], (20, 20))
        screen.blit(little, (206, y + 8))
        if chosen:
            font.draw(screen, ">", 10, y + 14, YELLOW)
    if controls == "shell":
        font.draw(screen, "SLIDE + OK", 0, 216, GRAY, center=True)      # the Study Pocket (§19.8)
    elif controls == "touch":
        font.draw(screen, "TAP A LEVEL", 0, 216, GRAY, center=True)     # docs/art/mobile/03_tap_menus.png
    else:
        font.draw(screen, "UP / DOWN TO CHOOSE", 0, 212, GRAY, center=True)
        font.draw(screen, "ENTER TO START", 0, 224, GRAY, center=True)


def level_tap_areas():
    """The three level boxes."""
    return [pygame.Rect(20, 70 + i * 44, 216, 38) for i in range(len(LEVEL_COLORS))]


def draw_stage_intro(screen, font, level, stage, controls="keyboard"):
    """docs/art/flow/04, with "LEVEL N" in its color on top. The pass mark stays secret.
    On phones (touch mode) it also says how to move (GAME_SPEC §19.4)."""
    screen.fill(BLACK)
    font.draw(screen, f"LEVEL {level}", 0, 34, LEVEL_COLORS[level], center=True)
    font.draw(screen, f"STAGE {stage}", 0, 60, WHITE, scale=4, center=True)
    font.draw(screen, "READY,", 0, 112, GRAY, scale=2, center=True)
    font.draw(screen, "SET,", 0, 132, GRAY, scale=2, center=True)
    font.draw(screen, "STUDY!", 0, 156, YELLOW, scale=3, center=True, shadow=DARK_RED)
    font.draw(screen, "PASS MARK: ???", 0, 206, DARK_GRAY, center=True)
    if controls == "shell":
        font.draw(screen, "SLIDE ON THE PAD", 0, 220, GRAY, center=True)
        font.draw(screen, "LIFT TO SIT", 0, 230, GRAY, center=True)
    elif controls == "touch":
        font.draw(screen, "SLIDE ANYWHERE TO MOVE", 0, 220, GRAY, center=True)
        font.draw(screen, "LIFT TO STOP AND SIT", 0, 230, GRAY, center=True)


def draw_pause(screen, font, selected):
    """docs/art/flow/07: a box over the frozen game."""
    draw_box(screen, 58, 84, 140, 112)
    font.draw(screen, "PAUSED", 0, 96, YELLOW, scale=2, center=True)
    draw_choices(screen, font, PAUSE_CHOICES, selected, x=84, y=124, cursor_x=72)


def pause_tap_areas():
    """The four lines of the pause box."""
    return [pygame.Rect(62, 120 + i * 16, 132, 16) for i in range(len(PAUSE_CHOICES))]


def draw_stage_code(screen, font, typed, wrong):
    """docs/art/flow/16 and 17. `typed` = the letters so far; `wrong` = show WRONG CODE!"""
    screen.fill(BLACK)
    font.draw(screen, "STAGE CODE", 0, 40, WHITE, scale=2, center=True)
    font.draw(screen, "TYPE YOUR CODE", 0, 70, GRAY, center=True)
    draw_box(screen, 24, 92, 208, 34)
    font.draw(screen, typed + "_", 36, 105, YELLOW)
    if wrong:
        font.draw(screen, "WRONG CODE!", 0, 142, RED, scale=2, center=True)
    font.draw(screen, "ENTER = GO", 0, 196, GRAY, center=True)
    font.draw(screen, "ESC = BACK", 0, 210, GRAY, center=True)


def draw_options(screen, font, selected, music, sound_fx, controls="keyboard"):
    """docs/art/flow/02: two volume bars (0 to VOLUME_MAX) and BACK.
    The pause menu's SOUND opens this same screen."""
    screen.fill(BLACK)
    font.draw(screen, "OPTIONS", 0, 30, WHITE, scale=2, center=True)
    for i, (label, value) in enumerate([("MUSIC", music), ("SOUND FX", sound_fx)]):
        y = 84 + i * 36
        if i == selected:
            font.draw(screen, ">", 18, y, YELLOW)
        font.draw(screen, label, 30, y, YELLOW if i == selected else WHITE)
        for block in range(settings.VOLUME_MAX):
            color = YELLOW if block < value else DARK_GRAY
            pygame.draw.rect(screen, color, (110 + block * 10, y - 1, 8, 9))
        font.draw(screen, str(value), 216, y, WHITE)
    if selected == 2:
        font.draw(screen, ">", 18, 164, YELLOW)
    font.draw(screen, "BACK", 30, 164, YELLOW if selected == 2 else WHITE)
    if controls == "shell":
        font.draw(screen, "SLIDE TO SELECT AND CHANGE", 0, 206, GRAY, center=True)
        font.draw(screen, "BACK WHEN DONE", 0, 220, GRAY, center=True)
    elif controls == "touch":
        font.draw(screen, "TAP THE BARS TO CHANGE", 0, 206, GRAY, center=True)
        font.draw(screen, "TAP BACK WHEN DONE", 0, 220, GRAY, center=True)
    else:
        font.draw(screen, "UP / DOWN TO SELECT", 0, 206, GRAY, center=True)
        font.draw(screen, "LEFT / RIGHT TO CHANGE", 0, 220, GRAY, center=True)


def option_tap_areas():
    """The options screen: [(line, block, area)]. line 0 = MUSIC, 1 = SOUND FX,
    2 = BACK; block = which volume block (0 to VOLUME_MAX - 1), or None for the
    line's name. The blocks are tall, so a finger can hit them."""
    areas = []
    for line in (0, 1):
        y = 84 + line * 36
        areas.append((line, None, pygame.Rect(14, y - 8, 94, 24)))
        for block in range(settings.VOLUME_MAX):
            areas.append((line, block, pygame.Rect(109 + block * 10, y - 8, 10, 24)))
    areas.append((2, None, pygame.Rect(14, 156, 80, 24)))
    return areas


def draw_click_to_play(screen, font, seconds, touch=False):
    """Web only: browsers block sound and the keyboard until the page is clicked,
    so the game waits here first (GAME_SPEC §18.1). Phones say TAP (§19.1)."""
    screen.fill(BLACK)
    font.draw(screen, "ELSC", 0, 60, YELLOW, scale=5, center=True, shadow=DARK_RED)
    font.draw(screen, "GAME", 0, 104, WHITE, scale=2, center=True)
    if int(seconds / settings.CLICK_TO_PLAY_BLINK_SECONDS) % 2 == 0:
        font.draw(screen, "TAP TO PLAY" if touch else "CLICK TO PLAY", 0, 160, WHITE, scale=2, center=True)
