# ELSC Game — small effects: the "+1 / +2 / +3" pop-ups (GAME_SPEC §6)
# and the Noise Tornado's noise bubbles (GAME_SPEC §7).

import math
import random

import pygame

import settings
import sprites as sprite_loader
from font import BLACK, WHITE

# Where a pop-up starts, relative to the student's sprite (from effects_sheet.json).
POPUP_START_OFFSET = sprite_loader.read_json("effects_sheet")["plus_popup"]["start_offset_from_student"]


class PlusPopup:
    def __init__(self, points, student_x, student_y):
        # Only plus_1, plus_2 and plus_3 exist, so bigger numbers show as +3.
        self.sprite = f"plus_{max(1, min(points, 3))}"
        self.x = student_x + POPUP_START_OFFSET[0]
        self.y = student_y + POPUP_START_OFFSET[1]
        self.age = 0.0   # seconds since it appeared

    def update(self, dt):
        self.age += dt

    def finished(self):
        return self.age >= settings.POPUP_RISE_SECONDS + settings.POPUP_BLINK_SECONDS

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        rise = min(self.age / settings.POPUP_RISE_SECONDS, 1) * settings.POPUP_RISE_PIXELS
        bounce = 0
        if self.age < settings.POPUP_BOUNCE_SECONDS:
            bounce = math.sin(math.pi * self.age / settings.POPUP_BOUNCE_SECONDS) * settings.POPUP_BOUNCE_PIXELS

        # Blinking: after rising, show it only every other blink step.
        blink_time = self.age - settings.POPUP_RISE_SECONDS
        if blink_time > 0 and int(blink_time / settings.BLINK_TOGGLE_SECONDS) % 2 == 1:
            return

        screen_x = round(self.x) - camera_x
        screen_y = round(self.y - rise - bounce) - camera_y + view_top
        surface.blit(sprites[self.sprite], (screen_x, screen_y))


# All the noise bubble sprite names, for example "bubble_ha".
BUBBLE_NAMES = [name for name in sprite_loader.read_json("effects_sheet")["sprites"]
                if name.startswith("bubble_")]


class NoiseBubble:
    def __init__(self, sprites, cloud_center_x, cloud_top, shift_x=0, shift_y=0):
        """Pick a random bubble and place it just above the top of the cloud,
        moved by (shift_x, shift_y) pixels (used to fan out the lunge burst)."""
        self.sprite = random.choice(BUBBLE_NAMES)
        width, height = sprites[self.sprite].get_size()
        self.x = cloud_center_x - width / 2 + shift_x
        self.y = cloud_top - height + shift_y
        self.age = 0.0   # seconds since it appeared

    def update(self, dt):
        self.age += dt

    def blink_seconds(self):
        # each blink = off once and on once
        return settings.BUBBLE_BLINKS * 2 * settings.BLINK_TOGGLE_SECONDS

    def finished(self):
        return self.age >= settings.BUBBLE_RISE_SECONDS + self.blink_seconds()

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        rise = min(self.age / settings.BUBBLE_RISE_SECONDS, 1) * settings.BUBBLE_RISE_PIXELS

        # Blinking: after rising, hide it on every other blink step.
        blink_time = self.age - settings.BUBBLE_RISE_SECONDS
        if blink_time > 0 and int(blink_time / settings.BLINK_TOGGLE_SECONDS) % 2 == 0:
            return

        screen_x = round(self.x) - camera_x
        screen_y = round(self.y - rise) - camera_y + view_top
        surface.blit(sprites[self.sprite], (screen_x, screen_y))


# ---------------------------------------------------------------------------
# Speech bubbles (GAME_SPEC §17.8): a white box with a 1 px black border,
# black text, 4 px padding, and the little tail pointing down at the speaker.
# ---------------------------------------------------------------------------
BUBBLE_PADDING = 4          # space between the text and the border, in pixels
BUBBLE_LINE_HEIGHT = 10     # distance from one line of text to the next
BUBBLE_GAP = 4              # space between the tail's tip and the top of the speaker's picture


def draw_speech_bubble(surface, font, sprites, lines, speaker_x, speaker_top, view_top):
    """Draw a speech bubble over someone. speaker_x = the middle of their picture and
    speaker_top = the top of it, both on the screen. The bubble slides sideways (and
    down) to stay on screen; the tail stays over the speaker. Nothing is drawn
    while the speaker is off screen (a bubble pointing at nobody would be confusing)."""
    speaker_size = settings.TILE_SIZE
    if (speaker_x < 0 or speaker_x > surface.get_width()
            or speaker_top + speaker_size < view_top or speaker_top > surface.get_height()):
        return
    width = max(font.width(line) for line in lines) + 2 * BUBBLE_PADDING + 2
    height = len(lines) * BUBBLE_LINE_HEIGHT + BUBBLE_PADDING + 1
    tail = sprites["bubble_tail"]
    tail_w, tail_h = tail.get_size()

    # Centered over the speaker, then kept inside the play view.
    x = round(speaker_x - width / 2)
    x = max(0, min(x, surface.get_width() - width))
    y = speaker_top - BUBBLE_GAP - tail_h - height + 1
    y = max(view_top, y)

    pygame.draw.rect(surface, BLACK, (x, y, width, height))
    pygame.draw.rect(surface, WHITE, (x + 1, y + 1, width - 2, height - 2))
    for i, line in enumerate(lines):
        font.draw(surface, line, x + BUBBLE_PADDING, y + 3 + i * BUBBLE_LINE_HEIGHT, BLACK)

    # The tail, under the box, over the speaker (but never past the box's corners).
    tail_x = round(speaker_x - tail_w / 2)
    tail_x = max(x + 2, min(tail_x, x + width - tail_w - 2))
    surface.blit(tail, (tail_x, y + height - 1))
