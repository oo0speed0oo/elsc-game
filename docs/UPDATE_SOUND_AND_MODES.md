# Update — Modes and all the sound (Sept 28, 2026)

This one package has everything added on Sept 28: the Easy / Normal / Hard modes, and all 10 music and sound files. It replaces Update 01 and Update 02 (you don't need those).

**What this package changes:** it only adds new files and replaces a few documents (`docs/GAME_SPEC.md`, `assets/sounds/README.md`, the scripts in `art_tools/`). It does **not** touch any game code or `docs/BUILD_PLAN.md`.

**Claude Code:**
1. Look at `docs/BUILD_PLAN.md`. Add any of the steps below (Step 12, 13, 14) that aren't there yet to the end of it, in order, before the "Later" section. Don't change or untick anything that's already there.
2. Check which of Steps 12–14 are already done in the code. Do the **first one that isn't done**, then stop and tell me how to test it. I'll ask for the next one.
3. Don't change anything else that already works. The rules are in `docs/GAME_SPEC.md` (§3 settings, §7 modes, §15 sound).

---

## Step 12 — Difficulty modes (Easy / Normal / Hard)
- [ ] New **mode select** screen after START (and after a correct stage code), before character select. Match `docs/art/modes/mode_select.png`
- [ ] **Easy = 1 noise cloud** (exactly the game as it is now), **Normal = 2**, **Hard = 3**, in every stage. The number per mode goes in `settings.py`
- [ ] Extra clouds start at **E3** (cloud 2) and **O22** (cloud 3); every cloud uses its stage's size, speed, hitbox and notice time, wanders on its own and pops its own bubbles
- [ ] When the student has studied for the notice time, **all** clouds notice, lunge, burst bubbles and chase; they all go back to random when the student stops studying
- [ ] One hit at a time: the 1 second of invincibility protects from every cloud
- [ ] The mode shows on the stage intro ("NORMAL MODE") and in the HUD next to "STAGE N", in its color (EASY green, NORMAL yellow, HARD red)
- [ ] The chosen mode stays for all 3 stages; Restart (pause) keeps it

**Test:** play Easy: nothing has changed. Play Normal: two clouds in Stage 1. Play Hard: three big clouds in Stage 3. Study too long and watch them all come for you. Compare with `docs/art/modes/`.

## Step 13 — Main theme and menu sounds
- [ ] `main_theme.ogg` loops on the title screen and all menus (`pygame.mixer.music`), keeps playing smoothly between menus, and fades out (~0.5 s) when a stage intro starts. Silent during play for now
- [ ] `sfx_cursor.wav` plays every time a menu cursor moves (all menus, including pause and the volume bars)
- [ ] `sfx_select.wav` plays every time something is chosen with Enter
- [ ] Options: MUSIC controls the theme volume and SOUND FX controls the effects volume (0–10, 0 = silent), and changes take effect right away
- [ ] If a sound file is missing, the game still runs, silently

**Test:** the theme starts on the title screen, keeps going through the menus and fades when Stage 1 begins. Every cursor move blips and every choice chirps. Turning MUSIC to 0 silences the theme.

## Step 14 — Music and sound everywhere
- [ ] **Music** (`pygame.mixer.music`, one at a time): the main theme in menus; `stage_music.ogg` during play; switch to `stage_music_hurry.ogg` at **15 seconds left**; `victory_song.ogg` on the course complete screen. Pause pauses the music, Continue resumes it, and time's up stops it
- [ ] **Jingles** (`pygame.mixer.Sound`): `jingle_ready.wav` on every stage intro; `jingle_drumroll.wav` while "DID YOU PASS?" builds; `jingle_passed.wav` / `jingle_failed.wav` on the reveal
- [ ] **Reused sounds**, exactly as in GAME_SPEC §15:
  - `sfx_cursor.wav`: typing a code, Backspace, pause open/close, Esc/back, the +1 pop-up
  - `sfx_select.wav`: sitting down, the +2 / +3 pop-ups
  - `jingle_ready.wav`: the study bar reaching full
  - `jingle_passed.wav` / `jingle_failed.wav`: a correct / wrong stage code
  - the first **0.4 s** of `jingle_failed.wav` when you get hit
  - the first **0.5 s** of `jingle_drumroll.wav` when the tornado notices you (once, even with several clouds)
- [ ] The hurry-up time (15 s) and both short lengths live in `settings.py`
- [ ] MUSIC volume controls the 4 `.ogg` files, SOUND FX controls the 6 `.wav` files
- [ ] If any sound file is missing, the game still runs

**Test:** play a full run. Menus have the main theme; the stage intro beeps "ready, set, STUDY!"; the stage music plays and speeds up at 0:15; sitting down chirps; +1 blips and +3 chirps; getting hit bonks; studying too long in Stage 2 gives a quick drumroll as the tornado lunges; time's up goes silent, then the drumroll, then the pass or fail jingle; finishing Stage 3 plays the victory song.

