"""ELSC Game — build both web editions in one go (GAME_SPEC §18.4).

    python tools/build_web.py

For "site" and "friends":
  1. make_web_copy.py makes build_web/<edition>/elsc-game/ (just the game, with its EDITION)
  2. pygbag builds it into build_web/<edition>/elsc-game/build/web/
Those two web/ folders are what you upload (see docs/PUBLISH_ON_WEBSITE.md).
Needs pygbag (pip install pygbag) and an internet connection (pygbag downloads
its page template the first time).
"""

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_web_copy import EDITIONS, GAME_DIR, folder_size, make_web_copy   # noqa: E402

TITLE = "ELSC Game"          # the name shown on the browser tab
SIZE_LIMIT_MB = 15           # each edition should stay under this (GAME_SPEC §18.4)

# The phone page (GAME_SPEC §19.2): no zooming, scrolling, pull-to-refresh,
# text selection or long-press menus, and a black background.
VIEWPORT = ('<meta name="viewport" content="width=device-width, initial-scale=1, '
            'maximum-scale=1, user-scalable=no, viewport-fit=cover">')
PHONE_CSS = """<style>
        html, body, canvas {
            touch-action: none; overscroll-behavior: none;
            user-select: none; -webkit-user-select: none; -webkit-touch-callout: none;
        }
        html, body { background-color: #000000 !important; overflow: hidden; }   /* !important: pygbag sets grey */

        /* The loading layer (GAME_SPEC §19.8): on phones only, the Study Pocket with
           LOADING... and a red light until the game's first frame. pygbag's own message
           box stays on top of it (it says "Ready to start! Please click/touch page" when
           the browser wants a tap first), and taps go through it. Computers: no layer. */
        #elsc-loading { display: none; }
        @media (pointer: coarse) {
            #elsc-loading {
                position: fixed; top: 0; right: 0; bottom: 0; left: 0; z-index: 999990;
                background-color: #000000; display: flex; align-items: center; justify-content: center;
                pointer-events: none;
            }
            #elsc-loading img { image-rendering: pixelated; width: min(100vw, calc(100vh * 268 / 580)); height: auto; }
        }
    </style>"""
LOADING_PICTURE = "handheld_loading.png"
LOADING_LAYER = f'<div id="elsc-loading"><img src="{LOADING_PICTURE}" alt="LOADING..."></div>'

# Add to Home Screen (GAME_SPEC §19.6): these files from web/app/ go next to
# index.html, and these tags go into its <head> (pygbag's own copies of the two
# "-capable" tags are taken out, so each is there once).
APP_DIR = os.path.join(GAME_DIR, "web", "app")
APP_FILES = ["manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png"]
APP_TAGS = ['<link rel="manifest" href="manifest.webmanifest">',
            '<link rel="apple-touch-icon" href="icon-180.png">',
            '<meta name="apple-mobile-web-app-capable" content="yes">',
            '<meta name="mobile-web-app-capable" content="yes">',
            '<meta name="theme-color" content="#000000">']


def phone_page(upload):
    """Put the viewport tag, the CSS and the Add to Home Screen tags above into
    the built index.html (pygbag's own copies of those tags are taken out), add
    the loading picture, and copy the app icons, manifest and picture next to it."""
    path = os.path.join(upload, "index.html")
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    replaced = ('name="viewport"', 'name="apple-mobile-web-app-capable"', 'name="mobile-web-app-capable"')
    lines = [line for line in lines if not any(tag in line for tag in replaced)]
    page = "\n".join(lines)
    if "</head>" not in page:
        raise SystemExit("index.html has no </head>: can't add the phone page tags.")
    tags = "\n    ".join([VIEWPORT] + APP_TAGS)
    page = page.replace("</head>", f"    {tags}\n    {PHONE_CSS}\n</head>", 1)
    if "<body>" not in page:
        raise SystemExit("index.html has no <body>: can't add the loading picture.")
    page = page.replace("<body>", f"<body>\n    {LOADING_LAYER}", 1)    # first thing on the page
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    for name in APP_FILES + [LOADING_PICTURE]:
        shutil.copy(os.path.join(APP_DIR, name), os.path.join(upload, name))


def build(edition):
    """Make the copy, build it with pygbag, and return the folder to upload."""
    copy = make_web_copy(edition)
    print(f"\n=== {edition}: building with pygbag ...", flush=True)
    result = subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", TITLE, copy],
                            cwd=GAME_DIR, capture_output=True, text=True)
    upload = os.path.join(copy, "build", "web")
    if result.returncode != 0 or not os.path.isfile(os.path.join(upload, "index.html")):
        print(result.stdout[-2000:], result.stderr[-2000:])
        raise SystemExit(f"pygbag could not build the {edition} edition (see above).")
    phone_page(upload)
    return upload


if __name__ == "__main__":
    finished = []
    for edition in EDITIONS:
        finished.append((edition, build(edition)))

    print("\nReady to upload:")
    too_big = False
    for edition, upload in finished:
        mb = folder_size(upload) / 1e6
        too_big = too_big or mb >= SIZE_LIMIT_MB
        print(f"  {edition:8} {os.path.relpath(upload, GAME_DIR)}   {mb:.1f} MB"
              + ("   <- over the limit!" if mb >= SIZE_LIMIT_MB else ""))
    print(f"\nEach should be under {SIZE_LIMIT_MB} MB: " + ("NO, see above." if too_big else "yes."))
    print("Try one locally:  python -m pygbag build_web/site/elsc-game   (then open http://localhost:8000)")
