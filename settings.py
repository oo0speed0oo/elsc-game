# ELSC Game — settings
# Every number you might want to tune lives here. Change a number, save, and
# run `python main.py` again to try it.
#
# Most per-level numbers are in LEVELS (further down). Lists like [30, 30, 40]
# have one number per stage: the first is stage 1, the second stage 2, and so on.

# ---------------------------------------------------------------------------
# Screen and window
# ---------------------------------------------------------------------------
WINDOW_TITLE = "ELSC Game"   # the text in the window's title bar
NES_WIDTH = 256              # width of the NES screen we draw on, in pixels
NES_HEIGHT = 240             # height of the NES screen we draw on, in pixels
WINDOW_SCALE = 3             # how much to blow up the NES screen: 2 = 512 x 480, 3 = 768 x 720, 4 = 1024 x 960
FPS = 60                     # frames per second (how many times the game updates each second)
MAX_STEP_SECONDS = 0.05      # if the game hiccups (e.g. dragging the window), never jump ahead more than this in one frame
                             # (in a web browser the window scale is worked out to fit the page instead)
CLICK_TO_PLAY_BLINK_SECONDS = 0.5   # web only: "CLICK TO PLAY" blinks on and off this often

# ---------------------------------------------------------------------------
# The web version (GAME_SPEC §18)
# ---------------------------------------------------------------------------
EDITION = "site"             # which web edition this is: "site" (the website) or "friends" (the friends link)
SCORE_SERVER_URL = "https://script.google.com/macros/s/AKfycbxkMGJsik50WjshdZ2fdUoTB0nAqHJ4FdwxyTY8h31r-Vj8z38Z_xrEw1dF2N3j2mNx/exec"  # the online score server's address (ends in /exec); "" = offline, scores stay on this computer
ONLINE_TIMEOUT_SECONDS = 15  # a question to the score server that takes longer than this counts as failed
                             # (Google's free server can take 10+ s to wake up after a quiet spell)

# ---------------------------------------------------------------------------
# Phones and tablets (GAME_SPEC §19; web version only)
# ---------------------------------------------------------------------------
PHONE_GAME_TOP = 24          # phones held upright: the black gap above the game, in game pixels
PHONE_DRAW_SCALE_MAX = 3     # phones: we draw at most this many real pixels per game pixel and let the
                             # browser stretch the rest (bigger = a bit sharper, smaller = faster)
TOUCH_MOUSE_IGNORE_SECONDS = 1.0   # phones also send a pretend mouse click after each touch; ignore
                                   # clicks this soon after a touch (or they'd switch to keyboard mode)
TOUCH_DEAD_ZONE = 6          # sliding less than this (game pixels) from where the thumb landed does nothing
TOUCH_STICK_FOLLOW = 24      # if the thumb goes further than this, the stick's center follows it
TOUCH_STICK_VISIBLE = True   # show the faint dotted ring and thumb dot while a thumb is down
TOUCH_STICK_RING_RADIUS = 14 # the size of that dotted ring, in game pixels
TOUCH_TAP_MAX_MOVE = 6       # a touch only counts as a tap if the finger moved less than this (game pixels)
GRID_FLASH_SECONDS = 0.1     # the letter grid: a tapped cell flashes yellow for this long
HANDHELD_SHELL = True        # phones held upright: show the game inside the yellow ELSC Study Pocket (False = plain)
MENU_REPEAT_DELAY = 0.4      # Study Pocket: holding a slide in a menu moves the cursor again after this long...
MENU_REPEAT_EVERY = 0.15     # ...and then every this many seconds
HANDHELD_BRAND_PLATE_MIN_GAP = 30   # tall phones: the ELSC plate shows if the plain body is at least this tall

# ---------------------------------------------------------------------------
# Tiles, HUD and room
# ---------------------------------------------------------------------------
TILE_SIZE = 16               # one tile is 16 x 16 pixels
HUD_HEIGHT = 64              # the black strip at the top of the screen, in pixels
ROOM_WIDTH_TILES = 24        # the room is 24 tiles wide (columns A to X)
ROOM_HEIGHT_TILES = 24       # the room is 24 tiles tall (rows 1 to 24)

# ---------------------------------------------------------------------------
# Round and timer
# ---------------------------------------------------------------------------
TIMER_RED_AT = 10            # the HUD timer turns red when this many seconds are left
                             # (round lengths are per level and stage: see LEVELS)

# ---------------------------------------------------------------------------
# The student
# ---------------------------------------------------------------------------
STUDENT_SPEED = 90           # walking speed, in pixels per second (about 5.6 tiles per second)
STUDENT_HITBOX = 12          # the student's hitbox is a square this many pixels wide, centered in the 16 x 16 sprite
WALK_FRAMES_PER_SECOND = 8   # how many times per second the walk switches between walk1 and walk2
READ_FRAMES_PER_SECOND = 2   # how many times per second the seated head nod switches between read1 and read2

# ---------------------------------------------------------------------------
# Studying and the study meter
# ---------------------------------------------------------------------------
BAR_MAX_POINTS = 150         # points in a full study bar
CHARGE_POINTS_PER_SECOND = 5 # points per second while studying normally
CHAIR_BONUS = {              # points per second during the bonus, by chair color
    "green": 15,
    "red": 10,
    "white": 5,
    "blue": 5,
}
BONUS_SECONDS = 2            # the chair bonus lasts this many seconds after sitting at a new table

# The "+1 / +2 / +3" pop-up over your head each second while studying.
# It shows how fast you studied that second: +1 = normal speed (5 per second),
# +2 = twice as fast (a red chair), +3 = three times as fast (a green chair).
POPUP_RISE_PIXELS = 12       # how far it floats up, in pixels
POPUP_RISE_SECONDS = 0.6     # how long it takes to float up, in seconds
POPUP_BOUNCE_PIXELS = 2      # the little hop at the start, in pixels
POPUP_BOUNCE_SECONDS = 0.15  # how long that hop lasts, in seconds
POPUP_BLINK_SECONDS = 0.2    # after rising it blinks for this long, then disappears
BLINK_TOGGLE_SECONDS = 0.05  # when something blinks, it turns on/off this often

# ---------------------------------------------------------------------------
# Getting hit
# ---------------------------------------------------------------------------
                             # (the points a hit takes are per level: see LEVELS)
KNOCKBACK_DISTANCE = 32      # how far a hit pushes you, in pixels (32 = 2 tiles)
KNOCKBACK_SECONDS = 0.2      # how long the push takes, in seconds
                             # (how long you flash after a hit is per level: see LEVELS)

# ---------------------------------------------------------------------------
# Haruna and Hitomi
# ---------------------------------------------------------------------------
HARUNA_TYPE_FRAMES_PER_SECOND = 2   # how fast Haruna types at her desk (switches between 2 pictures)
HITOMI_WORK_FRAMES_PER_SECOND = 2   # how fast Hitomi works at her desk (switches between 2 pictures)
HARUNA_CALL_EVERY_SECONDS = 15      # Haruna calls out "BE QUIET PLEASE..." this often
HARUNA_CALL_SECONDS = 2             # how long she waves her hands up when she calls out
HARUNA_CALL_FRAMES_PER_SECOND = 4   # how fast her hands-up pictures switch
HARUNA_BUBBLE_SECONDS = 2.5         # how long her speech bubble stays on screen
                                    # (when Hitomi comes out, how fast she walks and how long she
                                    #  stays out are per level: see LEVELS)
HITOMI_HITBOX = 12                  # Hitomi is solid: a square this many pixels wide, centered on her
HITOMI_POINT_SECONDS = 1            # "DID YOU STUDY?!": how long she points at you when she comes out...
HITOMI_POINT_FRAMES_PER_SECOND = 4  # ...how fast her pointing pictures switch...
HITOMI_BUBBLE_SECONDS = 2           # ...and how long her speech bubble shows
HITOMI_STUCK_SECONDS = 1            # if she's stuck against something this long...
HITOMI_DETOUR_SECONDS = 2           # ...she walks to a random spot for this long, then tries again
HITOMI_CHAIR_SECONDS = 2            # Level 3: how long she stands on a chair before picking the next one
HITOMI_PUSH_DISTANCE = 16           # Levels 2 and 3: how far she pushes you, in pixels (16 = 1 tile)...
HITOMI_PUSH_SECONDS = 0.15          # ...and how long the push takes (no damage, no flashing)
PUSH_SOUND_SECONDS = 0.2            # her push plays just the start of jingle_failed.wav, this long

# ---------------------------------------------------------------------------
# Power-ups (GAME_SPEC §17.6)
# ---------------------------------------------------------------------------
ITEM_BOB_PIXELS = 1                 # power-ups bob up and down this many pixels...
ITEM_BOBS_PER_SECOND = 2            # ...this many times per second
ITEM_GRAB_BOX_PIXELS = 12           # a floor item is grabbed when you touch the box this wide in its middle
TABLE_GRAB_REACH_PIXELS = 2         # a table item is grabbed when you get this close to its table
POWERUP_SOUND_SECONDS = 0.6         # grabbing a power-up plays just the start of jingle_passed.wav, this long

COFFEE_SECONDS = 10                 # the coffee lasts this long...
COFFEE_BOOST = 1.5                  # ...and makes you walk and study this many times faster

HEADPHONES_CHECK_AT = 0.5           # Haruna checks on you when this much of the round is gone (0.5 = half)
HEADPHONES_IF_BAR_UNDER = 50        # ...and drops the headphones if your bar is under this percent
HARUNA_TOSS_SECONDS = 0.4           # how long her "toss" picture shows when she drops them
HEADPHONES_SECONDS = 8              # the headphones last this long: clouds pass through you and can't notice you
STAR_BLINK_EVERY_FRAMES = 3         # with headphones on you blink (like Mario's star), changing colors every this many frames...
STAR_FAST_BLINK_EVERY_FRAMES = 2    # ...and faster, every this many frames...
STAR_FAST_BLINK_SECONDS = 2         # ...in the last this many seconds, as a warning

LAPTOP_EXTRA_SECONDS = 10           # the laptop ("DEADLINE EXTENDED!") adds this many seconds to the timer...
LAPTOP_TICK_SECONDS = 0.1           # ...counting up one second every this many seconds...
LAPTOP_HOLD_SECONDS = 0.5           # ...then the box stays this long before play goes on

HIGHLIGHTER_SECONDS = 8             # the highlighter lasts this long...
HIGHLIGHTER_POINTS_PER_SECOND = 15  # ...and every chair gives this many points per second the whole time you sit
BOOK_BLINKS_PER_SECOND = 4          # with the highlighter, the book switches to green and back this often

PIZZA_FALL_SECONDS = 0.4            # bump the right bookshelf and the pizza box falls off behind it in this long...
PIZZA_ARC_PIXELS = 24               # ...rising this many pixels on the way (a little arc)
PIZZA_BUMP_SOUND_SECONDS = 0.4      # the bump plays just the start of jingle_failed.wav, this long
PIZZA_LURE_SECONDS = 8              # then every cloud goes to the pizza for this long, ignoring you...
PIZZA_LURE_TILES = 1.5              # ...wandering within this many tiles of it

# ---------------------------------------------------------------------------
# Levels (the big table: everything that changes from level to level)
# One number per stage in the lists: [stage 1, stage 2, stage 3, ...].
# The number of stages in a level = how many round lengths it has.
# ---------------------------------------------------------------------------
LEVELS = {
    1: {                                                   # LEVEL 1 (easy)
        "round_seconds": [30, 30, 40],                     # how long each stage lasts, in seconds
        "clouds": [1, 2, 3],                               # how many noise clouds in each stage
        "cloud_sizes": ["small", "medium", "big"],         # cloud size in each stage (see CLOUD_SIZES)
        "cloud_speed": [36, 54, 72],                       # cloud speed in each stage, in pixels per second
        "notice_seconds": None,                            # seconds of studying before the clouds notice you (None = never, they only wander)
        "keep_chasing_seconds": 0,                         # after you stop studying, the clouds keep chasing this long
        "pass_marks": [50, 60, 70],                        # percent of the bar needed to pass each stage (hidden from the player)
        "hit_damage": 15,                                  # points a hit takes from the bar
        "invincible_seconds": 1,                           # after a hit you flash and can't be hit (or study) for this long
        "hurry_music_at": 10,                              # the music speeds up at this many seconds left
        "hitomi_comes_out_at": [50, 70],                   # Hitomi comes out when the bar first reaches these percents
        "hitomi_moves": "wander",                          # what she does: "wander" (random spots), "follow" (you) or "chairs" (steals chairs)
        "hitomi_speed": 40,                                # her walking speed, in pixels per second
        "hitomi_out_seconds": 6,                           # how long she stays out before walking back in
        "hitomi_pushes": False,                            # does she push you when she bumps into you? (False = she just stops)
        "power_ups": ["coffee", "headphones"],             # which power-ups this level has
        "score_multiplier": 1,                             # stage scores are multiplied by this
    },
    2: {                                                   # LEVEL 2 (normal)
        "round_seconds": [45, 45, 45, 45, 45],
        "clouds": [1, 2, 3, 4, 5],
        "cloud_sizes": ["small", "small", "medium", "medium", "big"],
        "cloud_speed": [54, 54, 54, 54, 54],
        "notice_seconds": 3,
        "keep_chasing_seconds": 0,
        "pass_marks": [50, 55, 60, 65, 70],
        "hit_damage": 20,
        "invincible_seconds": 1,
        "hurry_music_at": 15,
        "hitomi_comes_out_at": [50, 70],
        "hitomi_moves": "follow",
        "hitomi_speed": 60,
        "hitomi_out_seconds": 8,
        "hitomi_pushes": True,
        "power_ups": ["coffee", "headphones", "laptop", "highlighter"],
        "score_multiplier": 2,
    },
    3: {                                                   # LEVEL 3 (hard)
        "round_seconds": [60, 60, 60, 60, 60],
        "clouds": [1, 2, 3, 4, 5],
        "cloud_sizes": ["big", "big", "big", "big", "big"],
        "cloud_speed": [72, 72, 72, 72, 72],
        "notice_seconds": 1.5,
        "keep_chasing_seconds": 3,
        "pass_marks": [55, 60, 65, 70, 75],
        "hit_damage": 20,
        "invincible_seconds": 1.5,
        "hurry_music_at": 15,
        "hitomi_comes_out_at": [30, 50, 70],
        "hitomi_moves": "chairs",
        "hitomi_speed": 75,
        "hitomi_out_seconds": 10,
        "hitomi_pushes": True,
        "power_ups": ["coffee", "headphones", "laptop", "highlighter", "pizza"],
        "score_multiplier": 3,
    },
}

# ---------------------------------------------------------------------------
# The Noise Tornado (clouds)
# ---------------------------------------------------------------------------
CLOUD_SIZES = {"small": 32, "medium": 48, "big": 64}    # size of the cloud drawing, in pixels (2 x 2, 3 x 3, 4 x 4 tiles)
CLOUD_HITBOX = {"small": 20, "medium": 30, "big": 40}   # hitbox, a centered square this many pixels wide (smaller than the drawing so near misses feel fair)
LUNGE_SECONDS = 0.5                            # how long the lunge lasts when it notices you, in seconds
LUNGE_SPEED = 90                               # lunge speed, in pixels per second
TORNADO_FRAMES_PER_SECOND = 10                 # animation speed of the cloud
BUBBLE_SECONDS = 0.7                           # a noise bubble pops out this often, in seconds
BUBBLES_ON_LUNGE = 3                           # how many bubbles pop out at once when it lunges
BUBBLE_RISE_PIXELS = 8                         # how far a noise bubble floats up, in pixels
BUBBLE_RISE_SECONDS = 0.6                      # how long it takes to float up, in seconds
BUBBLE_BLINKS = 2                              # how many times it blinks before it disappears
BURST_SPREAD_PIXELS = 16                       # in the lunge burst, each bubble sits this far to the right of the last one
BURST_STEP_UP_PIXELS = 6                       # ...and this much higher, so they fan out

# ---------------------------------------------------------------------------
# Passing the test
# ---------------------------------------------------------------------------
                                               # (pass marks are per level and stage: see LEVELS)
FAILS_BEFORE_CODE = 5                          # fail a stage this many times and its stage code appears
STAGE_CODES = {               # stage codes (letters only): the level and stage each one starts at
    "MATHCLASS": (1, 2),
    "COMPUTERSCIENCECLASS": (1, 3),
    "GRAMMAR": (2, 3),
    "VOCABULARY": (2, 5),
    "PRESENTATION": (3, 3),
    "FINALEXAM": (3, 5),
}

# Score and high scores
# WARNING: the online score server (server/apps_script/Code.gs, MAX_SCORE) has its own copy of the
# highest possible score per level, worked out from BAR_MAX_POINTS, SCORE_PER_POINT, PASS_BONUS, the
# number of stages and each level's score_multiplier. If you change any of those, change MAX_SCORE
# in Code.gs too (and redeploy it), or real high scores will be refused.
SCORE_PER_POINT = 10         # each study bar point at the test is worth this many score points...
PASS_BONUS = 1000            # ...plus this for passing the stage (then times the level's score_multiplier)
HIGH_SCORES_KEPT = 10        # each level keeps its top this-many scores
NAME_MAX_LETTERS = 10        # the longest name you can type for a high score
SCORE_NEW_HIGH_AT = 1.5      # on the score screen, "NEW HIGH SCORE!" appears after this many seconds

# Screens
STAGE_INTRO_SECONDS = 2      # how long "STAGE N / READY, SET, STUDY!" shows before play starts

# Time's up and the results screen
TIMES_UP_SECONDS = 1.5       # how long the "TIME'S UP!" banner shows before the test
RESULTS_QUESTION_AT = 1.0    # on the results screen, "DID YOU PASS?" appears after this many seconds
RESULTS_VERDICT_AT = 2.5     # ...and PASSED! or FAILED... appears after this many seconds
RESULTS_LEAVE_AT = 5.0       # ...and the game moves on after this many seconds
RESULTS_TYPING_LETTERS_PER_SECOND = 30   # Hitomi's answer types out this many letters per second...
RESULTS_TYPING_BLIP_EVERY = 2            # ...with a blip every this many letters
PORTRAIT_FRAMES_PER_SECOND = 4           # how fast Haruna talks and Hitomi cheers / shakes her head on the results screen
CONFETTI_PIECES = 90         # how many bits of confetti on the "YOU PASSED THE COURSE!!!" screen

# ---------------------------------------------------------------------------
# Sound and volume (the Options screen changes the volumes while you play)
# ---------------------------------------------------------------------------
VOLUME_MAX = 10              # volumes go from 0 (silent) to this
MUSIC_VOLUME_START = 4       # music volume when the game opens
SOUND_FX_VOLUME_START = 6    # sound effects volume when the game opens
THEME_FADE_SECONDS = 0.5     # the main theme fades out over this many seconds when a stage intro starts
SOUND_BUFFER_SAMPLES = 2048      # sound is made in chunks this big: too small = crackling, too big = sounds start late
WEB_SOUND_BUFFER_SAMPLES = 4096  # the same in a web browser, which needs bigger chunks (must be 256, 512, ... 16384)
HIT_SOUND_SECONDS = 0.4      # getting hit plays just the start of jingle_failed.wav, this long
NOTICE_SOUND_SECONDS = 0.5   # the tornado noticing you plays just the start of jingle_drumroll.wav, this long

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG_KEYS = False           # True = keys 1 to 5 jump to that stage of the current level
