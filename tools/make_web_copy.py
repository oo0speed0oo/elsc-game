"""ELSC Game — make a copy of the game for the web (GAME_SPEC §18.4).

    python tools/make_web_copy.py --edition site
    python tools/make_web_copy.py --edition friends

Copies only what the game needs (its .py files and assets/) into
build_web/<edition>/elsc-game/ and sets EDITION in that copy's settings.py.
Players don't download the docs, the art tools or the preview pictures.
The .wav sounds are left out too: every sound has an .ogg, which is what
browsers play (and pygbag refuses .wav files).

Then try it:  python -m pygbag build_web/site/elsc-game   (open http://localhost:8000)
"""

import argparse
import os
import re
import shutil

GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the folder with main.py
EDITIONS = ("site", "friends")


def make_web_copy(edition):
    """Make build_web/<edition>/elsc-game/ and return its path."""
    target = os.path.join(GAME_DIR, "build_web", edition, "elsc-game")
    if os.path.exists(target):
        shutil.rmtree(target)           # start clean (this folder is only ever made by this script)
    os.makedirs(target)

    # The game's own .py files (the ones next to main.py).
    for name in sorted(os.listdir(GAME_DIR)):
        if name.endswith(".py"):
            shutil.copy2(os.path.join(GAME_DIR, name), target)

    # assets/, without .wav files and Python's cache folders.
    shutil.copytree(os.path.join(GAME_DIR, "assets"), os.path.join(target, "assets"),
                    ignore=shutil.ignore_patterns("*.wav", "__pycache__"))

    # This copy's edition.
    settings_path = os.path.join(target, "settings.py")
    with open(settings_path, encoding="utf-8") as f:
        text = f.read()
    text, changed = re.subn(r'^EDITION = "[^"]*"', f'EDITION = "{edition}"', text, flags=re.MULTILINE)
    if changed != 1:
        raise SystemExit("Could not find the EDITION line in settings.py")
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(text)
    return target


def folder_size(path):
    return sum(os.path.getsize(os.path.join(root, f)) for root, dirs, files in os.walk(path) for f in files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy the game for the web.")
    parser.add_argument("--edition", choices=EDITIONS, default="site",
                        help='"site" (the website) or "friends" (the friends link)')
    edition = parser.parse_args().edition
    target = make_web_copy(edition)
    print(f"Made {os.path.relpath(target, GAME_DIR)}  (edition {edition}, "
          f"{folder_size(target) / 1e6:.1f} MB)")
    print(f"Try it:  python -m pygbag {os.path.relpath(target, GAME_DIR).replace(os.sep, '/')}")
