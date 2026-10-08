# ELSC Game — the ELSC Study Pocket: the yellow handheld shell around the game
# on a phone held upright (GAME_SPEC §19.8).
#
# Every position comes from assets/sprites/handheld/handheld_skin.json, so the
# art can change without changing this code. The shell is drawn in "skin
# pixels": 268 wide, and as tall as the phone's shape needs.

import json
import math
import os

import pygame

import settings

HANDHELD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sprites", "handheld")


class Shell:
    def __init__(self):
        with open(os.path.join(HANDHELD_DIR, "handheld_skin.json")) as f:
            self.skin = json.load(f)
        load = lambda name: pygame.image.load(os.path.join(HANDHELD_DIR, name)).convert_alpha()
        pieces = self.skin["pieces"]
        self.top, self.filler, self.bottom = load(pieces["top"]), load(pieces["filler"]), load(pieces["bottom"])
        sheet = load(self.skin["parts_sheet"])
        self.parts = {name: sheet.subsurface((p["x"], p["y"], p["w"], p["h"]))
                      for name, p in self.skin["parts"].items()}
        self.width = self.skin["width"]
        screen = self.skin["screen"]
        self.screen_spot = (screen["x"], screen["y"])     # where the game's 256 x 240 screen goes

    def height_for(self, page_size):
        """How tall the skin is on this phone: the phone's shape, but at least min_height."""
        page_w, page_h = page_size
        return max(self.skin["min_height"], round(page_h * self.width / page_w))

    def bottom_y(self, height):
        """Where the bottom piece (pad and buttons) starts."""
        return height - self.skin["bottom_height"]

    # -----------------------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------------------
    def draw(self, frame, screen, light, pressed=(), muted=False):
        """Draw the whole shell on `frame` (width x skin height), with the game's
        `screen` in its hole. light = "running", "paused" or "offline_or_loading";
        pressed = the buttons a finger is on; muted = the sound is off."""
        height = frame.get_height()
        frame.fill((0, 0, 0))
        frame.blit(screen, self.screen_spot)                    # under the top piece
        frame.blit(self.top, (0, 0))
        top_h, bottom_y = self.skin["top_height"], self.bottom_y(height)
        for y in range(top_h, bottom_y):                        # the plain body, one row at a time
            frame.blit(self.filler, (0, y))
        frame.blit(self.bottom, (0, bottom_y))

        gap = bottom_y - top_h
        if gap >= settings.HANDHELD_BRAND_PLATE_MIN_GAP:        # tall phones: the ELSC brand plate
            plate = self.parts[self.skin["brand_plate"]["sprite"]]
            frame.blit(plate, ((self.width - plate.get_width()) // 2,
                               top_h + (gap - plate.get_height()) // 2))

        lamp = self.skin["status_light"]
        dx, dy = lamp["sprite_offset"]
        frame.blit(self.parts[lamp[light]], (lamp["cx"] + dx, lamp["cy"] + dy))

        for name, button in self.skin["buttons"].items():
            spot = (button["cx"] - button["r"] - 2, bottom_y + button["cy"] - button["r"] - 2)
            if name in pressed:
                frame.blit(self.parts[button["down"]], spot)
            if name == "sound" and muted:
                frame.blit(self.parts[self.skin["sound_muted_mark"]], spot)

    # -----------------------------------------------------------------------
    # Touching
    # -----------------------------------------------------------------------
    def button_at(self, pos, height):
        """The button (e.g. "ok") under a finger at pos (skin pixels), or None.
        Each button's touch circle is a bit bigger than its drawing (touch_r)."""
        bottom_y = self.bottom_y(height)
        for name, button in self.skin["buttons"].items():
            if math.dist(pos, (button["cx"], bottom_y + button["cy"])) <= button["touch_r"]:
                return name
        return None
