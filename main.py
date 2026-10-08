# ELSC Game — starts the game and runs the game loop.
# The same file runs on the desktop (python main.py) and in a web browser
# (built with pygbag). The browser needs the loop to be "async": once every
# frame it hands control back to the browser with `await asyncio.sleep(0)`.

import asyncio
import math
import sys
import time

import pygame

import highscores
import layout
import settings
import sprites as sprite_loader
from effects import NoiseBubble, PlusPopup
from font import YELLOW, Font
from hud import draw_hud
from items import Item, Pizza
from online import Online, new_session
from people import Haruna, Hitomi
import letter_grid
from menus import (CHARACTERS, CODE_MAX_LETTERS, LEVEL_COLORS, OPTION_CHOICES, PAUSE_CHOICES,
                   TITLE_CHOICES, character_tap_areas, draw_character_select, draw_click_to_play,
                   draw_level_select, draw_options, draw_pause, draw_stage_code, draw_stage_intro,
                   draw_title, level_tap_areas, option_tap_areas, pause_tap_areas, title_tap_areas)
from shell import Shell
from screens import (draw_course_complete, draw_deadline_extended, draw_high_scores, draw_results,
                     draw_score, draw_times_up, high_scores_arrow_areas, letters_typed, make_confetti,
                     results_lines)
from sound import Sound, start_mixer
from student import Student
from tornado import Tornado
from touch import HeldKeys, Stick
from view import View

# True when the game runs in a web browser (pygbag).
WEB = sys.platform == "emscripten"
def in_hud(pos):
    """Is this spot (game pixels) on the HUD bar at the top of the game?"""
    return 0 <= pos[0] < settings.NES_WIDTH and 0 <= pos[1] < settings.HUD_HEIGHT


FINGER_EVENTS = {pygame.FINGERDOWN: "down", pygame.FINGERMOTION: "move", pygame.FINGERUP: "up"}

ENTER_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)

# The number pad's keys (their key numbers aren't in order, so we list them).
NUMBER_PAD = {getattr(pygame, f"K_KP{n}"): str(n) for n in range(10)}

# The screens where the main theme plays (Options too, when opened from the title).
MENU_STATES = ("title", "options", "stage_code", "level_select", "character_select", "high_scores")

LEVELS = list(settings.LEVELS)       # [1, 2, 3], in the order shown on level select

# Debug keys (only when settings.DEBUG_KEYS is True): jump to a stage of the current level.
DEBUG_STAGE_KEYS = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4, pygame.K_5: 5}


def camera_position(student, view_width, view_height, room_width, room_height):
    """Top-left of the camera in the room: centered on the student, but
    never past the room's edges."""
    center_x, center_y = student.center()
    camera_x = round(center_x - view_width / 2)
    camera_y = round(center_y - view_height / 2)
    camera_x = max(0, min(camera_x, room_width - view_width))
    camera_y = max(0, min(camera_y, room_height - view_height))
    return camera_x, camera_y


def stage_count(level):
    """How many stages a level has (3 or 5)."""
    return len(settings.LEVELS[level]["round_seconds"])


class Round:
    """One round of one stage of one level: the student, the noise clouds, the
    timer and the effects on screen. A new Round = a fresh start."""

    def __init__(self, level, stage, character):
        self.level = level                  # 1, 2 or 3
        self.stage = stage                  # 1 to 3 (Level 1) or 1 to 5 (Levels 2 and 3)
        self.last_stage = stage_count(level)
        rules = settings.LEVELS[level]      # this level's numbers from settings.py
        i = stage - 1                       # lists in LEVELS start at 0 for stage 1
        self.hit_damage = rules["hit_damage"]
        self.invincible_seconds = rules["invincible_seconds"]
        self.score_multiplier = rules["score_multiplier"]
        self.pass_mark = rules["pass_marks"][i]
        self.hurry_music_at = rules["hurry_music_at"]
        self.student = Student(character)   # starts at V2 with an empty meter
        self.haruna = Haruna()              # sits at her desk
        self.hitomi = Hitomi(rules)         # sits inside her desk until the bar reaches her percents
        self.hitomi_percents = list(rules["hitomi_comes_out_at"])   # the ones that haven't happened yet
        # This stage's noise clouds, each at its own start tile.
        count = rules["clouds"][i]
        self.tornadoes = [Tornado(rules["cloud_sizes"][i], rules["cloud_speed"][i],
                                  rules["notice_seconds"], rules["keep_chasing_seconds"], start)
                          for start in layout.TORNADO_STARTS[:count]]
        self.popups = []                    # the "+1 / +2 / +3" pop-ups on screen
        self.bubbles = []                   # the tornado's noise bubbles on screen
        self.round_seconds = rules["round_seconds"][i]
        self.seconds_left = self.round_seconds
        # Power-ups waiting to be grabbed, by name. New every stage (and on Restart).
        self.power_ups = rules["power_ups"]     # which ones this level has
        self.items = {}
        if "coffee" in self.power_ups:
            self.items["coffee"] = Item("coffee", "item_coffee", *layout.COFFEE_ITEM_PIXEL)
        if "laptop" in self.power_ups:
            self.items["laptop"] = Item("laptop", "item_laptop", *layout.LAPTOP_PIXEL,
                                        table=layout.table_rect(layout.LAPTOP_TABLE))
        if "highlighter" in self.power_ups:
            self.items["highlighter"] = Item("highlighter", "item_highlighter", *layout.HIGHLIGHTER_PIXEL,
                                             table=layout.table_rect(layout.HIGHLIGHTER_TABLE))
        self.pizza = Pizza() if "pizza" in self.power_ups else None
        self.pizza_shelf = layout.shelf_rect(layout.PIZZA_SHELF)
        self.headphones_checked = False     # Haruna checks on you once, at half time
        self.deadline_extended = False      # True when the laptop was just grabbed (the Game takes over)
        self.frame_count = 0                # counts frames, for things that change every few frames

    def time_is_up(self):
        return self.seconds_left <= 0

    def stage_score(self, passed):
        """(bar points x 10, + 1000 if passed) x the level's multiplier. Rounded down."""
        points = int(self.student.meter)
        bonus = settings.PASS_BONUS if passed else 0
        return (points * settings.SCORE_PER_POINT + bonus) * self.score_multiplier

    def passed(self):
        """Did you study enough? Compare the bar (in percent) with the pass mark."""
        percent = self.student.meter / settings.BAR_MAX_POINTS * 100
        return percent >= self.pass_mark

    def update(self, dt, keys, solids, sprites, sound):
        # When the timer reaches 0 everything freezes.
        if self.time_is_up():
            return
        self.seconds_left = max(0, self.seconds_left - dt)
        self.frame_count += 1

        self.haruna.update(dt)
        if self.haruna.just_called:
            sound.play("sfx_cursor")                    # a speech bubble appears
        self.check_on_student(sound)

        # The student. While Hitomi is out she's solid too, and nobody can sit
        # on the chair she's standing on.
        student = self.student
        hitomi = self.hitomi
        solids_now = solids if hitomi.at_desk else solids + [hitomi.hitbox()]
        meter_before = student.meter
        for points in student.update(dt, keys, solids_now, hitomi.blocked_chair()):
            name, sprite_x, sprite_y = student.sprite_and_position()
            self.popups.append(PlusPopup(points, sprite_x, sprite_y))
            sound.play("sfx_cursor" if points == 1 else "sfx_select")   # +1 blips, +2 / +3 chirp
        if student.just_sat:
            sound.play("sfx_select")
        if meter_before < settings.BAR_MAX_POINTS <= student.meter:
            sound.play("jingle_ready")                  # the study bar just got full

        # Hitomi comes out the first time the bar reaches each of her percents
        # (skipped if she's already out). Then she does her thing.
        percent = student.meter / settings.BAR_MAX_POINTS * 100
        for mark in [m for m in self.hitomi_percents if percent >= m]:
            self.hitomi_percents.remove(mark)
            if hitomi.at_desk:
                hitomi.come_out()
                sound.play("sfx_select")                # her gate opens
        hitomi.update(dt, student, solids)
        for event in hitomi.events:
            if event == "bubble":
                sound.play("sfx_cursor")                # "DID YOU STUDY?!"
            elif event == "gate_close":
                sound.play("sfx_cursor")
            elif event == "push":
                sound.play("jingle_failed", settings.PUSH_SOUND_SECONDS)

        # The pizza (Level 3): bump the right bookshelf and it drops behind it.
        pizza_spot = None
        if self.pizza is not None:
            if self.pizza.state == "waiting" and self.pizza_shelf in student.bumped:
                self.pizza.knock_off()
                sound.play("jingle_failed", settings.PIZZA_BUMP_SOUND_SECONDS)   # bonk
            self.pizza.update(dt)
            pizza_spot = self.pizza.lure()
            if self.pizza.just_eaten:
                # It vanishes in a burst of noise bubbles, and the clouds go back to normal.
                count = settings.BUBBLES_ON_LUNGE
                for i in range(count):
                    shift_x = (i - (count - 1) / 2) * settings.BURST_SPREAD_PIXELS
                    self.bubbles.append(NoiseBubble(sprites, self.pizza.x + settings.TILE_SIZE / 2,
                                                    self.pizza.y, shift_x, -i * settings.BURST_STEP_UP_PIXELS))
                sound.play("sfx_cursor")

        # Every cloud moves on its own. They all watch the same student, so
        # they all notice (and give up) at the same moment. While the pizza is
        # open they all go to it instead.
        for tornado in self.tornadoes:
            self.bubbles += tornado.update(dt, sprites, student, pizza_spot)
        if any(tornado.just_noticed for tornado in self.tornadoes):
            sound.play("jingle_drumroll", settings.NOTICE_SOUND_SECONDS)   # once, however many clouds

        # Power-ups: grab one by touching it.
        for name, item in list(self.items.items()):
            item.update(dt)
            if item.touched_by(student):
                self.grab(name, sound)

        # Getting hit: one hit at a time. The first cloud touching you hits;
        # after that you're flashing, so the others can't. With the headphones
        # on, the clouds pass right through you. (Clouds float over Hitomi.)
        for tornado in self.tornadoes:
            if student.wearing_headphones:
                break
            if not student.invincible and student.overlap_area(tornado.hitbox()) > 0:
                student.get_hit(tornado.center(), self.hit_damage, self.invincible_seconds)
                sound.play("jingle_failed", settings.HIT_SOUND_SECONDS)   # bonk

        for effect in self.popups + self.bubbles:
            effect.update(dt)
        self.popups = [p for p in self.popups if not p.finished()]
        self.bubbles = [b for b in self.bubbles if not b.finished()]

    def check_on_student(self, sound):
        """Half time: if the bar is under 50%, Haruna drops the headphones (once per stage)."""
        time_gone = self.round_seconds - self.seconds_left
        if self.headphones_checked or time_gone < self.round_seconds * settings.HEADPHONES_CHECK_AT:
            return
        self.headphones_checked = True
        percent = self.student.meter / settings.BAR_MAX_POINTS * 100
        if "headphones" in self.power_ups and percent < settings.HEADPHONES_IF_BAR_UNDER:
            self.haruna.toss()
            tile_x, tile_y = layout.HEADPHONES_TILE
            self.items["headphones"] = Item("headphones", "item_headphones",
                                            layout.to_pixels(tile_x), layout.to_pixels(tile_y))
            sound.play("sfx_select")                    # a power-up appears

    def grab(self, name, sound):
        """The student grabbed a power-up: it disappears and does its thing."""
        del self.items[name]
        sound.play("jingle_passed", settings.POWERUP_SOUND_SECONDS)
        if name == "coffee":
            self.student.coffee_left = settings.COFFEE_SECONDS
        elif name == "headphones":
            self.student.headphones_left = settings.HEADPHONES_SECONDS
            self.student.star_frames = 0
        elif name == "laptop":
            self.deadline_extended = True       # the Game freezes play and adds the time
        elif name == "highlighter":
            self.student.highlighter_left = settings.HIGHLIGHTER_SECONDS

    def draw(self, screen, room, font, sprites, timer_color=None):
        view_width = settings.NES_WIDTH
        view_height = settings.NES_HEIGHT - settings.HUD_HEIGHT
        camera_x, camera_y = camera_position(self.student, view_width, view_height,
                                             room.get_width(), room.get_height())
        top = settings.HUD_HEIGHT

        # Back to front (GAME_SPEC §14).
        screen.fill((0, 0, 0))
        screen.blit(room, (0, top), pygame.Rect(camera_x, camera_y, view_width, view_height))
        if self.student.highlighting:
            # The highlighter: every chair is drawn green while it lasts.
            for chair in layout.CHAIRS:
                table, x, y, side, color = chair
                screen.blit(sprites[layout.chair_sprite_name(chair, True)],
                            (layout.to_pixels(x) - camera_x, layout.to_pixels(y) - camera_y + top))
        self.hitomi.draw_gate(screen, sprites, camera_x, camera_y, top)
        for item in self.items.values():
            item.draw(screen, sprites, camera_x, camera_y, top)
        if self.pizza is not None:
            self.pizza.draw(screen, sprites, camera_x, camera_y, top)
        self.haruna.draw(screen, sprites, camera_x, camera_y, top)
        self.hitomi.draw(screen, sprites, camera_x, camera_y, top)
        self.student.draw(screen, sprites, camera_x, camera_y, top)
        self.hitomi.draw_walking(screen, sprites, camera_x, camera_y, top)
        for tornado in self.tornadoes:
            tornado.draw(screen, camera_x, camera_y, top)
        for effect in self.bubbles + self.popups:
            effect.draw(screen, sprites, camera_x, camera_y, top)
        self.haruna.draw_bubble(screen, font, sprites, camera_x, camera_y, top)
        self.hitomi.draw_bubble(screen, font, sprites, camera_x, camera_y, top)
        draw_hud(screen, font, sprites, self.level, LEVEL_COLORS[self.level], self.stage,
                 self.student.character, self.seconds_left,
                 self.student.meter, self.student.studying and not self.time_is_up(),
                 self.frame_count, timer_color)


class Game:
    """The whole game: which screen we're on, and what each screen does.

    Screens (self.state), in play order:
      "click_to_play"    - web only: wait for a click (browsers block sound and keys until then)
      "title"            - START / HIGH SCORES / OPTIONS / STAGE CODE
      "options"          - MUSIC and SOUND FX volume (also the pause menu's SOUND)
      "stage_code"       - type a code to start at Stage 2 or 3
      "level_select"     - LEVEL 1 / 2 / 3
      "character_select" - boy or girl
      "stage_intro"      - STAGE N, READY, SET, STUDY!
      "play"             - playing a round (Esc pauses)
      "pause"            - the pause box over the frozen round
      "deadline"         - the laptop: frozen, DEADLINE EXTENDED!, the timer counts up +10
      "times_up"         - frozen, with the TIME'S UP! banner
      "results"          - the test: PASSED! or FAILED...
      "course_complete"  - YOU PASSED THE COURSE!!!
      "score"            - after every run: YOU SCORED (and your name if it's a high score),
                           then SAVED! with the top 10 when the score server has it
      "high_scores"      - the top 10 of each level (online if there's a score server)
    """

    def __init__(self, sprites, font, room, solids, touch=False):
        self.sprites, self.font, self.room, self.solids = sprites, font, room, solids
        self.touch = touch          # touch mode (phones) or keyboard mode (GAME_SPEC §19.1)
        self.last_touch = -100.0    # when the last touch happened (time.monotonic())
        self.stick = Stick()        # phones: the "slide anywhere" stick (§19.3)
        self.finger_starts = {}     # finger -> where it went down (to tell taps from slides)
        self.grid_flash = None      # the letter grid: the cell just tapped (flashes yellow)
        self.grid_flash_left = 0.0  # ...for this many more seconds
        self.grid_cursor = 0        # the letter grid: the cell the Study Pocket's slide pad is on
        self.shell = None           # the Study Pocket (a Shell) while it's showing, else None (§19.8)
        self.skin_height = 0        # ...and how tall it is (skin pixels)
        self.button_fingers = {}    # finger -> the Study Pocket button it's on
        self.menu_key = None        # Study Pocket: the arrow the slide pad is holding in a menu
        self.menu_repeat_left = 0.0 # ...and when it moves the cursor again
        self.title_cloud = sprite_loader.load_frames("noise_tornado_stage1")
        self.level_clouds = {1: self.title_cloud,           # the little clouds on level select
                             2: sprite_loader.load_frames("noise_tornado_stage2"),
                             3: sprite_loader.load_frames("noise_tornado_stage3")}
        self.character = "boy"
        self.level = 1              # the level for this run (all its stages)
        self.round = None           # the Round being played
        self.passed = False         # the test result, worked out when time's up
        self.confetti = []
        self.menu_choice = 0        # which line of a menu the cursor is on
        self.deadline_ticks = 0     # seconds added so far by the laptop
        self.first_stage = 1        # the stage the next game starts at (a stage code changes it)
        self.stage_score = 0        # the score for the stage just tested
        self.run_score = 0          # all the stage scores of this run added up
        self.level_complete = False # did this run finish its level?
        self.new_high = False       # does this run's score make the level's top 10?
        self.name = ""              # the name being typed for a high score
        self.high_scores = highscores.load()      # the lists on this computer
        self.scores_level = 1       # which level the HIGH SCORES screen shows
        self.online = Online()      # the score server (does nothing if SCORE_SERVER_URL is "")
        if self.online.enabled:
            self.online.wake_up()   # wake the score server now, so it's ready later
        self.session = ""           # this run's random id (the server needs it to save a score)
        self.device = "computer"    # "phone" if this run started in touch mode
        self.board_request = None   # HIGH SCORES: the question to the server for the list
        self.board_status = "local" # HIGH SCORES: "local", "loading", "online" or "offline"
        self.board_entries = []     # HIGH SCORES: the list being shown
        self.score_phase = "decided"   # score screen: "checking", "decided", "saving", "saved", "could_not_save"
        self.score_request = None   # score screen: the question to the server (top 10, then save)
        self.announced = False      # score screen: NEW HIGH SCORE! (or PRESS ENTER) is showing
        self.saved_here = False     # score screen: saved on this computer after COULD NOT SAVE
        self.saved_entries, self.saved_rank = [], None   # score screen: the list after SAVED!
        self.fail_counts = {}       # (level, stage) -> fails while the game runs
        self.typed_code = ""        # letters typed on the stage code screen
        self.wrong_code = False     # show WRONG CODE!
        self.music_volume = settings.MUSIC_VOLUME_START          # 0 to VOLUME_MAX
        self.sound_fx_volume = settings.SOUND_FX_VOLUME_START    # 0 to VOLUME_MAX
        self.sound = Sound(self.music_volume, self.sound_fx_volume)
        self.options_back_to = "title"   # where BACK goes: "title" or "pause"
        self.go("click_to_play" if WEB else "title")

    def go(self, state):
        """Switch to another screen."""
        self.state = state
        self.state_time = 0.0       # seconds on this screen
        self.stick.lift()           # a new screen: the thumb has to go down again to steer
        self.grid_cursor = 0        # the letter grid starts on "A"
        self.menu_choice = 0
        self.screen_sounds()

    def screen_sounds(self):
        """The music (and jingle) for the screen we just switched to."""
        from_pause = self.state == "options" and self.options_back_to == "pause"
        if self.state in MENU_STATES and not from_pause:
            self.sound.play_music("main_theme")         # keeps going between menus
        elif self.state == "stage_intro":
            self.sound.fade_out_music(settings.THEME_FADE_SECONDS)
            self.sound.play("jingle_ready")             # "ready, set, STUDY!"
        elif self.state == "play":
            self.sound.play_music("stage_music", restart=True)
        elif self.state == "pause":
            self.sound.pause_music()
        elif self.state == "times_up":
            self.sound.stop_music()
        elif self.state == "course_complete":
            self.sound.play_music("victory_song", restart=True)
        elif self.state == "score":
            self.sound.play("jingle_ready")             # the score appears

    def back(self):
        """Esc to go back (a blip)."""
        self.sound.play("sfx_cursor")

    def start_stage(self, stage):
        """A fresh round of this stage (full timer, empty meter), after its intro."""
        self.round = Round(self.level, stage, self.character)
        self.go("stage_intro")

    # -----------------------------------------------------------------------
    # Keys
    # -----------------------------------------------------------------------
    def move_cursor(self, key, choices):
        """Up/down moves a menu cursor (with a blip)."""
        if key == pygame.K_UP:
            self.menu_choice = (self.menu_choice - 1) % len(choices)
            self.sound.play("sfx_cursor")
        elif key == pygame.K_DOWN:
            self.menu_choice = (self.menu_choice + 1) % len(choices)
            self.sound.play("sfx_cursor")

    def choose(self):
        """Something was chosen with Enter (a chirp)."""
        self.sound.play("sfx_select")

    def handle_click(self, pos):
        """A mouse click; pos is in game pixels. Only used by the CLICK TO PLAY
        screen so far. A real mouse click means keyboard mode (§19.1)."""
        if time.monotonic() - self.last_touch < settings.TOUCH_MOUSE_IGNORE_SECONDS:
            return                          # the pretend click a phone sends after a touch
        self.touch = False
        if self.state == "click_to_play":
            self.go("title")                # sound is allowed now: the theme starts

    def handle_finger(self, kind, finger, pos, frame_pos=None):
        """A touch: kind is "down", "move" or "up", finger is which finger,
        pos is in game pixels (below the game, y is more than 240) and frame_pos
        in frame pixels (where the Study Pocket's buttons are). Any touch means
        touch mode (§19.1). Taps count when the finger lifts."""
        self.touch = True
        self.last_touch = time.monotonic()
        if kind == "down":
            button = self.shell.button_at(frame_pos, self.skin_height) if self.shell else None
            if button:
                self.button_fingers[finger] = button    # drawn pressed until the finger lifts
                self.press_button(button)
                return
            self.finger_starts[finger] = pos
            if self.state == "play" and not in_hud(pos):
                self.stick.press(finger, pos)           # steer from here
            elif self.state != "play" and self.shell:
                self.stick.press(finger, pos)           # Study Pocket: slide to move menu cursors
        elif kind == "move":
            self.stick.slide(finger, pos)
        elif kind == "up":
            if self.button_fingers.pop(finger, None):
                return
            self.stick.lift(finger)                     # stop (and sit if on a chair)
            start = self.finger_starts.pop(finger, None)
            tap = start is not None and math.dist(start, pos) < settings.TOUCH_TAP_MAX_MOVE
            if self.state == "click_to_play":
                self.go("title")                # sound is allowed now: the theme starts
            elif tap:
                self.handle_tap(pos)

    def handle_tap(self, pos):
        """A tap (the finger lifted without sliding), pos in game pixels. Taps
        do what the keys do (§19.4): tapping a menu item = moving the cursor
        there and pressing Enter."""
        state = self.state
        if state == "play":
            if in_hud(pos):
                self.pause_game()               # tap the HUD bar to pause
        elif state == "title":
            self.tap_choice(pos, title_tap_areas())
        elif state == "level_select":
            self.tap_choice(pos, level_tap_areas())
        elif state == "character_select":
            self.tap_choice(pos, character_tap_areas())
        elif state == "pause":
            self.tap_choice(pos, pause_tap_areas())
        elif state == "options":
            self.tap_options(pos)
        elif state == "high_scores":
            left, right = high_scores_arrow_areas()
            if left.collidepoint(pos):
                self.press(pygame.K_LEFT)
            elif right.collidepoint(pos):
                self.press(pygame.K_RIGHT)
            else:
                self.press(pygame.K_ESCAPE)     # anywhere else = back
        elif state == "stage_code":
            self.tap_grid(pos, codes=True)
        elif state == "score":
            if self.score_phase == "decided" and self.new_high and self.announced:
                self.tap_grid(pos)              # typing a name
            else:
                self.press(pygame.K_RETURN)     # a tap anywhere = Enter
        elif state == "course_complete":
            self.press(pygame.K_RETURN)

    def tap_choice(self, pos, areas):
        """If a menu item was tapped, put the cursor on it and choose it."""
        for i, area in enumerate(areas):
            if area.collidepoint(pos):
                self.menu_choice = i
                self.press(pygame.K_RETURN)
                return

    def tap_options(self, pos):
        """Options: tap a volume block to set the volume there, or tap BACK.
        Tapping the first block again when it's the only one lit turns it off (0)."""
        for line, block, area in option_tap_areas():
            if not area.collidepoint(pos):
                continue
            self.menu_choice = line
            if OPTION_CHOICES[line] == "BACK":
                self.press(pygame.K_RETURN)
                return
            if block is not None:
                volume = block + 1
                current = self.music_volume if line == 0 else self.sound_fx_volume
                if volume == current == 1:
                    volume = 0
                if line == 0:
                    self.music_volume = volume
                    self.sound.set_music_volume(volume)
                else:
                    self.sound_fx_volume = volume
                    self.sound.set_fx_volume(volume)
            self.sound.play("sfx_cursor")
            return

    def tap_grid(self, pos, codes=False):
        """The letter grid (§19.5): a tapped cell works like its key."""
        value = letter_grid.tapped(pos, codes)
        if value is not None:
            self.grid_input(value, codes)

    def grid_codes(self):
        """Is the letter grid showing? None = no; True = for a stage code
        (letters only); False = for a name."""
        if not self.touch:
            return None
        if self.state == "stage_code":
            return True
        if self.state == "score" and self.score_phase == "decided" and self.new_high and self.announced:
            return False
        return None

    def grid_input(self, value, codes):
        """A grid cell was tapped (or chosen with OK): flash it and do what its key does."""
        self.grid_flash, self.grid_flash_left = value, settings.GRID_FLASH_SECONDS
        if value == "OK":
            self.press(pygame.K_RETURN)
        elif value == "DEL":
            if codes and not self.typed_code:
                self.press(pygame.K_ESCAPE)     # nothing left to delete: back to the title
            else:
                self.press(pygame.K_BACKSPACE)
        elif value == " ":
            self.press(pygame.K_SPACE)
        else:
            self.press(ord(value.lower()))      # pygame's key numbers are the characters

    def press_button(self, name):
        """A Study Pocket button went down (§19.8)."""
        codes = self.grid_codes()
        if name == "sound":
            self.sound.set_muted(not self.sound.muted)   # stays until the page closes
        elif name == "ok":
            if codes is not None:
                self.grid_input(letter_grid.value_at(self.grid_cursor, codes), codes)   # type that cell
            else:
                self.press(pygame.K_RETURN)
        elif name == "back":
            if codes is not None:
                self.grid_input("DEL", codes)           # delete a letter (an empty code: back)
            elif self.state not in ("play", "click_to_play"):
                self.press(pygame.K_ESCAPE)
        elif name == "pause":
            if self.state == "play":
                self.pause_game()
            elif self.state == "pause":
                self.press(pygame.K_ESCAPE)             # close the pause menu

    def slide_step(self, key):
        """Study Pocket: the slide pad moved a menu cursor one step, like an arrow key."""
        codes = self.grid_codes()
        if codes is not None:
            self.grid_cursor = letter_grid.move(self.grid_cursor, key, codes)
            self.sound.play("sfx_cursor")
        else:
            self.press(key)

    @property
    def controls(self):
        """Which hints to show: "shell" (the Study Pocket), "touch" or "keyboard"."""
        if self.shell:
            return "shell"
        return "touch" if self.touch else "keyboard"

    def status_light(self):
        """The Study Pocket's light: off while paused, red when the score server
        can't be reached on HIGH SCORES, green otherwise (§19.8)."""
        if self.state == "pause" or (self.state == "options" and self.options_back_to == "pause"):
            return "paused"
        if self.state == "high_scores" and self.board_status == "offline":
            return "offline_or_loading"
        return "running"

    def pressed_buttons(self):
        return set(self.button_fingers.values())

    def pause_game(self):
        self.sound.play("sfx_cursor")       # pause opens
        self.go("pause")

    def draw_touch(self, surface, offset):
        """Phones: the stick's faint guide, on top of everything. offset = where
        the game's (0, 0) is on `surface` (it can be drawn below the game too)."""
        if self.state == "play":
            self.stick.draw(surface, offset)

    def handle_key(self, key):
        self.touch = False                  # any key means keyboard mode (§19.1)
        self.press(key)

    def press(self, key):
        """A key press (from the keyboard, or a tap acting like one)."""
        if self.state == "click_to_play":
            self.go("title")
            return
        if settings.DEBUG_KEYS and key in DEBUG_STAGE_KEYS:
            stage = DEBUG_STAGE_KEYS[key]
            if stage <= stage_count(self.level):   # keys above the level's stages do nothing
                self.round = Round(self.level, stage, self.character)
                self.go("play")
            return

        if self.state == "title":
            self.move_cursor(key, TITLE_CHOICES)
            if key in ENTER_KEYS:
                self.choose()
                choice = TITLE_CHOICES[self.menu_choice]
                if choice == "START":
                    self.first_stage = 1
                    self.go("level_select")
                elif choice == "HIGH SCORES":
                    self.scores_level = self.level
                    self.go("high_scores")
                    self.load_board()
                elif choice == "OPTIONS":
                    self.open_options("title")
                elif choice == "STAGE CODE":
                    self.typed_code, self.wrong_code = "", False
                    self.go("stage_code")

        elif self.state == "options":
            self.change_options(key)

        elif self.state == "high_scores":
            change = {pygame.K_LEFT: -1, pygame.K_RIGHT: 1}.get(key, 0)
            if change:
                self.scores_level = LEVELS[(LEVELS.index(self.scores_level) + change) % len(LEVELS)]
                self.sound.play("sfx_cursor")
                self.load_board()
            elif key == pygame.K_ESCAPE:
                self.back()
                self.go("title")
                self.menu_choice = TITLE_CHOICES.index("HIGH SCORES")

        elif self.state == "score":
            self.type_name(key)

        elif self.state == "stage_code":
            self.type_code(key)

        elif self.state == "level_select":
            self.move_cursor(key, LEVELS)
            if key == pygame.K_ESCAPE:
                self.back()
                self.go("title")
            elif key in ENTER_KEYS:
                self.choose()
                self.level = LEVELS[self.menu_choice]
                self.go("character_select")

        elif self.state == "character_select":
            new_choice = {pygame.K_LEFT: 0, pygame.K_RIGHT: 1}.get(key, self.menu_choice)
            if new_choice != self.menu_choice:
                self.menu_choice = new_choice
                self.sound.play("sfx_cursor")
            elif key in ENTER_KEYS:
                self.choose()
                self.character = CHARACTERS[self.menu_choice]
                self.run_score = 0                  # a new run
                self.start_run()
                self.start_stage(self.first_stage)

        elif self.state == "play":
            if key == pygame.K_ESCAPE:
                self.pause_game()

        elif self.state == "pause":
            self.move_cursor(key, PAUSE_CHOICES)
            if key == pygame.K_ESCAPE:
                self.sound.play("sfx_cursor")       # pause closes: Esc again = continue
                self.sound.resume_music()
                self.state = "play"
            elif key in ENTER_KEYS:
                self.choose()
                choice = PAUSE_CHOICES[self.menu_choice]
                if choice == "CONTINUE":
                    self.sound.resume_music()
                    self.state = "play"
                elif choice == "RESTART":
                    self.round = Round(self.level, self.round.stage, self.character)
                    self.go("play")
                elif choice == "SOUND":
                    self.open_options("pause")
                elif choice == "QUIT TO TITLE":
                    self.go("title")

        elif self.state == "course_complete":
            if key in ENTER_KEYS:
                self.choose()
                self.show_score(level_complete=True)

    def open_options(self, came_from):
        self.options_back_to = came_from
        self.go("options")

    def change_options(self, key):
        """The options screen: up/down picks a line, left/right changes a volume."""
        self.move_cursor(key, OPTION_CHOICES)
        choice = OPTION_CHOICES[self.menu_choice]
        change = {pygame.K_LEFT: -1, pygame.K_RIGHT: 1}.get(key, 0)
        if choice == "MUSIC":
            new_volume = max(0, min(settings.VOLUME_MAX, self.music_volume + change))
            if new_volume != self.music_volume:
                self.music_volume = new_volume
                self.sound.set_music_volume(new_volume)     # takes effect right away
                self.sound.play("sfx_cursor")
        elif choice == "SOUND FX":
            new_volume = max(0, min(settings.VOLUME_MAX, self.sound_fx_volume + change))
            if new_volume != self.sound_fx_volume:
                self.sound_fx_volume = new_volume
                self.sound.set_fx_volume(new_volume)        # the blip plays at the new volume
                self.sound.play("sfx_cursor")

        if choice == "BACK" and key in ENTER_KEYS:
            self.choose()
        elif key == pygame.K_ESCAPE:
            self.back()
        if key == pygame.K_ESCAPE or (choice == "BACK" and key in ENTER_KEYS):
            # Go back where we came from, with the cursor on OPTIONS / SOUND.
            back_to = self.options_back_to
            self.go(back_to)
            if back_to == "title":
                self.menu_choice = TITLE_CHOICES.index("OPTIONS")
            else:
                self.menu_choice = PAUSE_CHOICES.index("SOUND")

    def type_code(self, key):
        """The stage code screen: letters, Backspace, Enter, Esc."""
        if key == pygame.K_ESCAPE:
            self.back()
            self.go("title")
        elif key == pygame.K_BACKSPACE:
            self.sound.play("sfx_cursor")
            self.typed_code = self.typed_code[:-1]
            self.wrong_code = False
        elif key in ENTER_KEYS:
            where = self.stage_for_code(self.typed_code)
            if where is None:
                self.sound.play("jingle_failed")
                self.wrong_code = True           # try again
            else:
                # A right code picks its level too, so it skips level select.
                self.sound.play("jingle_passed")
                self.level, self.first_stage = where
                self.go("character_select")
        elif pygame.K_a <= key <= pygame.K_z and len(self.typed_code) < CODE_MAX_LETTERS:
            # Letter keys: pygame.K_a is the letter "a", K_b is "b", and so on.
            self.sound.play("sfx_cursor")
            self.typed_code += chr(key).upper()
            self.wrong_code = False

    def stage_for_code(self, typed):
        """(level, stage) a code starts at, or None if it's wrong. Case doesn't matter."""
        for code, where in settings.STAGE_CODES.items():
            if typed.upper() == code.upper():
                return where
        return None

    def earned_code(self, level, stage):
        """The code to show on this stage's FAILED screen, or None if not earned yet
        (fail this stage of this level FAILS_BEFORE_CODE times)."""
        if self.fail_counts.get((level, stage), 0) < settings.FAILS_BEFORE_CODE:
            return None
        for code, where in settings.STAGE_CODES.items():
            if where == (level, stage):
                return code
        return None

    def start_run(self):
        """A run begins (after character select, which a stage code also leads to):
        give it a new session id and tell the score server. This counts a play in
        the Sheet, and the server only accepts a score from a run it saw start.
        Fire and forget: the game never waits for the answer."""
        self.session = new_session()
        self.device = "phone" if self.touch else "computer"   # for the Sheet's Device column (§19.7)
        if self.online.enabled:
            self.online.post({"action": "start", "session": self.session, "level": self.level,
                              "character": self.character, "device": self.device})

    def finish_run(self, level_complete):
        """A run ends (the last FAILED, or after YOU PASSED THE COURSE!!!): tell the
        score server how far it got. Fire and forget, like start."""
        if self.online.enabled:
            self.online.post({"action": "finish", "session": self.session, "level": self.level,
                              "character": self.character, "stage": self.round.stage,
                              "score": self.run_score, "completed": level_complete,
                              "device": self.device})

    def load_board(self):
        """HIGH SCORES: ask the score server for this level's list (or use the local one)."""
        if self.online.enabled:
            self.board_request = self.online.top(self.scores_level)
            self.board_status = "loading"
        else:
            self.board_request = None
            self.board_status = "local"
            self.board_entries = self.high_scores[self.scores_level]

    def show_score(self, level_complete):
        """The run is over: show YOU SCORED. With a score server, first ask it for the
        level's top 10 to see if the score makes it (§18.3); NEW HIGH SCORE! (or PRESS
        ENTER) only shows once the answer is in."""
        self.level_complete = level_complete
        self.finish_run(level_complete)
        self.name = ""
        self.announced = False
        self.saved_here = False
        if self.online.enabled:
            self.score_request = self.online.top(self.level)
            self.score_phase = "checking"
            self.new_high = False
        else:
            self.score_request = None
            self.score_phase = "decided"
            self.new_high = highscores.makes_the_list(self.high_scores, self.level, self.run_score)
        self.go("score")

    def save_score(self):
        """Enter after typing a name: send it to the score server, or save it here."""
        name = self.name.strip() or "PLAYER"         # an empty name saves as PLAYER
        if self.online.enabled:
            self.score_request = self.online.post({"action": "score", "session": self.session,
                                                   "level": self.level, "score": self.run_score,
                                                   "name": name})
            self.score_phase = "saving"
        else:
            highscores.add(self.high_scores, self.level, name, self.run_score)
            highscores.save(self.high_scores)
            self.go("title")

    def type_name(self, key):
        """The score screen: type a name (letters, numbers, spaces) if it's a high
        score, Enter saves it. Otherwise Enter goes back to the title."""
        if self.score_phase in ("saved", "could_not_save"):
            if key in ENTER_KEYS:
                self.choose()
                self.go("title")
            return
        if self.score_phase != "decided":
            return                                   # still talking to the score server
        if not self.new_high:
            if key in ENTER_KEYS:
                self.choose()
                self.go("title")
            return
        if not self.announced:
            return                                   # wait for "NEW HIGH SCORE!"
        if key in ENTER_KEYS:
            self.choose()
            self.save_score()
        elif key == pygame.K_BACKSPACE:
            self.sound.play("sfx_cursor")
            self.name = self.name[:-1]
        elif len(self.name) < settings.NAME_MAX_LETTERS:
            letter = None
            if pygame.K_a <= key <= pygame.K_z or pygame.K_0 <= key <= pygame.K_9 or key == pygame.K_SPACE:
                letter = chr(key).upper()            # pygame's key numbers are the characters
            elif key in NUMBER_PAD:
                letter = NUMBER_PAD[key]             # the number pad
            if letter:
                self.sound.play("sfx_cursor")
                self.name += letter

    # -----------------------------------------------------------------------
    # Every frame
    # -----------------------------------------------------------------------
    def update(self, dt):
        self.sound.update()                 # stops sounds whose "first N seconds" are over
        self.online.update()                # collects answers from the score server
        before = self.state_time
        self.state_time += dt
        self.grid_flash_left -= dt
        if self.grid_flash_left <= 0:
            self.grid_flash = None
        self.slide_menus(dt)

        def reached(seconds):
            """True on the one frame this screen's timer passes `seconds`."""
            return before < seconds <= self.state_time

        if self.state == "stage_intro" and self.state_time >= settings.STAGE_INTRO_SECONDS:
            self.go("play")

        elif self.state == "play":
            keys = HeldKeys(pygame.key.get_pressed(), self.stick.arrows())   # keyboard + phone stick
            self.round.update(dt, keys, self.solids, self.sprites, self.sound)
            self.music_follows_time()
            if self.round.deadline_extended:
                self.round.deadline_extended = False
                self.deadline_ticks = 0
                self.go("deadline")
            elif self.round.time_is_up():
                self.passed = self.round.passed()
                self.stage_score = self.round.stage_score(self.passed)
                self.run_score += self.stage_score
                if not self.passed:
                    where = (self.round.level, self.round.stage)
                    self.fail_counts[where] = self.fail_counts.get(where, 0) + 1
                self.go("times_up")

        elif self.state == "deadline":
            # The timer counts up one second at a time, holds, then play goes on.
            while (self.deadline_ticks < settings.LAPTOP_EXTRA_SECONDS
                   and self.state_time >= (self.deadline_ticks + 1) * settings.LAPTOP_TICK_SECONDS):
                self.deadline_ticks += 1
                self.round.seconds_left += 1
                self.sound.play("sfx_cursor")
            done_at = settings.LAPTOP_EXTRA_SECONDS * settings.LAPTOP_TICK_SECONDS + settings.LAPTOP_HOLD_SECONDS
            if self.state_time >= done_at:
                self.state = "play"             # carry on (not go(): the music keeps playing)
                self.music_follows_time()

        elif self.state == "times_up" and self.state_time >= settings.TIMES_UP_SECONDS:
            self.go("results")

        elif self.state == "results" and reached(settings.RESULTS_QUESTION_AT):
            self.sound.play("jingle_drumroll")                # "DID YOU PASS?"

        elif self.state == "results" and reached(settings.RESULTS_VERDICT_AT):
            self.sound.stop("jingle_drumroll")                # the drumroll stops for the reveal
            self.sound.play("jingle_passed" if self.passed else "jingle_failed")

        elif self.state == "results" and self.state_time < settings.RESULTS_LEAVE_AT:
            # Hitomi's answer types out: a blip every few letters (until it's all typed).
            lines = results_lines(self.passed, self.round.stage, self.round.last_stage,
                                  self.earned_code(self.round.level, self.round.stage), self.stage_score)
            total = sum(len(text) for text, *rest in lines)
            every = settings.RESULTS_TYPING_BLIP_EVERY
            if min(letters_typed(self.state_time), total) // every > min(letters_typed(before), total) // every:
                self.sound.play("sfx_cursor")

        elif self.state == "results" and self.state_time >= settings.RESULTS_LEAVE_AT:
            if self.passed and self.round.stage < self.round.last_stage:
                self.start_stage(self.round.stage + 1)   # next stage, empty meter
            elif self.passed:
                self.confetti = make_confetti()
                self.go("course_complete")
            else:
                self.show_score(level_complete=False)     # failed: the run is over

        elif self.state == "score":
            self.update_score_screen()

        elif self.state == "high_scores" and self.board_status == "loading":
            if self.board_request.done:
                if self.board_request.ok:
                    self.board_entries = self.board_request.data.get("top", [])
                    self.board_status = "online"
                else:
                    self.board_entries = self.high_scores[self.scores_level]
                    self.board_status = "offline"      # couldn't reach the server: the local list

    def update_score_screen(self):
        request = self.score_request
        if self.score_phase == "checking" and request.done:
            # The server's top 10 (or, if it couldn't be reached, the one on this computer).
            entries = request.data.get("top", []) if request.ok else self.high_scores[self.level]
            self.new_high = highscores.qualifies(entries, self.run_score)
            self.score_phase = "decided"
        if self.score_phase == "decided" and not self.announced and self.state_time >= settings.SCORE_NEW_HIGH_AT:
            self.announced = True
            if self.new_high:
                self.sound.play("jingle_passed")             # NEW HIGH SCORE!
        if self.score_phase == "saving" and request.done:
            if request.ok:
                # SAVED!: the new top 10 from the server, with the name it kept (it cleans names).
                self.saved_entries = request.data.get("top", [])
                self.saved_rank = request.data.get("rank") or None
                self.score_phase = "saved"
            else:
                self.score_phase = "could_not_save"
                if not WEB:                                  # the browser can't keep files
                    name = self.name.strip() or "PLAYER"
                    highscores.add(self.high_scores, self.level, name, self.run_score)
                    highscores.save(self.high_scores)
                    self.saved_here = True

    def slide_menus(self, dt):
        """Study Pocket: in menus the slide pad works like the arrow keys. One
        step when a direction starts; holding it repeats after MENU_REPEAT_DELAY,
        then every MENU_REPEAT_EVERY seconds (§19.8)."""
        key = self.stick.main_arrow() if self.shell and self.state != "play" else None
        if key != self.menu_key:
            self.menu_key = key
            if key:
                self.menu_repeat_left = settings.MENU_REPEAT_DELAY
                self.slide_step(key)
        elif key:
            self.menu_repeat_left -= dt
            if self.menu_repeat_left <= 0:
                self.menu_repeat_left += settings.MENU_REPEAT_EVERY
                self.slide_step(key)

    def music_follows_time(self):
        """During play: the fast "hurry" music when time is short, the normal stage
        music otherwise (the laptop can add time back)."""
        if self.sound.current_song not in ("stage_music", "stage_music_hurry"):
            return
        hurry = self.round.seconds_left <= self.round.hurry_music_at
        wanted = "stage_music_hurry" if hurry else "stage_music"
        if self.sound.current_song != wanted:
            self.sound.play_music(wanted)

    def draw(self, screen):
        font, sprites = self.font, self.sprites
        if self.state == "click_to_play":
            draw_click_to_play(screen, font, self.state_time, self.touch)
        elif self.state == "title":
            draw_title(screen, font, sprites, self.title_cloud, self.menu_choice, self.state_time)
        elif self.state == "level_select":
            draw_level_select(screen, font, self.level_clouds, self.menu_choice, self.controls)
        elif self.state == "character_select":
            draw_character_select(screen, font, sprites, self.menu_choice, self.controls)
        elif self.state == "stage_intro":
            draw_stage_intro(screen, font, self.round.level, self.round.stage, self.controls)
        elif self.state == "play":
            self.round.draw(screen, self.room, font, sprites)
        elif self.state == "pause":
            self.round.draw(screen, self.room, font, sprites)
            draw_pause(screen, font, self.menu_choice)
        elif self.state == "deadline":
            self.round.draw(screen, self.room, font, sprites, timer_color=YELLOW)
            draw_deadline_extended(screen, font, sprites)
        elif self.state == "times_up":
            self.round.draw(screen, self.room, font, sprites)
            draw_times_up(screen, font)
        elif self.state == "options":
            draw_options(screen, font, self.menu_choice, self.music_volume, self.sound_fx_volume, self.controls)
        elif self.state == "stage_code":
            if self.touch:
                letter_grid.draw_code_entry(screen, font, self.typed_code, self.wrong_code, self.grid_flash,
                                            self.grid_cursor if self.shell else None)
            else:
                draw_stage_code(screen, font, self.typed_code, self.wrong_code)
        elif self.state == "results":
            draw_results(screen, font, sprites, self.round.stage, self.round.last_stage,
                         self.round.student.meter, self.passed, self.state_time,
                         self.earned_code(self.round.level, self.round.stage), self.stage_score)
        elif self.state == "course_complete":
            draw_course_complete(screen, font, sprites, self.confetti, self.controls)
        elif self.state == "score":
            if self.score_phase == "saved":
                draw_high_scores(screen, font, self.level, self.saved_entries, "online",
                                 saved_rank=self.saved_rank or 0, controls=self.controls)
            else:
                draw_score(screen, font, sprites, self.level, self.run_score, self.level_complete,
                           self.new_high, self.name, self.score_phase, self.announced, self.saved_here,
                           self.controls, self.grid_flash, self.grid_cursor if self.shell else None)
        elif self.state == "high_scores":
            draw_high_scores(screen, font, self.scores_level, self.board_entries, self.board_status,
                             controls=self.controls)


def page_size():
    """How big the window is, in real screen pixels: the NES screen times
    WINDOW_SCALE on the desktop, or the whole web page in a browser. It's counted
    in the screen's real pixels (a laptop set to 125% has 1.25 real pixels per
    page pixel, a phone often 3), so every game pixel is the same size on screen."""
    if not WEB:
        return (settings.NES_WIDTH * settings.WINDOW_SCALE, settings.NES_HEIGHT * settings.WINDOW_SCALE)
    import platform                     # pygbag's platform module: it can reach the web page
    ratio = platform.window.devicePixelRatio or 1
    return (int(platform.window.innerWidth * ratio), int(platform.window.innerHeight * ratio))


def ask_page(question):
    """Web only: ask the page a yes/no question in JavaScript (False if it can't answer)."""
    try:
        import platform
        return bool(platform.window.eval(question))
    except Exception:
        return False


def phone_page():
    """Is the main pointer a finger (a phone or tablet)? Then the game fills the
    screen (§19.2). A laptop with a touch screen still counts as a computer."""
    return WEB and ask_page('matchMedia("(pointer: coarse)").matches')


def touch_screen_guess():
    """Start in touch mode? (§19.1: the first tap or click decides after that.)"""
    return WEB and ask_page('matchMedia("(pointer: coarse)").matches || navigator.maxTouchPoints > 0')


def hide_loading_picture():
    """Web only: take away the yellow LOADING... picture that tools/build_web.py
    put on the page (GAME_SPEC §19.8). The game is running now."""
    if WEB:
        import platform
        platform.window.eval('var layer = document.getElementById("elsc-loading"); if (layer) layer.remove();')


def open_window(view):
    window = pygame.display.set_mode(view.canvas_size)
    keep_canvas_size(view)
    return window


def keep_canvas_size(view):
    """Web only: show the canvas at exactly the size we want, centered, pixelated.
    pygbag's page stretches the canvas to fill the page, so this puts our size
    back whenever it changes."""
    if not WEB:
        return
    import platform
    ratio = platform.window.devicePixelRatio or 1
    width, height = f"{view.shown_size[0] / ratio:.2f}px", f"{view.shown_size[1] / ratio:.2f}px"
    style = platform.window.canvas.style
    if style.width != width or style.height != height:
        style.width, style.height = width, height
        style.margin = "auto"
        style.imageRendering = "pixelated"


async def main():
    start_mixer()                   # set up sound before pygame.init()
    pygame.init()

    # The real window: the NES screen blown up (see view.py).
    phone = phone_page()
    view = View(page_size(), phone)
    window = open_window(view)
    pygame.display.set_caption(settings.WINDOW_TITLE)

    # The small NES screen. Everything gets drawn here, then scaled up.
    screen = pygame.Surface((settings.NES_WIDTH, settings.NES_HEIGHT))
    frame = pygame.Surface(view.frame_size)     # phones: the whole picture, the NES screen inside

    # Load the art and draw the whole room once. It never changes, so each
    # frame we only copy the part the camera can see.
    sprites = sprite_loader.load_all()
    game = Game(sprites, Font(), layout.draw_room(sprites), layout.solid_rects(), touch_screen_guess())
    shell = Shell() if WEB and settings.HANDHELD_SHELL else None   # the Study Pocket (§19.8)

    clock = pygame.time.Clock()
    running = True
    first_frame = True

    while running:
        # How many seconds passed since the last frame.
        dt = min(clock.tick(settings.FPS) / 1000, settings.MAX_STEP_SECONDS)

        # 1. Handle input.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not getattr(event, "touch", False):     # skip clicks made up from touches
                    game.handle_click(view.window_to_game(event.pos))
            elif event.type in FINGER_EVENTS and WEB:      # the desktop game stays keyboard-only
                game.handle_finger(FINGER_EVENTS[event.type], event.finger_id,
                                   view.to_game(event.x, event.y), view.to_frame(event.x, event.y))

        # In the browser, follow the page if it changes size (and keep our canvas size).
        # The Study Pocket shows in touch mode with the phone held upright.
        if WEB:
            page = page_size()
            use_shell = shell if shell and game.touch and page[1] > page[0] else None
            if page != view.page_size or (use_shell is not None) != view.shell:
                view = View(page, phone, use_shell)
                window = open_window(view)
                frame = pygame.Surface(view.frame_size)
            keep_canvas_size(view)
            game.shell, game.skin_height = use_shell, view.frame_size[1]

        # 2. Update and 3. draw whatever screen we're on.
        game.update(dt)
        game.draw(screen)

        # 4. Scale up to the window. pygame.transform.scale uses
        #    nearest-neighbor, so the pixels stay crisp.
        if view.shell:
            shell.draw(frame, screen, game.status_light(), game.pressed_buttons(), game.sound.muted)
            game.draw_touch(frame, view.offset)
            pygame.transform.scale(frame, view.canvas_size, window)
        elif view.phone:
            frame.fill((0, 0, 0))
            frame.blit(screen, view.offset)
            game.draw_touch(frame, view.offset)
            pygame.transform.scale(frame, view.canvas_size, window)
        else:
            game.draw_touch(screen, (0, 0))
            pygame.transform.scale(screen, view.canvas_size, window)
        pygame.display.flip()
        if first_frame:
            hide_loading_picture()          # our first picture is up: the loading picture can go
            first_frame = False

        # Let the browser do its work (on the desktop this costs nothing).
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
