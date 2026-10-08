# ELSC Game

**Beat the noise. Pass the test.**

A small top-down, NES Zelda-style game made with Python and pygame. You're a student racing the clock to a test: sit on chairs to fill your study bar, and dodge the clouds of noisy students.

**Play it in your browser:** https://oo0speed0oo.github.io/elsc-game/
(Computers: arrow keys and Enter. Phones: hold the phone upright and use the ELSC Study Pocket's slide pad and buttons.)

## Run it on your computer

```
pip install pygame-ce
python main.py
```

## Build the web version

```
pip install pygbag
python tools/build_web.py
```

This makes `build_web/site/elsc-game/build/web/` (the website edition) and `build_web/friends/elsc-game/build/web/` (the friends edition). See `docs/PUBLISH_ON_WEBSITE.md`.

## What's where

- `main.py`: starts the game; `settings.py`: every number you can tune
- `assets/`: the art and sounds; `art_tools/`: the scripts that drew the art
- `docs/GAME_SPEC.md`: the rules; `docs/BUILD_PLAN.md`: how it was built, step by step
- `server/`: the online high scores (a Google Apps Script and its setup guide)
- `tools/`: the web build; `web/`: the leaderboard page and the phone app files
