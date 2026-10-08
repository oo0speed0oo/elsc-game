# ELSC Game — instructions for Claude Code

This is a small top-down, NES Zelda-style game built in **Python + pygame**. The rules are in `docs/GAME_SPEC.md`, the build is split into small steps in `docs/BUILD_PLAN.md`, and all the art is finished in `assets/sprites/` (read `assets/sprites/README.md`). Pictures of every screen, in play order, are in `docs/art/flow/`, and the version 2 screens are in `docs/art/v2/`. The game also runs in a web browser (built with pygbag). Read the spec, the build plan and the sprites README before writing any code.

## How to work with me

- **Build one step at a time.** Only do the step I ask for (for example, "do step 3"). When the step is done, stop and tell me how to run and test it. Don't start the next step until I say so.
- **Explain in plain words.** I'm learning. After each step, briefly explain what you added and which parts of the code do what. Keep it short and beginner-friendly.
- **Stick to the spec.** Version 2 and the web version (§18) are built; we're now adding **phone and tablet play** (`GAME_SPEC.md` §19). §17, §18 and §19 win over §1–15 where they disagree. Don't add features that aren't in the spec. The §16 list is off limits unless I ask.
- **Ask before changing the design.** If something in the spec is unclear, looks wrong, or can't work, ask me instead of guessing. Small technical choices (variable names, helper functions) are yours to make.
- **Keep it runnable.** After every step, the game must still start and run with `python main.py`, with no errors. After Step 27 it must also run in the browser (pygbag). While we add phones (Steps 31–34), the game must keep working with the keyboard on computers, on the desktop and in the browser, after every step.
- **Use the finished art.** Every sprite is in `assets/sprites/` with a `.json` map of where each one sits on its sheet. Don't draw with shapes and don't change the art. If you need a sprite that doesn't exist, ask me.
- **Keep the pixels crisp.** Draw everything on a 256 × 240 surface (the NES screen) and scale it up to the window with nearest-neighbor scaling (no smoothing).
- **Make tuning as easy as possible.** Every tunable number lives in **`settings.py` only**: speeds, timers, sizes, points, pass marks, the window scale. Group them and give each a plain-English comment, so I can change a number, save and play again. Never hard-code these numbers anywhere else.
- **Update `docs/BUILD_PLAN.md`** when a step is finished (tick its checkbox).

## Project layout

```
elsc-game/
├── CLAUDE.md          (this file)
├── main.py            (starts the game, game loop, screens)
├── settings.py        (every tunable number, with plain-English notes)
├── layout.py          (the room: bookshelves, walls, tables, chairs, desks, whiteboard)
├── assets/
│   ├── sprites/       (all the NES art + .json maps; see its README)
│   └── sounds/        (music and sound effects, added last, later)
├── art_tools/         (the scripts that drew the art; not part of the game itself)
├── tools/             (make_web_copy.py, build_web.py: build the web editions; not part of the game)
├── server/            (the score server: Google Apps Script + setup guide; not part of the game)
├── web/               (the leaderboard page and embed code for the website; not part of the game)
└── docs/
    ├── GAME_SPEC.md   (the rules)
    ├── BUILD_PLAN.md  (the steps)
    └── art/           (preview pictures; flow/ has every screen in play order)
```

Splitting into more files later is fine if a file gets too long (for example `sprites.py` for loading art, `tornado.py`, `menus.py`), but keep it simple.

## Running the game

```
pip install pygame
python main.py
```

In the browser (see `docs/PUBLISH_ON_WEBSITE.md`): `pip install pygbag`, `python tools/make_web_copy.py --edition site`, `python -m pygbag build_web/site/elsc-game`, then open http://localhost:8000.
