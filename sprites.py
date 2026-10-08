# ELSC Game — loads the sprite sheets from assets/sprites/.
# Each sheet has a .json file that says where each sprite sits on the sheet.
# We cut every sprite out once, at the start, and keep them in a dictionary
# so the rest of the game can ask for a sprite by name.

import json
import os

import pygame

SPRITE_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")

# The sheets whose .json has a "sprites" list of named boxes.
# (The tornado and the font use a different .json layout; they get loaded in
# the steps that need them.)
NAMED_SHEETS = [
    "furniture_sheet",
    "students_sheet",
    "students_seated_sheet",
    "effects_sheet",
    "people_v2_sheet",
    "objects_v2_sheet",
]


def read_json(name):
    """Read assets/sprites/<name>.json and return it as a dictionary."""
    with open(os.path.join(SPRITE_DIR, name + ".json")) as f:
        return json.load(f)


def load_sheet(name):
    """Load <name>.png using <name>.json and return {sprite name: picture}."""
    info = read_json(name)
    sheet = pygame.image.load(os.path.join(SPRITE_DIR, info["sheet"])).convert_alpha()

    pictures = {}
    for sprite_name, box in info["sprites"].items():
        rect = pygame.Rect(box["x"], box["y"], box["w"], box["h"])
        pictures[sprite_name] = sheet.subsurface(rect)
    return pictures


def load_frames(name):
    """Load an animation sheet whose .json has "frames_xywh" (the Noise
    Tornado). Returns the frames as a list, in order."""
    info = read_json(name)
    sheet = pygame.image.load(os.path.join(SPRITE_DIR, info["sheet"])).convert_alpha()
    return [sheet.subsurface(pygame.Rect(box["x"], box["y"], box["w"], box["h"]))
            for box in info["frames_xywh"]]


def load_all():
    """Load every named sprite into one dictionary. Call after the window is open."""
    sprites = {}
    for name in NAMED_SHEETS:
        sprites.update(load_sheet(name))
    return sprites
