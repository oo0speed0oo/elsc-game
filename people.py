# ELSC Game — Haruna (the receptionist) and Hitomi (the teacher), GAME_SPEC §17.4 and §17.5.
# Haruna sits at her desk and calls out every so often. Hitomi sits at her
# desk and walks out into the room when your bar reaches certain percents.

import math
import random

import pygame

import layout
import settings
from effects import draw_speech_bubble

HARUNA_CALL_LINES = ["BE QUIET PLEASE,", "PEOPLE ARE STUDYING!"]
HITOMI_LINES = ["DID YOU STUDY?!"]


def draw_at_tile(surface, picture, tile, lift, camera_x, camera_y, view_top):
    """Draw a 16 x 16 picture on a room tile, `lift` pixels higher."""
    tile_x, tile_y = tile
    surface.blit(picture, (layout.to_pixels(tile_x) - camera_x,
                           layout.to_pixels(tile_y) - lift - camera_y + view_top))


class Haruna:
    """Sits at her desk facing it, typing. Every HARUNA_CALL_EVERY_SECONDS she
    puts her hands up and calls out "BE QUIET PLEASE, PEOPLE ARE STUDYING!".
    It's just for fun and tension: it changes nothing."""

    def __init__(self):
        self.time = 0.0             # seconds, for the typing animation
        self.until_call = settings.HARUNA_CALL_EVERY_SECONDS   # seconds until she calls out
        self.calling_left = 0.0     # seconds of hands-up still to go
        self.bubble_left = 0.0      # seconds her speech bubble still shows
        self.just_called = False    # True for the one frame she calls out (for the sound)
        self.toss_left = 0.0        # seconds of the "toss" picture still to go (dropping the headphones)

    def toss(self):
        """She drops the headphones for a struggling student."""
        self.toss_left = settings.HARUNA_TOSS_SECONDS

    def update(self, dt):
        self.time += dt
        self.just_called = False
        self.calling_left = max(0.0, self.calling_left - dt)
        self.toss_left = max(0.0, self.toss_left - dt)
        self.bubble_left = max(0.0, self.bubble_left - dt)
        self.until_call -= dt
        if self.until_call <= 0:
            self.until_call += settings.HARUNA_CALL_EVERY_SECONDS
            self.calling_left = settings.HARUNA_CALL_SECONDS
            self.bubble_left = settings.HARUNA_BUBBLE_SECONDS
            self.just_called = True

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        if self.toss_left > 0:
            picture = sprites["haruna_toss"]
        elif self.calling_left > 0:
            frame = int(self.time * settings.HARUNA_CALL_FRAMES_PER_SECOND) % 2
            picture = sprites["haruna_call1" if frame == 0 else "haruna_call2"]
        else:
            frame = int(self.time * settings.HARUNA_TYPE_FRAMES_PER_SECOND) % 2
            picture = sprites["haruna_type1" if frame == 0 else "haruna_type2"]
        draw_at_tile(surface, picture, layout.HARUNA_SEAT, layout.SITTING_LIFT,
                     camera_x, camera_y, view_top)

    def draw_bubble(self, surface, font, sprites, camera_x, camera_y, view_top):
        """Her speech bubble (drawn later than the people, so it's on top)."""
        if self.bubble_left <= 0:
            return
        seat_x, seat_y = layout.HARUNA_SEAT
        speaker_x = layout.to_pixels(seat_x) + settings.TILE_SIZE / 2 - camera_x
        speaker_top = layout.to_pixels(seat_y) - layout.SITTING_LIFT - camera_y + view_top
        draw_speech_bubble(surface, font, sprites, HARUNA_CALL_LINES, speaker_x, speaker_top, view_top)


class Hitomi:
    """The teacher. She sits inside her U-shaped desk facing left, working, until
    your study bar first reaches one of the level's percents. Then:

      "desk"      - sitting and working (the gate is closed)
      "exiting"   - the gate opens and she walks down out of her desk
      "pointing"  - just outside: "DID YOU STUDY?!" while she wags her finger
      "out"       - she walks around the room, depending on the level:
                    "wander" = random spots, "follow" = toward you,
                    "chairs" = stands on the free chair closest to you
      "returning" - her time is up: she walks back to her gate
      "entering"  - she walks in to her chair and the gate closes

    While she's out she's solid, is blocked by furniture like the student (and
    slides along it), and never walks into you. If she bumps you while you're
    standing, she stops (Level 1) or pushes you 1 tile (Levels 2 and 3). She
    treats a seated student as a wall. She never takes points."""

    def __init__(self, rules):
        """rules = this level's numbers from settings.LEVELS."""
        self.moves = rules["hitomi_moves"]
        self.speed = rules["hitomi_speed"]
        self.out_seconds = rules["hitomi_out_seconds"]
        self.pushes = rules["hitomi_pushes"]

        # x, y = top-left of her 16 x 16 picture in the room, in pixels.
        self.seat_x, self.seat_y = tile_pixels(layout.HITOMI_SEAT)
        self.door_x, self.door_y = tile_pixels(layout.HITOMI_DOOR)
        self.x, self.y = float(self.seat_x), float(self.seat_y)

        self.state = "desk"
        self.state_time = 0.0       # seconds in the current state
        self.time = 0.0             # seconds, for the animations
        self.gate_open = False
        self.facing = "down"
        self.moving = False
        self.walk_time = 0.0
        self.bubble_left = 0.0      # seconds her speech bubble still shows
        self.out_left = 0.0         # seconds she still stays out

        self.goal = None            # where she's walking to (top-left, pixels)
        self.stuck_time = 0.0       # seconds she's been stuck against something
        self.detour_left = 0.0      # seconds of walking to a random spot (to get unstuck)
        self.detour_goal = None
        self.chair = None           # Level 3: the chair she's going to (or standing on)
        self.on_chair_left = 0.0    # Level 3: seconds she still stands on it
        self.last_chair = None      # Level 3: the chair she stood on last

        self.events = []            # what happened this frame, for the sounds: "bubble", "gate_close", "push"

    # -----------------------------------------------------------------------
    # Asking about her
    # -----------------------------------------------------------------------
    @property
    def at_desk(self):
        return self.state == "desk"

    def hitbox(self):
        """She's solid: a 12 x 12 box in the middle of her picture."""
        margin = (settings.TILE_SIZE - settings.HITOMI_HITBOX) / 2
        return pygame.Rect(round(self.x + margin), round(self.y + margin),
                           settings.HITOMI_HITBOX, settings.HITOMI_HITBOX)

    def blocked_chair(self):
        """The chair she's standing on (nobody can sit there), or None."""
        return self.chair if self.on_chair_left > 0 else None

    # -----------------------------------------------------------------------
    # Every frame
    # -----------------------------------------------------------------------
    def come_out(self):
        """The bar reached one of her percents: the gate opens and out she comes."""
        self.go("exiting")
        self.gate_open = True
        self.facing = "down"

    def go(self, state):
        self.state = state
        self.state_time = 0.0

    def update(self, dt, student, solids):
        self.time += dt
        self.state_time += dt
        self.events = []
        self.bubble_left = max(0.0, self.bubble_left - dt)
        self.moving = False

        if self.state == "exiting":
            # Straight down through her gate. If you're standing right outside, she waits.
            if self.walk_straight(self.door_x, self.door_y, dt, student):
                self.go("pointing")
                self.bubble_left = settings.HITOMI_BUBBLE_SECONDS
                self.events.append("bubble")

        elif self.state == "pointing":
            if self.state_time >= settings.HITOMI_POINT_SECONDS:
                self.go("out")
                self.out_left = self.out_seconds
                self.goal = None

        elif self.state == "out":
            self.out_left -= dt
            if self.out_left <= 0:
                self.chair = None
                self.on_chair_left = 0.0
                self.go("returning")
            else:
                self.roam(dt, student, solids)

        elif self.state == "returning":
            if self.walk_to((self.door_x, self.door_y), dt, student, solids):
                self.go("entering")

        elif self.state == "entering":
            if self.walk_straight(self.seat_x, self.seat_y, dt, student):
                self.go("desk")
                self.gate_open = False
                self.events.append("gate_close")

        if self.moving:
            self.walk_time += dt
        else:
            self.walk_time = 0.0

    def roam(self, dt, student, solids):
        """Out in the room: move the way this level says."""
        if self.moves == "wander":
            if self.goal is None:
                self.goal = random_floor_spot()
            if self.walk_to(self.goal, dt, student, solids):
                self.goal = None                                # got there: pick another spot

        elif self.moves == "follow":
            self.walk_to((student.x, student.y), dt, student, solids)

        elif self.moves == "chairs":
            if self.on_chair_left > 0:
                self.on_chair_left -= dt                        # standing on a chair
                if self.on_chair_left <= 0:
                    self.last_chair, self.chair = self.chair, None
                return
            if self.chair is None:
                self.chair = self.chair_to_steal(student)
            if self.chair is not None:
                table, x, y, side, color = self.chair
                if self.walk_to((layout.to_pixels(x), layout.to_pixels(y)), dt, student, solids):
                    self.on_chair_left = settings.HITOMI_CHAIR_SECONDS

    def chair_to_steal(self, student):
        """Level 3: the free chair closest to the student (not the one she just left)."""
        student_x, student_y = student.center()
        best, best_distance = None, None
        for chair in layout.CHAIRS:
            if chair is student.chair or chair is self.last_chair:
                continue
            table, x, y, side, color = chair
            distance = math.hypot(layout.to_pixels(x) + 8 - student_x, layout.to_pixels(y) + 8 - student_y)
            if best is None or distance < best_distance:
                best, best_distance = chair, distance
        return best

    # -----------------------------------------------------------------------
    # Walking
    # -----------------------------------------------------------------------
    def walk_straight(self, goal_x, goal_y, dt, student):
        """In and out of her desk: a straight line, through the gate. She waits
        if the student is in the way. Returns True when she's there."""
        to_x, to_y = goal_x - self.x, goal_y - self.y
        distance = math.hypot(to_x, to_y)
        if distance < 0.5:
            self.x, self.y = float(goal_x), float(goal_y)
            return True
        step = min(self.speed * dt, distance)
        old = (self.x, self.y)
        self.x += to_x / distance * step
        self.y += to_y / distance * step
        if student.overlap_area(self.hitbox()) > 0:
            self.x, self.y = old                                # you're in the way: she waits
            return False
        self.moving = True
        self.face(to_x, to_y)
        return False

    def walk_to(self, goal, dt, student, solids):
        """Walk toward `goal` like the student walks: blocked by furniture (sliding
        along it) and never into the student. If she's stuck for a while she takes
        a short detour to a random spot. Returns True when she's there."""
        if self.detour_left > 0:
            self.detour_left -= dt
            goal = self.detour_goal
        goal_x, goal_y = goal
        to_x, to_y = goal_x - self.x, goal_y - self.y
        distance = math.hypot(to_x, to_y)
        if distance < 0.5:
            if self.detour_left > 0:
                self.detour_left = 0.0                          # detour spot reached: back to her goal
                return False
            return True

        step = min(self.speed * dt, distance)
        old = (self.x, self.y)
        self.move(to_x / distance * step, 0, student, solids)   # one direction at a time,
        self.move(0, to_y / distance * step, student, solids)   # so she slides along things
        moved = math.hypot(self.x - old[0], self.y - old[1])
        if moved > 0.01:
            self.moving = True
            self.face(self.x - old[0], self.y - old[1])

        # Stuck? (moving much less than she's trying to)
        if moved < step * 0.3:
            self.stuck_time += dt
            if self.stuck_time >= settings.HITOMI_STUCK_SECONDS:
                self.stuck_time = 0.0
                self.detour_left = settings.HITOMI_DETOUR_SECONDS
                self.detour_goal = random_floor_spot()
        else:
            self.stuck_time = 0.0
        return False

    def move(self, dx, dy, student, solids):
        """Try a small step. If it would put her into furniture or the student,
        she doesn't take it. Bumping a standing student pushes them (Levels 2-3)."""
        if dx == 0 and dy == 0:
            return
        self.x += dx
        self.y += dy
        box = self.hitbox()
        if any(box.colliderect(solid) for solid in solids):
            self.x -= dx
            self.y -= dy
            return
        if student.overlap_area(box) > 0:
            self.x -= dx
            self.y -= dy
            if self.pushes and not student.studying and not student.being_pushed:
                center = (self.x + settings.TILE_SIZE / 2, self.y + settings.TILE_SIZE / 2)
                student.push_away_from(center, settings.HITOMI_PUSH_DISTANCE, settings.HITOMI_PUSH_SECONDS)
                self.events.append("push")

    def face(self, dx, dy):
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        elif dy != 0:
            self.facing = "down" if dy > 0 else "up"

    # -----------------------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------------------
    def draw_gate(self, surface, sprites, camera_x, camera_y, view_top):
        picture = sprites["hitomi_desk_gate_open" if self.gate_open else "hitomi_desk_gate_closed"]
        draw_at_tile(surface, picture, layout.HITOMI_GATE, 0, camera_x, camera_y, view_top)

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        """Sitting at her desk (drawn before the student)."""
        if self.state != "desk":
            return
        frame = int(self.time * settings.HITOMI_WORK_FRAMES_PER_SECOND) % 2
        picture = sprites["hitomi_desk_work1" if frame == 0 else "hitomi_desk_work2"]
        draw_at_tile(surface, picture, layout.HITOMI_SEAT, layout.SITTING_LIFT,
                     camera_x, camera_y, view_top)

    def draw_walking(self, surface, sprites, camera_x, camera_y, view_top):
        """Walking around (drawn after the student)."""
        if self.state == "desk":
            return
        if self.state == "pointing":
            frame = int(self.time * settings.HITOMI_POINT_FRAMES_PER_SECOND) % 2
            name = "hitomi_point1" if frame == 0 else "hitomi_point2"
        elif self.moving:
            frame = int(self.walk_time * settings.WALK_FRAMES_PER_SECOND) % 2
            name = f"hitomi_{self.facing}_{'walk1' if frame == 0 else 'walk2'}"
        else:
            name = f"hitomi_{self.facing}_stand"
        surface.blit(sprites[name], (round(self.x) - camera_x, round(self.y) - camera_y + view_top))

    def draw_bubble(self, surface, font, sprites, camera_x, camera_y, view_top):
        if self.bubble_left <= 0:
            return
        speaker_x = self.x + settings.TILE_SIZE / 2 - camera_x
        speaker_top = round(self.y) - camera_y + view_top
        draw_speech_bubble(surface, font, sprites, HITOMI_LINES, speaker_x, speaker_top, view_top)


def tile_pixels(tile):
    return layout.to_pixels(tile[0]), layout.to_pixels(tile[1])


def random_floor_spot():
    """A random free floor tile (top-left, in pixels) for Hitomi to walk to."""
    return tile_pixels(random.choice(layout.floor_tiles()))
