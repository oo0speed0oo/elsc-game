# ELSC Game — the HUD: the black strip at the top during play (GAME_SPEC §12).
# Positions are copied from the mockup in docs/art/flow/05_stage1_play.png.

import math

import pygame

import settings
import sprites as sprite_loader
from font import BLACK, DARK_GRAY, GRAY, RED, WHITE, YELLOW

# The study bar flash colors and speed (from effects_sheet.json).
_flash = sprite_loader.read_json("effects_sheet")["study_bar_flash"]
BAR_FLASH_COLORS = [pygame.Color("#" + c) for c in _flash["fill_colors_cycle"]]
BAR_FLASH_EVERY_FRAMES = _flash["switch_every_frames"]

BAR_INSIDE = (0x50, 0x30, 0x00)      # the dark inside of the study bar
BAR_TICK_FILLED = (0xAC, 0x7C, 0x00) # segment ticks over the filled part

# Where everything goes (pixels on the 256 x 240 screen).
LEVEL_TEXT_POS = (10, 14)    # "LV2", from docs/art/v2/02_haruna_calls.png
STAGE_TEXT_POS = (32, 14)    # "STAGE 3", right after it
FACE_POS = (14, 30)
NAME_POS = (34, 36)
TIME_LABEL_Y = 8
TIME_Y = 22
TIME_SCALE = 3
STUDY_LABEL_POS = (172, 14)
BAR_FRAME = pygame.Rect(172, 28, 76, 14)   # white frame
BAR_INSIDE_RECT = pygame.Rect(174, 30, 72, 10)
BAR_TICK_EVERY = 8                         # a tick every 8 pixels


def draw_hud(surface, font, sprites, level, level_color, stage, character, seconds_left,
             meter, studying, frame_count, timer_color=None):
    pygame.draw.rect(surface, BLACK, (0, 0, settings.NES_WIDTH, settings.HUD_HEIGHT))

    # Top left: level (in its color), stage and character
    font.draw(surface, f"LV{level}", *LEVEL_TEXT_POS, level_color)
    font.draw(surface, f"STAGE {stage}", *STAGE_TEXT_POS, WHITE)
    surface.blit(sprites[f"{character}_down_stand"], FACE_POS)
    font.draw(surface, character.upper(), *NAME_POS, GRAY)

    # Top middle: the timer. Round up, so it shows 1:00 at the start and
    # only shows 0:00 when time is really up.
    whole_seconds = math.ceil(seconds_left)
    time_color = RED if whole_seconds <= settings.TIMER_RED_AT else WHITE
    if timer_color is not None:
        time_color = timer_color            # yellow while "DEADLINE EXTENDED!" counts up
    font.draw(surface, "TIME", 0, TIME_LABEL_Y, GRAY, center=True)
    font.draw(surface, f"{whole_seconds // 60}:{whole_seconds % 60:02d}", 0, TIME_Y,
              time_color, scale=TIME_SCALE, center=True)

    # Top right: the study bar (no numbers)
    font.draw(surface, "STUDY", *STUDY_LABEL_POS, GRAY)
    pygame.draw.rect(surface, WHITE, BAR_FRAME)
    pygame.draw.rect(surface, BAR_INSIDE, BAR_INSIDE_RECT)

    fill_width = int(BAR_INSIDE_RECT.width * meter / settings.BAR_MAX_POINTS)
    if studying:
        fill_color = BAR_FLASH_COLORS[(frame_count // BAR_FLASH_EVERY_FRAMES) % len(BAR_FLASH_COLORS)]
    else:
        fill_color = YELLOW
    if fill_width > 0:
        pygame.draw.rect(surface, fill_color, (BAR_INSIDE_RECT.x, BAR_INSIDE_RECT.y,
                                               fill_width, BAR_INSIDE_RECT.height))

    for tick_x in range(BAR_INSIDE_RECT.x + BAR_TICK_EVERY, BAR_INSIDE_RECT.right - 1, BAR_TICK_EVERY):
        filled = tick_x < BAR_INSIDE_RECT.x + fill_width
        pygame.draw.line(surface, BAR_TICK_FILLED if filled else BLACK,
                         (tick_x, BAR_INSIDE_RECT.top), (tick_x, BAR_INSIDE_RECT.bottom - 1))

    # A thin gray line under the HUD
    pygame.draw.line(surface, DARK_GRAY, (0, settings.HUD_HEIGHT - 1),
                     (settings.NES_WIDTH - 1, settings.HUD_HEIGHT - 1))
