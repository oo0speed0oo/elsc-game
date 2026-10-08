# ELSC Game — where the game sits in the window, and turning a click or a
# touch into game pixels (GAME_SPEC §18.1, §19.2).
#
# Everything is drawn on the 256 x 240 NES screen. That screen is copied onto
# the "frame": the whole picture we show.
#   - Computers: the frame IS the NES screen, blown up by a whole number.
#   - Phones (§19.2): the frame is as wide and tall as the phone's shape needs,
#     with the NES screen near the top (portrait) or in the middle (landscape)
#     and black around it. So the black space is part of our picture too, and
#     a thumb there still lands "in the game".
#   - Phones held upright in touch mode (§19.8): the frame is the ELSC Study
#     Pocket shell (268 skin pixels wide), with the NES screen in its hole.

import settings

GAME_W, GAME_H = settings.NES_WIDTH, settings.NES_HEIGHT


class View:
    def __init__(self, page_size, phone, shell=None):
        """page_size: the window (desktop) or the web page, in real screen pixels.
        phone: use the phone page (§19.2). shell: the Study Pocket (a Shell) to
        draw the game in, or None."""
        page_w, page_h = page_size
        self.page_size = page_size
        self.phone = phone
        self.shell = shell is not None
        scale = min(page_w / GAME_W, page_h / GAME_H)     # real pixels per game pixel
        if shell is not None:
            # As wide as the phone; a phone too short for the shell gets it
            # scaled to fit the height instead, centered on black.
            frame_w, frame_h = shell.width, shell.height_for(page_size)
            self.frame_size = (frame_w, frame_h)
            self.offset = shell.screen_spot
            scale = min(page_w / frame_w, page_h / frame_h)
            draw = max(1, min(int(scale), settings.PHONE_DRAW_SCALE_MAX))
            self.canvas_size = (frame_w * draw, frame_h * draw)
            self.shown_size = (round(frame_w * scale), round(frame_h * scale))
        elif phone:
            # Fill the whole screen, at any scale (not only whole numbers).
            frame_w = max(GAME_W, round(page_w / scale))
            frame_h = max(GAME_H, round(page_h / scale))
            self.frame_size = (frame_w, frame_h)
            self.offset = ((frame_w - GAME_W) // 2, min(settings.PHONE_GAME_TOP, frame_h - GAME_H))
            # We draw a whole number of real pixels per game pixel (at most
            # PHONE_DRAW_SCALE_MAX, to keep phones fast); the browser stretches
            # the last little bit, also without smoothing.
            draw = max(1, min(int(scale), settings.PHONE_DRAW_SCALE_MAX))
            self.canvas_size = (frame_w * draw, frame_h * draw)
            self.shown_size = page_size
        else:
            # The biggest whole-number scale that fits (every pixel the same
            # size), or on a very small page the biggest scale that fits at all.
            if scale >= 1:
                scale = int(scale)
            self.frame_size = (GAME_W, GAME_H)
            self.offset = (0, 0)
            self.canvas_size = (max(1, int(GAME_W * scale)), max(1, int(GAME_H * scale)))
            self.shown_size = self.canvas_size

    def to_frame(self, x, y):
        """A spot given as fractions of the window (0 to 1 across, 0 to 1 down),
        the way touches arrive, in frame pixels (skin pixels on the shell)."""
        return x * self.frame_size[0], y * self.frame_size[1]

    def to_game(self, x, y):
        """The same spot in game pixels: (0, 0) is the top left of the 256 x 240
        game. Spots in the black space (or on the shell) below the game have y > 240."""
        frame_x, frame_y = self.to_frame(x, y)
        return frame_x - self.offset[0], frame_y - self.offset[1]

    def window_to_game(self, pos):
        """A mouse position (window pixels) in game pixels."""
        canvas_w, canvas_h = self.canvas_size
        return self.to_game(pos[0] / canvas_w, pos[1] / canvas_h)
