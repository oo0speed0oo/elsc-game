# ELSC Game — the student you play (GAME_SPEC §5, §6 and §8).

import math

import pygame

import layout
import settings
import sprites as sprite_loader

# Where the hitbox sits inside the 16 x 16 sprite (centered).
HITBOX_OFFSET = (settings.TILE_SIZE - settings.STUDENT_HITBOX) / 2

# Extra info for the seated sprites: offset_from_chair and draw_chair_on_top.
SEATED_INFO = sprite_loader.read_json("students_seated_sheet")["sprites"]

# The book in the student's hands while studying (GAME_SPEC §17.7):
# book_<side> -> offset_from_seated (pixels from the seated sprite's position).
BOOK_INFO = sprite_loader.read_json("objects_v2_sheet")["sprites"]

# The Zelda-style hit flash (from effects_sheet.json): each sprite's 3 colors
# get swapped for these, switching every few frames.
_hit_flash = sprite_loader.read_json("effects_sheet")["hit_flash"]
FLASH_EVERY_FRAMES = _hit_flash["switch_every_frames"]
NORMAL_DARK = pygame.Color("#" + _hit_flash["normal"]["dark"])
NORMAL_SKIN = pygame.Color("#" + _hit_flash["normal"]["skin"])
FLASH_COLORS = [
    {part: pygame.Color("#" + _hit_flash[flash][part]) for part in ("dark", "skin", "blazer")}
    for flash in ("flash_1", "flash_2")
]

# Which way each arrow key moves you: (x change, y change, facing).
ARROW_KEYS = {
    pygame.K_LEFT:  (-1, 0, "left"),
    pygame.K_RIGHT: (1, 0, "right"),
    pygame.K_UP:    (0, -1, "up"),
    pygame.K_DOWN:  (0, 1, "down"),
}


class Student:
    def __init__(self, character):
        self.character = character      # "boy" or "girl"
        start_x, start_y = layout.STUDENT_START
        # x, y = top-left corner of the sprite in the room, in pixels.
        # They're decimals so slow, smooth movement isn't lost to rounding.
        self.x = float(layout.to_pixels(start_x))
        self.y = float(layout.to_pixels(start_y))
        self.facing = "down"
        self.moving = False
        self.walk_time = 0.0            # seconds spent walking, used for the walk animation

        # Studying
        self.meter = 0.0                # study points, 0 to BAR_MAX_POINTS
        self.chair = None               # the chair you're sitting on, or None
        self.study_time = 0.0           # seconds studied on this chair without a break
        self.bonus_rate = None          # this chair's bonus points per second, or None (no bonus)
        self.last_bonus_table = None    # the table where you last got a bonus
        self.just_sat = False           # True for the one frame you sit down (for the sound)
        self.bumped = []                # solid things your own walking ran into this frame

        # Getting hit
        self.knockback_left = 0.0       # seconds of knockback push still to go
        self.knockback_dir = (0.0, 0.0) # which way the push goes (length 1)
        self.knockback_speed = 0.0      # how fast the push moves you, in pixels per second
        self.invincible_left = 0.0      # seconds of flashing / invincibility still to go
        self.flash_frames = 0           # frames since the hit, for the flash colors
        self.flash_sprites = {}         # (sprite name, flash 1 or 2) -> recolored sprite

        # Power-ups
        self.coffee_left = 0.0          # seconds of coffee left: walk and study faster
        self.headphones_left = 0.0      # seconds of headphones left: clouds can't hit or notice you
        self.highlighter_left = 0.0     # seconds of highlighter left: every chair gives green-chair points
        self.second_points = 0.0        # points studied so far in the current second (for its pop-up)
        self.star_frames = 0            # frames since the headphones went on, for the blinking

    # -----------------------------------------------------------------------
    # Every frame
    # -----------------------------------------------------------------------
    def update(self, dt, keys, solids, blocked_chair=None):
        """Move with the arrow keys, then study if sitting still on a chair.
        dt = seconds since the last frame. Returns a list of pop-up values
        (1, 2 or 3) for each full second of studying that just finished."""
        self.just_sat = False
        self.bumped = []
        self.coffee_left = max(0.0, self.coffee_left - dt)
        self.highlighter_left = max(0.0, self.highlighter_left - dt)
        if self.headphones_left > 0:
            self.headphones_left = max(0.0, self.headphones_left - dt)
            self.star_frames += 1
        if self.invincible_left > 0:
            self.invincible_left -= dt
            self.flash_frames += 1

        if self.knockback_left > 0:
            # Being pushed back: no steering until the push is over.
            self.moving = False
            self.get_pushed(dt, solids)
        else:
            self.walk(dt, keys, solids)

        # No studying while moving, or while flashing after a hit.
        if self.moving or self.invincible:
            self.chair = None           # walking = standing up
            return []

        chair = self.find_chair(blocked_chair)
        if chair is None:
            self.chair = None
            return []
        if chair is not self.chair:
            self.sit_down(chair)
        return self.study(dt)

    # -----------------------------------------------------------------------
    # Walking
    # -----------------------------------------------------------------------
    def walk(self, dt, keys, solids):
        dx, dy = 0, 0
        pressed_facings = []
        for key, (kx, ky, facing) in ARROW_KEYS.items():
            if keys[key]:
                dx += kx
                dy += ky
                pressed_facings.append(facing)

        self.moving = (dx, dy) != (0, 0)
        if not self.moving:
            self.walk_time = 0.0
            return

        # Face the way you're going. When walking diagonally, keep your
        # current facing if it's one of the two keys held (like Zelda).
        if self.facing not in pressed_facings:
            if dx < 0:
                self.facing = "left"
            elif dx > 0:
                self.facing = "right"
            elif dy < 0:
                self.facing = "up"
            else:
                self.facing = "down"

        # Diagonals: shrink each part so the total speed stays the same.
        length = math.hypot(dx, dy)
        step = settings.STUDENT_SPEED * self.boost() * dt
        # Move one direction at a time so you slide along walls.
        # (Remember what you walked into: bumping the right bookshelf drops the pizza.)
        self.bumped = self.move_x(dx / length * step, solids) + self.move_y(dy / length * step, solids)

        self.walk_time += dt

    def move_x(self, amount, solids):
        """Move sideways, stopping at solid things. Returns the ones you ran into."""
        self.x += amount
        hit = []
        for solid in solids:
            if self.overlap_area(solid) > 0:
                hit.append(solid)
                if amount > 0:   # moving right: stop at the solid's left edge
                    self.x = solid.left - HITBOX_OFFSET - settings.STUDENT_HITBOX
                else:            # moving left: stop at its right edge
                    self.x = solid.right - HITBOX_OFFSET
        return hit

    def move_y(self, amount, solids):
        """Move up or down, stopping at solid things. Returns the ones you ran into."""
        self.y += amount
        hit = []
        for solid in solids:
            if self.overlap_area(solid) > 0:
                hit.append(solid)
                if amount > 0:   # moving down: stop at the solid's top edge
                    self.y = solid.top - HITBOX_OFFSET - settings.STUDENT_HITBOX
                else:            # moving up: stop at its bottom edge
                    self.y = solid.bottom - HITBOX_OFFSET
        return hit

    # -----------------------------------------------------------------------
    # Getting hit
    # -----------------------------------------------------------------------
    @property
    def invincible(self):
        return self.invincible_left > 0

    @property
    def wearing_headphones(self):
        return self.headphones_left > 0

    @property
    def noticeable(self):
        """Can the clouds notice you? Only while studying without headphones on."""
        return self.studying and not self.wearing_headphones

    def boost(self):
        """How much faster you walk and study right now (the coffee)."""
        return settings.COFFEE_BOOST if self.coffee_left > 0 else 1

    def get_hit(self, tornado_center, damage, invincible_seconds):
        """The tornado touched you: lose `damage` points, get pushed away, and flash
        (safe from more hits) for `invincible_seconds`."""
        self.meter = max(0, self.meter - damage)
        self.chair = None
        self.invincible_left = invincible_seconds
        self.flash_frames = 0

        self.push_away_from(tornado_center, settings.KNOCKBACK_DISTANCE, settings.KNOCKBACK_SECONDS)

    def push_away_from(self, center, distance, seconds):
        """Start a push straight away from `center`: `distance` pixels over `seconds`.
        You can't steer while it lasts. Used by cloud hits and by Hitomi."""
        center_x, center_y = self.center()
        away_x = center_x - center[0]
        away_y = center_y - center[1]
        length = math.hypot(away_x, away_y)
        if length == 0:
            # Exactly on top of each other: push the way you're facing, backwards.
            facing_x, facing_y = {"left": (-1, 0), "right": (1, 0),
                                  "up": (0, -1), "down": (0, 1)}[self.facing]
            away_x, away_y, length = -facing_x, -facing_y, 1
        self.knockback_dir = (away_x / length, away_y / length)
        self.knockback_left = seconds
        self.knockback_speed = distance / seconds

    @property
    def being_pushed(self):
        return self.knockback_left > 0

    def get_pushed(self, dt, solids):
        push_time = min(dt, self.knockback_left)
        self.knockback_left -= push_time
        distance = self.knockback_speed * push_time
        # move_x / move_y stop at solid things, so you're never pushed into furniture.
        self.move_x(self.knockback_dir[0] * distance, solids)
        self.move_y(self.knockback_dir[1] * distance, solids)

    def flashed(self, sprites, name):
        """The sprite to draw right now: normal, or with flash colors while invincible
        (after a hit) or while wearing the headphones (the Mario-star blink)."""
        if self.wearing_headphones:
            every = settings.STAR_BLINK_EVERY_FRAMES
            if self.headphones_left <= settings.STAR_FAST_BLINK_SECONDS:
                every = settings.STAR_FAST_BLINK_EVERY_FRAMES      # hurry: they're running out
            step = (self.star_frames // every) % 3
        elif self.invincible:
            step = (self.flash_frames // FLASH_EVERY_FRAMES) % 3   # 0 = normal, 1 = flash_1, 2 = flash_2
        else:
            return sprites[name]
        if step == 0:
            return sprites[name]
        if (name, step) not in self.flash_sprites:
            self.flash_sprites[(name, step)] = recolor(sprites[name], FLASH_COLORS[step - 1])
        return self.flash_sprites[(name, step)]

    # -----------------------------------------------------------------------
    # Studying
    # -----------------------------------------------------------------------
    def find_chair(self, blocked_chair=None):
        """The chair your hitbox touches the most, or None. You can't sit on
        `blocked_chair` (Hitomi is standing on it)."""
        best, best_area = None, 0
        for chair in layout.CHAIRS:
            if chair is blocked_chair:
                continue
            area = self.overlap_area(chair_rect(chair))
            if area > best_area:
                best, best_area = chair, area
        return best

    def sit_down(self, chair):
        self.chair = chair
        self.just_sat = True
        self.study_time = 0.0
        self.second_points = 0.0
        table, x, y, side, color = chair
        if table != self.last_bonus_table:
            # A different table than last time: you get the bonus.
            self.bonus_rate = settings.CHAIR_BONUS[color]
            self.last_bonus_table = table
        else:
            self.bonus_rate = None

    def points_after(self, seconds):
        """Total points earned after studying this many seconds on this chair."""
        base = settings.CHARGE_POINTS_PER_SECOND
        if self.bonus_rate is None:
            return base * seconds
        bonus_part = min(seconds, settings.BONUS_SECONDS)
        normal_part = max(0, seconds - settings.BONUS_SECONDS)
        return self.bonus_rate * bonus_part + base * normal_part

    @property
    def highlighting(self):
        return self.highlighter_left > 0

    def study(self, dt):
        before = self.study_time
        after = before + dt
        self.study_time = after

        # Points this frame: the highlighter's rate while it's on, otherwise
        # the chair's normal rate (with its bonus for the first 2 seconds).
        if self.highlighting:
            points = settings.HIGHLIGHTER_POINTS_PER_SECOND * dt
        else:
            points = self.points_after(after) - self.points_after(before)

        # Fill the meter smoothly (the coffee makes it faster), but never past full.
        self.meter = min(self.meter + points * self.boost(), settings.BAR_MAX_POINTS)

        # One pop-up for each full second that just finished: 1, 2 or 3 for
        # normal, double or triple speed that second (+1 / +2 / +3). The coffee
        # doesn't change which pop-up shows.
        self.second_points += points
        popups = []
        for second in range(int(before) + 1, int(after) + 1):
            popups.append(max(1, round(self.second_points / settings.CHARGE_POINTS_PER_SECOND)))
            self.second_points = 0.0
        return popups

    @property
    def studying(self):
        return self.chair is not None

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def hitbox(self):
        """The hitbox as (left, top, right, bottom) in room pixels."""
        left = self.x + HITBOX_OFFSET
        top = self.y + HITBOX_OFFSET
        return left, top, left + settings.STUDENT_HITBOX, top + settings.STUDENT_HITBOX

    def overlap_area(self, rect):
        """How many square pixels the hitbox overlaps the rectangle (0 = not touching)."""
        left, top, right, bottom = self.hitbox()
        width = min(right, rect.right) - max(left, rect.left)
        height = min(bottom, rect.bottom) - max(top, rect.top)
        if width <= 0 or height <= 0:
            return 0
        return width * height

    def center(self):
        half = settings.TILE_SIZE / 2
        return self.x + half, self.y + half

    # -----------------------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------------------
    def sprite_and_position(self):
        """Which sprite to draw and where its top-left goes in the room."""
        if self.studying:
            table, cx, cy, side, color = self.chair
            frame = int(self.study_time * settings.READ_FRAMES_PER_SECOND) % 2
            name = f"{self.character}_seat_{side}_{'read1' if frame == 0 else 'read2'}"
            offset_x, offset_y = SEATED_INFO[name]["offset_from_chair"]
            return name, layout.to_pixels(cx) + offset_x, layout.to_pixels(cy) + offset_y

        if self.moving:
            frame = int(self.walk_time * settings.WALK_FRAMES_PER_SECOND) % 2
            pose = "walk1" if frame == 0 else "walk2"
        else:
            pose = "stand"
        return f"{self.character}_{self.facing}_{pose}", round(self.x), round(self.y)

    def draw(self, surface, sprites, camera_x, camera_y, view_top):
        name, room_x, room_y = self.sprite_and_position()
        surface.blit(self.flashed(sprites, name), (room_x - camera_x, room_y - camera_y + view_top))

        # For S chairs the chair is drawn again on top, so its backrest
        # hides the student's back.
        if self.studying and SEATED_INFO[name]["draw_chair_on_top"]:
            table, cx, cy, side, color = self.chair
            chair_name = layout.chair_sprite_name(self.chair, self.highlighting)
            surface.blit(sprites[chair_name], (layout.to_pixels(cx) - camera_x,
                                               layout.to_pixels(cy) - camera_y + view_top))

        # The book goes over the seated student (on the table for S chairs).
        if self.studying:
            side = self.chair[3]
            book = f"book_{side}"
            offset_x, offset_y = BOOK_INFO[book]["offset_from_seated"]
            if self.highlighting and int(self.highlighter_left * settings.BOOK_BLINKS_PER_SECOND) % 2:
                book = f"book_{side}_green"             # the highlighter: the book blinks green
            surface.blit(sprites[book], (room_x + offset_x - camera_x,
                                         room_y + offset_y - camera_y + view_top))


def chair_rect(chair):
    table, x, y, side, color = chair
    return pygame.Rect(layout.to_pixels(x), layout.to_pixels(y),
                       settings.TILE_SIZE, settings.TILE_SIZE)


def recolor(sprite, colors):
    """A copy of a student sprite with its 3 colors swapped: black -> colors["dark"],
    skin -> colors["skin"], and the blazer (the other color) -> colors["blazer"]."""
    copy = sprite.copy()
    for x in range(copy.get_width()):
        for y in range(copy.get_height()):
            pixel = copy.get_at((x, y))
            if pixel.a == 0:
                continue
            rgb = pygame.Color(pixel.r, pixel.g, pixel.b)
            if rgb == NORMAL_DARK:
                new = colors["dark"]
            elif rgb == NORMAL_SKIN:
                new = colors["skin"]
            else:
                new = colors["blazer"]
            copy.set_at((x, y), (new.r, new.g, new.b, pixel.a))
    return copy
