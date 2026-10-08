# ELSC Game — the room (GAME_SPEC §4).
# Everything here is in TILES: (x, y, width, height), with (0, 0) at the
# top-left of the room. Multiply by TILE_SIZE to get pixels.
# Grid names: columns A-X are x = 0-23, rows 1-24 are y = 0-23 (so V2 = (21, 1)).

import pygame

import settings

# ---------------------------------------------------------------------------
# Bookshelves (solid)
# "faces" = which shelf sprite to use: one word for the whole shelf, or a list
# with one word per column.
# ---------------------------------------------------------------------------
SHELVES = [
    {"name": "Left bookshelf",   "x": 0,  "y": 0,  "w": 3,  "h": 24, "faces": "east"},
    {"name": "Top bookshelf",    "x": 3,  "y": 0,  "w": 15, "h": 1,  "faces": "front"},
    {"name": "Bottom bookshelf", "x": 3,  "y": 23, "w": 15, "h": 1,  "faces": "north"},
    {"name": "Inner shelf S1",   "x": 15, "y": 1,  "w": 2,  "h": 7,  "faces": ["west", "east"]},
    {"name": "Inner shelf S2",   "x": 18, "y": 14, "w": 2,  "h": 9,  "faces": ["west", "east"]},
]

# The book colors. Each shelf tile picks one so that no two neighbors match.
BOOK_COLORS = ["red", "blue", "yellow", "teal"]

# ---------------------------------------------------------------------------
# Walls (solid, placeholder sprite for v1)
# ---------------------------------------------------------------------------
WALLS = [
    (18, 0, 6, 1),
    (23, 1, 1, 1),
    (22, 2, 2, 22),
    (18, 23, 4, 1),
]

# ---------------------------------------------------------------------------
# Tables (solid)
# ---------------------------------------------------------------------------
TABLES = [
    {"name": "Long", "x": 9,  "y": 2,  "w": 2, "h": 6, "sprite": "table_long"},
    {"name": "T1",   "x": 5,  "y": 10, "w": 2, "h": 2, "sprite": "table_square"},
    {"name": "T2",   "x": 11, "y": 10, "w": 2, "h": 2, "sprite": "table_square"},
    {"name": "T3",   "x": 18, "y": 9,  "w": 1, "h": 1, "sprite": "table_small"},
    {"name": "T4",   "x": 6,  "y": 16, "w": 2, "h": 2, "sprite": "table_square"},
    {"name": "T5",   "x": 15, "y": 14, "w": 2, "h": 2, "sprite": "table_square"},
    {"name": "T6",   "x": 10, "y": 18, "w": 2, "h": 2, "sprite": "table_square"},
    {"name": "T7",   "x": 15, "y": 19, "w": 2, "h": 2, "sprite": "table_square"},
]

# ---------------------------------------------------------------------------
# Desks, office chairs and the coffee station (GAME_SPEC §17.3). All solid.
# ---------------------------------------------------------------------------
HARUNA_DESK = [               # Haruna's desk, T4 to T7, top to bottom
    ((19, 3), "haruna_desk_top"),
    ((19, 4), "haruna_desk_monitor"),
    ((19, 5), "haruna_desk_papers"),
    ((19, 6), "haruna_desk_bottom"),
]
HITOMI_DESK = [               # Hitomi's U-shaped desk (the gate is drawn separately: it opens)
    ((21, 8), "hitomi_desk_top_end"),     # V9
    ((20, 9), "hitomi_desk_upper"),       # U10
    ((20, 10), "hitomi_desk_monitor"),    # U11
    ((20, 11), "hitomi_desk_lower"),      # U12
]
HITOMI_GATE = (21, 12)        # V13: hitomi_desk_gate_closed / _open (always solid)
HITOMI_DESK_INSIDE = (21, 9, 1, 3)   # V10-V12: inside her desk, the student can never go in
COFFEE_STATION = (4, 1)       # E2, 2 x 2 tiles (E2-F3)

COFFEE_ITEM_PIXEL = (72, 48)  # the coffee power-up waits on the floor in front of the station (pixels)
HEADPHONES_TILE = (17, 6)     # R7: where Haruna drops the headphones
LAPTOP_PIXEL = (104, 264)     # the laptop power-up sits on table T4 (pixels)...
LAPTOP_TABLE = "T4"           # ...and you grab it by walking up to that table
HIGHLIGHTER_PIXEL = (248, 312)  # the highlighter power-up sits on table T7 (pixels)...
HIGHLIGHTER_TABLE = "T7"        # ...and you grab it by walking up to that table
PIZZA_BOX_PIXEL = (296, 221)    # the pizza box sits on top of bookshelf S2 (pixels)...
PIZZA_SHELF = "Inner shelf S2"  # ...you bump that shelf to knock it off...
PIZZA_FLOOR_PIXEL = (328, 272)  # ...and it lands open here, behind the shelf (pixels)


def shelf_rect(name):
    """A bookshelf's rectangle in pixels, by its name."""
    for s in SHELVES:
        if s["name"] == name:
            return pygame.Rect(to_pixels(s["x"]), to_pixels(s["y"]), to_pixels(s["w"]), to_pixels(s["h"]))
    raise ValueError(name)


def table_rect(name):
    """A table's rectangle in pixels, by its name (for example "T4")."""
    for t in TABLES:
        if t["name"] == name:
            return pygame.Rect(to_pixels(t["x"]), to_pixels(t["y"]), to_pixels(t["w"]), to_pixels(t["h"]))
    raise ValueError(name)

HARUNA_SEAT = (18, 4)         # S5: office chair, Haruna sits on it (solid: she's a person)
HITOMI_SEAT = (21, 10)        # V11: office chair inside her desk, Hitomi sits on it
HITOMI_DOOR = (21, 13)        # V14: the floor just outside her gate, where she comes out and says her line
SITTING_LIFT = 4              # people sitting on an office chair are drawn this many pixels higher

# ---------------------------------------------------------------------------
# Whiteboard: one 3 x 3 sprite, but only the 3 diagonal tiles are solid
# ---------------------------------------------------------------------------
WHITEBOARD_SPRITE_TILE = (6, 19)
WHITEBOARD_TILES = [(6, 19), (7, 20), (8, 21)]

# ---------------------------------------------------------------------------
# Chairs (walk over them to study). 31 chairs, all 1 x 1 tile.
# side = which side of its table the chair is on (N, S, W, E).
# The bonus points for each color are in settings.CHAIR_BONUS.
# ---------------------------------------------------------------------------
CHAIRS = [
    # table, x,    y,    side, color
    ("Long", 8,    2.5,  "W", "blue"),
    ("Long", 8,    4.5,  "W", "white"),
    ("Long", 8,    6.5,  "W", "green"),
    ("Long", 11,   2.5,  "E", "red"),
    ("Long", 11,   4.5,  "E", "blue"),
    ("Long", 11,   6.5,  "E", "white"),
    ("T1",   5.5,  9,    "N", "green"),
    ("T1",   5.5,  12,   "S", "red"),
    ("T1",   4,    10.5, "W", "blue"),
    ("T1",   7,    10.5, "E", "white"),
    ("T2",   11.5, 9,    "N", "green"),
    ("T2",   11.5, 12,   "S", "red"),
    ("T2",   10,   10.5, "W", "blue"),
    ("T2",   13,   10.5, "E", "white"),
    ("T3",   18,   8,    "N", "green"),
    ("T3",   17,   9,    "W", "red"),
    ("T3",   19,   9,    "E", "blue"),
    ("T4",   6.5,  15,   "N", "white"),
    ("T4",   5,    16.5, "W", "green"),
    ("T4",   8,    16.5, "E", "red"),
    ("T5",   15.5, 13,   "N", "blue"),
    ("T5",   14,   14.5, "W", "white"),
    ("T5",   17,   14.5, "E", "green"),
    ("T6",   10.5, 17,   "N", "red"),
    ("T6",   10.5, 20,   "S", "blue"),
    ("T6",   9,    18.5, "W", "white"),
    ("T6",   12,   18.5, "E", "green"),
    ("T7",   15.5, 18,   "N", "red"),
    ("T7",   15.5, 21,   "S", "blue"),
    ("T7",   14,   19.5, "W", "white"),
    ("T7",   17,   19.5, "E", "green"),
]

# ---------------------------------------------------------------------------
# Spawn points (tiles)
# ---------------------------------------------------------------------------
STUDENT_START = (21, 1)   # V2, the entrance nook, facing down
TORNADO_STARTS = [        # where each noise cloud starts (the tile is the cloud's center)
    (7, 21),              # cloud 1: H22, bottom of the room
    (4, 2),               # cloud 2: E3, top left
    (14, 21),             # cloud 3: O22, bottom middle
    (12, 2),              # cloud 4: M3, top middle
    (4, 14),              # cloud 5: E15, left side
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def to_pixels(tiles):
    """Turn a tile position (can be a half tile like 5.5) into pixels."""
    return round(tiles * settings.TILE_SIZE)


def solid_rects():
    """Every solid thing in the room as a pixel rectangle (used from step 2)."""
    boxes = [(s["x"], s["y"], s["w"], s["h"]) for s in SHELVES]
    boxes += WALLS
    boxes += [(t["x"], t["y"], t["w"], t["h"]) for t in TABLES]
    boxes += [(x, y, 1, 1) for (x, y), name in HARUNA_DESK + HITOMI_DESK]
    boxes += [(*HITOMI_GATE, 1, 1), HITOMI_DESK_INSIDE, (*COFFEE_STATION, 2, 2), (*HARUNA_SEAT, 1, 1)]
    boxes += [(x, y, 1, 1) for (x, y) in WHITEBOARD_TILES]
    return [pygame.Rect(to_pixels(x), to_pixels(y), to_pixels(w), to_pixels(h))
            for (x, y, w, h) in boxes]


_floor_tiles = []


def floor_tiles():
    """Every tile with nothing solid on it (chairs count as floor). Worked out once."""
    if not _floor_tiles:
        solids = solid_rects()
        tile = settings.TILE_SIZE
        for y in range(settings.ROOM_HEIGHT_TILES):
            for x in range(settings.ROOM_WIDTH_TILES):
                if not any(pygame.Rect(x * tile, y * tile, tile, tile).colliderect(s) for s in solids):
                    _floor_tiles.append((x, y))
    return _floor_tiles


def chair_sprite_name(chair, highlighted=False):
    """The sprite for a chair, for example 'chair_green_N'. While the highlighter
    is on (highlighted=True) every chair is drawn green."""
    table, x, y, side, color = chair
    if highlighted:
        color = "green"
    return f"chair_{color}_{side}"


def draw_room(sprites):
    """Draw the whole room (without people or the desk gate, which change) onto one
    big picture and return it. Order (GAME_SPEC §17.13): carpet, shelves/walls/desks/
    coffee station, chairs and office chairs, tables, whiteboard.
    The carpet goes everywhere first, so it shows through the curved desk corners."""
    tile = settings.TILE_SIZE
    room = pygame.Surface((settings.ROOM_WIDTH_TILES * tile,
                           settings.ROOM_HEIGHT_TILES * tile))

    def put(name, x, y):
        room.blit(sprites[name], (to_pixels(x), to_pixels(y)))

    # 1. Carpet checkerboard
    for y in range(settings.ROOM_HEIGHT_TILES):
        for x in range(settings.ROOM_WIDTH_TILES):
            put("carpet_a" if (x + y) % 2 == 0 else "carpet_b", x, y)

    # 2. Bookshelves, walls, desks, coffee station
    for shelf in SHELVES:
        for col in range(shelf["w"]):
            faces = shelf["faces"] if isinstance(shelf["faces"], str) else shelf["faces"][col]
            for row in range(shelf["h"]):
                x, y = shelf["x"] + col, shelf["y"] + row
                # x + 2*y: side-by-side tiles differ by 1, stacked tiles by 2,
                # so neighbors never get the same book color.
                book = BOOK_COLORS[(x + 2 * y) % len(BOOK_COLORS)]
                put(f"shelf_{faces}_{book}", x, y)

    for (wx, wy, ww, wh) in WALLS:
        for x in range(wx, wx + ww):
            for y in range(wy, wy + wh):
                put("wall_placeholder", x, y)

    for (x, y), name in HARUNA_DESK + HITOMI_DESK:
        put(name, x, y)
    put("coffee_station", *COFFEE_STATION)

    # 3. Chairs and office chairs
    for chair in CHAIRS:
        table, x, y, side, color = chair
        put(chair_sprite_name(chair), x, y)
    put("office_chair", *HARUNA_SEAT)
    put("office_chair", *HITOMI_SEAT)

    # 4. Tables
    for t in TABLES:
        put(t["sprite"], t["x"], t["y"])

    # 5. Whiteboard
    put("whiteboard", *WHITEBOARD_SPRITE_TILE)

    return room
