# ELSC Game — the "slide anywhere" stick for phones (GAME_SPEC §19.3).
#
# Put a thumb down: that spot is the stick's center. Slide: the student walks
# that way, snapped to 8 directions, exactly like holding the arrow keys.
# Lift: the student stops (and sits if on a chair). Every distance is in game
# pixels, so it feels the same on every phone.

import math

import pygame

import settings
from font import GRAY, WHITE

# The 8 directions, going clockwise from "right" (y grows downward).
DIRECTIONS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


class Stick:
    def __init__(self):
        self.finger = None          # the finger that steers (only the first one)
        self.center = (0.0, 0.0)    # where the thumb landed (it follows a far thumb)
        self.thumb = (0.0, 0.0)     # where the thumb is now

    @property
    def held(self):
        return self.finger is not None

    def press(self, finger, pos):
        """A finger went down. Only the first finger steers."""
        if self.finger is None:
            self.finger = finger
            self.center = self.thumb = pos

    def slide(self, finger, pos):
        if finger != self.finger:
            return                  # other fingers are ignored
        self.thumb = pos
        dx, dy = pos[0] - self.center[0], pos[1] - self.center[1]
        distance = math.hypot(dx, dy)
        reach = settings.TOUCH_STICK_FOLLOW
        if distance > reach:        # the center follows, so turning around stays quick
            self.center = (pos[0] - dx / distance * reach, pos[1] - dy / distance * reach)

    def lift(self, finger=None):
        """A finger came up (or None: let go no matter which finger)."""
        if finger is None or finger == self.finger:
            self.finger = None

    def arrows(self):
        """The arrow keys the stick is "holding": none, one, or two for a diagonal."""
        if self.finger is None:
            return set()
        dx, dy = self.thumb[0] - self.center[0], self.thumb[1] - self.center[1]
        if math.hypot(dx, dy) < settings.TOUCH_DEAD_ZONE:
            return set()            # too small a slide: do nothing
        sector = round(math.atan2(dy, dx) / (math.pi / 4)) % 8
        x, y = DIRECTIONS[sector]
        held = set()
        if x < 0:
            held.add(pygame.K_LEFT)
        elif x > 0:
            held.add(pygame.K_RIGHT)
        if y < 0:
            held.add(pygame.K_UP)
        elif y > 0:
            held.add(pygame.K_DOWN)
        return held

    def main_arrow(self):
        """For menus: the one arrow key the stick points at most (up, down, left
        or right), or None inside the dead zone."""
        if self.finger is None:
            return None
        dx, dy = self.thumb[0] - self.center[0], self.thumb[1] - self.center[1]
        if math.hypot(dx, dy) < settings.TOUCH_DEAD_ZONE:
            return None
        if abs(dx) > abs(dy):
            return pygame.K_RIGHT if dx > 0 else pygame.K_LEFT
        return pygame.K_DOWN if dy > 0 else pygame.K_UP

    def draw(self, surface, offset):
        """The faint guide: a dotted ring where the thumb landed and a small dot
        under the thumb (the same drawing as docs/art/mobile/02_playing.png).
        offset = where the game's (0, 0) is on `surface`."""
        if self.finger is None or not settings.TOUCH_STICK_VISIBLE:
            return
        cx, cy = self.center[0] + offset[0], self.center[1] + offset[1]
        radius = settings.TOUCH_STICK_RING_RADIUS
        dots = int(2 * math.pi * radius)
        for i in range(0, dots, 2):                     # every other pixel: it never hides the game
            angle = 2 * math.pi * i / dots
            spot = (int(cx + radius * math.cos(angle)), int(cy + radius * math.sin(angle)))
            if surface.get_rect().collidepoint(spot):
                surface.set_at(spot, WHITE)
        tx, ty = int(self.thumb[0] + offset[0]), int(self.thumb[1] + offset[1])
        pygame.draw.circle(surface, WHITE, (tx, ty), 4, 1)
        pygame.draw.circle(surface, GRAY, (tx, ty), 2)


class HeldKeys:
    """The keyboard's arrow keys plus the stick's, read like pygame.key.get_pressed()."""

    def __init__(self, keyboard, stick_arrows):
        self.keyboard, self.stick_arrows = keyboard, stick_arrows

    def __getitem__(self, key):
        return self.keyboard[key] or key in self.stick_arrows
