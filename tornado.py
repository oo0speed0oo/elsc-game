# ELSC Game — the Noise Tornado (GAME_SPEC §7).
# It floats over furniture (it never bumps into anything) but stays inside
# the room. It is always in one of three modes:
#   "random" - pick a random spot, float there, pick another
#   "lunge"  - it just noticed you studying: a quick dash at you
#   "chase"  - after the lunge, it follows you at its normal speed
#   "pizza"  - Level 3's pizza is on the floor: it wanders around it, ignoring you
# In Levels 2 and 3 the clouds notice you after you study for the level's
# notice time without a break. When you stop studying they go back to random,
# right away (Level 2) or after chasing a few more seconds (Level 3).

import math
import random

import pygame

import layout
import settings
import sprites as sprite_loader
from effects import NoiseBubble

ROOM_WIDTH = settings.ROOM_WIDTH_TILES * settings.TILE_SIZE
ROOM_HEIGHT = settings.ROOM_HEIGHT_TILES * settings.TILE_SIZE

# Which picture each cloud size uses (the art was made for v1's three stages).
CLOUD_SHEETS = {"small": "noise_tornado_stage1", "medium": "noise_tornado_stage2",
                "big": "noise_tornado_stage3"}


class Tornado:
    def __init__(self, size_name, speed, notice_seconds, keep_chasing_seconds, start_tile):
        self.size = settings.CLOUD_SIZES[size_name]           # drawing size in pixels
        self.hitbox_size = settings.CLOUD_HITBOX[size_name]
        self.speed = speed
        self.notice_seconds = notice_seconds                   # None = never notices
        self.keep_chasing_seconds = keep_chasing_seconds       # chase on this long after you stop studying
        self.frames = sprite_loader.load_frames(CLOUD_SHEETS[size_name])

        # x, y = top-left corner of the cloud in the room, in pixels.
        # The start tile is the cloud's CENTER; then the cloud is moved (clamped)
        # so all of it is inside the room.
        start_x, start_y = start_tile
        center_x = layout.to_pixels(start_x) + settings.TILE_SIZE / 2
        center_y = layout.to_pixels(start_y) + settings.TILE_SIZE / 2
        self.x, self.y = self.keep_inside(center_x - self.size / 2, center_y - self.size / 2)

        self.anim_time = 0.0        # seconds, for the 6-frame animation
        self.bubble_timer = 0.0     # seconds since the last noise bubble
        self.mode = "random"
        self.notice_timer = 0.0     # seconds you've been studying without a break
        self.lunge_left = 0.0       # seconds of lunge still to go
        self.chase_on_left = 0.0    # after you stop studying: seconds of chasing still to go
        self.just_noticed = False   # True for the one frame it notices you (for the sound)
        self.pick_target()

    def keep_inside(self, x, y):
        """Move a top-left position so the whole cloud is inside the room."""
        x = max(0, min(x, ROOM_WIDTH - self.size))
        y = max(0, min(y, ROOM_HEIGHT - self.size))
        return float(x), float(y)

    def pick_target(self):
        """Random mode: choose a new spot anywhere in the room to float to."""
        self.target_x = random.uniform(0, ROOM_WIDTH - self.size)
        self.target_y = random.uniform(0, ROOM_HEIGHT - self.size)

    # -----------------------------------------------------------------------
    # Every frame
    # -----------------------------------------------------------------------
    def update(self, dt, sprites, student, pizza=None):
        """Notice (or forget) the student, move, animate. `pizza` = where the
        open pizza is (its middle), or None. Returns a list of new noise bubbles."""
        self.anim_time += dt
        self.just_noticed = False
        bubbles = []

        if pizza is not None:
            # The pizza wins: wander around it, ignoring the student completely.
            self.notice_timer = 0.0
            self.chase_on_left = 0.0
            if self.mode != "pizza":
                self.mode = "pizza"
                self.pick_pizza_target(pizza)
            if self.move_toward(self.target_x, self.target_y, self.speed * dt):
                self.pick_pizza_target(pizza)
            return bubbles + self.pop_bubbles(dt, sprites)
        if self.mode == "pizza":
            self.mode = "random"                  # the pizza's gone: back to normal
            self.pick_target()

        # Noticing: only while you study without a break (and without headphones on).
        if student.noticeable:
            self.notice_timer += dt
            self.chase_on_left = self.keep_chasing_seconds   # sitting down again resets it
        else:
            self.notice_timer = 0.0
            if self.mode != "random":
                if self.chase_on_left > 0:
                    self.chase_on_left -= dt      # Level 3: keep chasing a little longer
                else:
                    self.mode = "random"          # you stood up: back to wandering
                    self.pick_target()

        if (self.mode == "random" and self.notice_seconds is not None
                and self.notice_timer >= self.notice_seconds):
            # It noticed you! Lunge, with a burst of bubbles as the warning.
            self.mode = "lunge"
            self.just_noticed = True
            self.lunge_left = settings.LUNGE_SECONDS
            bubbles += self.bubble_burst(sprites)

        # Move, depending on the mode.
        if self.mode == "random":
            if self.move_toward(self.target_x, self.target_y, self.speed * dt):
                self.pick_target()            # arrived: pick another spot
        else:
            # Lunge and chase both head for the student.
            student_x, student_y = student.center()
            goal_x, goal_y = self.keep_inside(student_x - self.size / 2, student_y - self.size / 2)
            if self.mode == "lunge":
                self.move_toward(goal_x, goal_y, settings.LUNGE_SPEED * dt)
                self.lunge_left -= dt
                if self.lunge_left <= 0:
                    self.mode = "chase"
            else:
                self.move_toward(goal_x, goal_y, self.speed * dt)

        return bubbles + self.pop_bubbles(dt, sprites)

    def pop_bubbles(self, dt, sprites):
        """A noise bubble every BUBBLE_SECONDS."""
        bubbles = []
        self.bubble_timer += dt
        while self.bubble_timer >= settings.BUBBLE_SECONDS:
            self.bubble_timer -= settings.BUBBLE_SECONDS
            bubbles.append(NoiseBubble(sprites, self.x + self.size / 2, self.y))
        return bubbles

    def pick_pizza_target(self, pizza):
        """A random spot for the cloud's middle within PIZZA_LURE_TILES of the pizza."""
        radius = settings.PIZZA_LURE_TILES * settings.TILE_SIZE * math.sqrt(random.random())
        angle = random.uniform(0, 2 * math.pi)
        center_x = pizza[0] + math.cos(angle) * radius
        center_y = pizza[1] + math.sin(angle) * radius
        self.target_x, self.target_y = self.keep_inside(center_x - self.size / 2, center_y - self.size / 2)

    def move_toward(self, goal_x, goal_y, step):
        """Float up to `step` pixels toward a spot. Returns True when it gets there."""
        to_x = goal_x - self.x
        to_y = goal_y - self.y
        distance = math.hypot(to_x, to_y)
        if distance <= step:
            self.x, self.y = goal_x, goal_y
            return True
        self.x += to_x / distance * step
        self.y += to_y / distance * step
        return False

    def bubble_burst(self, sprites):
        """BUBBLES_ON_LUNGE bubbles at once, fanned out like the mockup."""
        count = settings.BUBBLES_ON_LUNGE
        burst = []
        for i in range(count):
            shift_x = (i - (count - 1) / 2) * settings.BURST_SPREAD_PIXELS
            shift_y = -i * settings.BURST_STEP_UP_PIXELS
            burst.append(NoiseBubble(sprites, self.x + self.size / 2, self.y, shift_x, shift_y))
        return burst

    # -----------------------------------------------------------------------
    # Helpers and drawing
    # -----------------------------------------------------------------------
    def center(self):
        return self.x + self.size / 2, self.y + self.size / 2

    def hitbox(self):
        """The hitbox: a square smaller than the drawing, centered on the cloud."""
        center_x, center_y = self.center()
        half = self.hitbox_size / 2
        return pygame.Rect(round(center_x - half), round(center_y - half),
                           self.hitbox_size, self.hitbox_size)

    def draw(self, surface, camera_x, camera_y, view_top):
        frame = int(self.anim_time * settings.TORNADO_FRAMES_PER_SECOND) % len(self.frames)
        surface.blit(self.frames[frame], (round(self.x) - camera_x,
                                          round(self.y) - camera_y + view_top))
