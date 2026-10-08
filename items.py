# ELSC Game — power-up items waiting to be grabbed (GAME_SPEC §17.6).
# An item sits on the floor, on a table or on a shelf and bobs up and down so it
# reads as a power-up. What each one DOES happens when it's grabbed (in main.py).

import pygame

import layout
import settings


class Item:
    def __init__(self, name, sprite, x, y, table=None):
        """name = which power-up ("coffee", "headphones", ...), sprite = its picture,
        x, y = where its picture's top-left goes in the room (pixels).
        table = the table's rectangle for items that sit on a table, or None."""
        self.name = name
        self.sprite = sprite
        self.x, self.y = x, y
        self.table = table
        self.time = 0.0         # seconds, for the bobbing

    def update(self, dt):
        self.time += dt

    def grab_box(self):
        """Floor items: the box in the middle of the picture you have to touch."""
        size = settings.ITEM_GRAB_BOX_PIXELS
        margin = (settings.TILE_SIZE - size) / 2
        return pygame.Rect(round(self.x + margin), round(self.y + margin), size, size)

    def touched_by(self, student):
        """Is the student grabbing it? Floor item: their hitbox touches the grab box.
        Table item: their hitbox, grown a little, touches the table (so walking up
        to the table or sitting at it both work)."""
        if self.table is None:
            return student.overlap_area(self.grab_box()) > 0
        reach = settings.TABLE_GRAB_REACH_PIXELS
        return student.overlap_area(self.table.inflate(2 * reach, 2 * reach)) > 0

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        bob = settings.ITEM_BOB_PIXELS if int(self.time * settings.ITEM_BOBS_PER_SECOND * 2) % 2 else 0
        surface.blit(sprites[self.sprite], (round(self.x) - camera_x,
                                            round(self.y) - bob - camera_y + view_top))


class Pizza:
    """Level 3's pizza. It isn't grabbed like the others:
      "waiting" - the box sits on top of the right bookshelf (S2), bobbing
      "falling" - you bumped the shelf: it drops off behind it in a little arc
      "open"    - open on the floor: every cloud goes to it, ignoring you
      "gone"    - eaten (it vanished in a burst of noise bubbles)"""

    def __init__(self):
        self.state = "waiting"
        self.time = 0.0             # seconds, for the bobbing
        self.state_time = 0.0       # seconds in the current state
        self.start_x, self.start_y = layout.PIZZA_BOX_PIXEL
        self.end_x, self.end_y = layout.PIZZA_FLOOR_PIXEL
        self.x, self.y = float(self.start_x), float(self.start_y)
        self.just_eaten = False     # True for the one frame it vanishes

    def knock_off(self):
        self.state = "falling"
        self.state_time = 0.0

    def lure(self):
        """Where the clouds go while it's open (its middle, in pixels), or None."""
        if self.state != "open":
            return None
        return self.x + settings.TILE_SIZE / 2, self.y + settings.TILE_SIZE / 2

    def update(self, dt):
        self.time += dt
        self.state_time += dt
        self.just_eaten = False
        if self.state == "falling":
            t = min(self.state_time / settings.PIZZA_FALL_SECONDS, 1)
            # Slide from the shelf to the floor, lifted a little in the middle (an arc).
            self.x = self.start_x + (self.end_x - self.start_x) * t
            self.y = self.start_y + (self.end_y - self.start_y) * t - settings.PIZZA_ARC_PIXELS * 4 * t * (1 - t)
            if t >= 1:
                self.state = "open"
                self.state_time = 0.0
        elif self.state == "open" and self.state_time >= settings.PIZZA_LURE_SECONDS:
            self.state = "gone"
            self.just_eaten = True

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        if self.state == "gone":
            return
        bob = 0
        if self.state == "waiting":
            bob = settings.ITEM_BOB_PIXELS if int(self.time * settings.ITEM_BOBS_PER_SECOND * 2) % 2 else 0
        picture = sprites["item_pizza_open" if self.state == "open" else "item_pizza_box"]
        surface.blit(picture, (round(self.x) - camera_x, round(self.y) - bob - camera_y + view_top))
