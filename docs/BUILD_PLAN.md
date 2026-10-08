# ELSC Game — Build Plan (v1)

Build **one step at a time**. Each step ends with something you can run and see. After each step, Claude Code stops, explains in plain words what it added, and tells you how to test it. Tick the box when a step works.

To start a step, tell Claude Code: **"Do step 0"** (then 1, 2, 3 …).

The rules are in `docs/GAME_SPEC.md`; the art and how to use it is in `assets/sprites/README.md`; pictures of every screen are in `docs/art/flow/`.

---

## Step 0 — Setup check
- [x] Python 3 and pygame installed (`pip install pygame`)
- [x] `python main.py` opens a window titled "ELSC Game": the 256 × 240 NES screen scaled 3× (768 × 720), black, and it closes cleanly

**Test:** the window opens at 768 × 720 and closes without errors.

## Step 1 — Settings, sprites and the room
- [x] `settings.py` with every number from GAME_SPEC §3, each with a plain-English comment
- [x] A sprite loader that reads the `.json` files in `assets/sprites/`
- [x] `layout.py` with every bookshelf, wall, table, desk, the whiteboard and all 31 chairs from GAME_SPEC §4
- [x] The room is drawn with the real sprites (carpet checkerboard, shelves, chairs facing their tables, tables, whiteboard, placeholder walls and desks). For now, show the top-left of the room in the play view, with an empty black HUD strip on top

**Test:** compare with `docs/art/stage_with_sprites.png`. Every chair faces its table, and the long table has 3 chairs on each side.

## Step 2 — The student walks and the camera follows
- [x] Boy at the start tile V2, facing down
- [x] Arrow keys move him at the student speed (diagonals too, same speed), with the 2-frame walk and the standing pose
- [x] Solid objects block him and he slides along them; he walks over chairs
- [x] The camera follows him and stops at the room's edges

**Test:** walk everywhere, including between tables and into the dead-end corridor. You can't pass through anything solid, and you never see past the edge of the room.

## Step 3 — Studying, the meter, the chair bonus and the HUD
- [x] Standing still on a chair = sitting and studying, with the seated sprites and head nod (the `S` chair drawn over the student)
- [x] The meter fills in points (1 per second), with the chair bonus for the first 2 seconds at a new table (green 3, red 2, white 1, blue 1)
- [x] "+1 / +2 / +3" pop-ups each second, and the study bar flash
- [x] HUD: stage and character on the left, the timer in the middle (red in the last 10 s), the study bar on the right; text drawn with `font.png`
- [x] 60-second countdown; for now, just freeze at 0

**Test:** sit on a green chair: you see +3, +3, then +1. Move to another chair at the same table: only +1. Go to a different table's red chair: +2, +2, then +1.

## Step 4 — The Noise Tornado (Stage 1)
- [x] The Stage 1 cloud (2 × 2 tiles) at H22, animating its 6 frames
- [x] Random mode: floats over furniture, stays inside the room
- [x] Noise bubbles pop out every 0.7 s

**Test:** it wanders the whole room, passes over tables, never leaves the room, and keeps popping bubbles.

## Step 5 — Getting hit
- [x] Touching it: −10% of the bar, knocked back 2 tiles (stopping at solid things), no steering during the push
- [x] 1 second of invincibility with the Zelda-style hit flash (color swaps), and no studying while flashing

**Test:** walk into the cloud. The bar drops, you get pushed back and flash, and you can't be hit twice in a row. Get hit next to a table and make sure you never end up inside it.

## Step 6 — Stages 2 and 3
- [x] Per-stage size, speed, hitbox, notice time and pass mark from `settings.py`
- [x] Noticing, lunge, the 3-bubble burst, chasing, and back to random when you stop studying
- [x] Debug keys 1 / 2 / 3 to jump between stages (behind the debug setting)

**Test:** in Stage 2, study for 3 seconds: bubbles burst and it lunges at you. Stand up and it goes back to wandering. Stage 3 reacts after 1.5 seconds and is the big 4 × 4 cloud.

## Step 7 — Time's up and the test
- [x] At 0: freeze and the "TIME'S UP!" banner
- [x] Results screen: "THE TEST", the bar, "DID YOU PASS?", then PASSED! or FAILED...
- [x] Passed Stage 1/2 → next stage (empty meter). Passed Stage 3 → "YOU PASSED THE COURSE!!!". Failed → restart from Stage 1 for now

**Test:** play through all 3 stages. Fail one on purpose.

## Step 8 — Title, character select, stage intro and pause
- [x] Title screen with START / OPTIONS / STAGE CODE (OPTIONS and STAGE CODE can be placeholders for now)
- [x] Character select (boy or girl), and the girl plays everywhere the boy did
- [x] Stage intro "STAGE N / READY, SET, STUDY! / PASS MARK: ???"
- [x] Esc pause: CONTINUE / RESTART (this stage) / SOUND (placeholder) / QUIT TO TITLE
- [x] Failing and finishing the course both return to the title

**Test:** compare every screen with `docs/art/flow/`. Play as the girl.

## Step 9 — Stage codes
- [x] Fail counts per stage while the game runs
- [x] The code on the FAILED screen after 5 fails of Stage 2 (`MATHCLASS`) or Stage 3 (`COMPUTERSCIENCECLASS`)
- [x] The Stage Code screen: typing, case doesn't matter, Enter / Backspace / Esc, "WRONG CODE!" in red
- [x] A right code goes to character select, then starts at that stage

**Test:** type `mathclass` and you start at Stage 2. Type something wrong and see "WRONG CODE!". Fail Stage 2 five times and the code appears.

## Step 10 — Options
- [x] Options and the pause SOUND screen: MUSIC and SOUND FX volume bars (0–10), stored for later (no sound yet)

**Test:** change the volumes, leave, come back: they're remembered while the game runs.

## Step 11 — Playtest and tune
- [x] Play all 3 stages many times
- [x] Tune the numbers in `settings.py` (speeds, pass marks, bonus points, notice times) until each stage feels right

**v1 is done** when you can play from the title screen through all 3 stages, as the boy or the girl, with no crashes. 🎉

## Step 12 — Difficulty modes (Easy / Normal / Hard)
- [x] New **mode select** screen after START (and after a correct stage code), before character select. Match `docs/art/modes/mode_select.png`
- [x] **Easy = 1 noise cloud** (exactly the game as it is now), **Normal = 2**, **Hard = 3**, in every stage. The number per mode goes in `settings.py`
- [x] Extra clouds start at **E3** (cloud 2) and **O22** (cloud 3); every cloud uses its stage's size, speed, hitbox and notice time, wanders on its own and pops its own bubbles
- [x] When the student has studied for the notice time, **all** clouds notice, lunge, burst bubbles and chase; they all go back to random when the student stops studying
- [x] One hit at a time: the 1 second of invincibility protects from every cloud
- [x] The mode shows on the stage intro ("NORMAL MODE") and in the HUD next to "STAGE N", in its color (EASY green, NORMAL yellow, HARD red)
- [x] The chosen mode stays for all 3 stages; Restart (pause) keeps it

**Test:** play Easy: nothing has changed. Play Normal: two clouds in Stage 1. Play Hard: three big clouds in Stage 3. Study too long and watch them all come for you. Compare with `docs/art/modes/`.

## Step 13 — Main theme and menu sounds
- [x] `main_theme.ogg` loops on the title screen and all menus (`pygame.mixer.music`), keeps playing smoothly between menus, and fades out (~0.5 s) when a stage intro starts. Silent during play for now
- [x] `sfx_cursor.wav` plays every time a menu cursor moves (all menus, including pause and the volume bars)
- [x] `sfx_select.wav` plays every time something is chosen with Enter
- [x] Options: MUSIC controls the theme volume and SOUND FX controls the effects volume (0–10, 0 = silent), and changes take effect right away
- [x] If a sound file is missing, the game still runs, silently

**Test:** the theme starts on the title screen, keeps going through the menus and fades when Stage 1 begins. Every cursor move blips and every choice chirps. Turning MUSIC to 0 silences the theme.

## Step 14 — Music and sound everywhere
- [x] **Music** (`pygame.mixer.music`, one at a time): the main theme in menus; `stage_music.ogg` during play; switch to `stage_music_hurry.ogg` at **15 seconds left**; `victory_song.ogg` on the course complete screen. Pause pauses the music, Continue resumes it, and time's up stops it
- [x] **Jingles** (`pygame.mixer.Sound`): `jingle_ready.wav` on every stage intro; `jingle_drumroll.wav` while "DID YOU PASS?" builds; `jingle_passed.wav` / `jingle_failed.wav` on the reveal
- [x] **Reused sounds**, exactly as in GAME_SPEC §15:
  - `sfx_cursor.wav`: typing a code, Backspace, pause open/close, Esc/back, the +1 pop-up
  - `sfx_select.wav`: sitting down, the +2 / +3 pop-ups
  - `jingle_ready.wav`: the study bar reaching full
  - `jingle_passed.wav` / `jingle_failed.wav`: a correct / wrong stage code
  - the first **0.4 s** of `jingle_failed.wav` when you get hit
  - the first **0.5 s** of `jingle_drumroll.wav` when the tornado notices you (once, even with several clouds)
- [x] The hurry-up time (15 s) and both short lengths live in `settings.py`
- [x] MUSIC volume controls the 4 `.ogg` files, SOUND FX controls the 6 `.wav` files
- [x] If any sound file is missing, the game still runs

**Test:** play a full run. Menus have the main theme; the stage intro beeps "ready, set, STUDY!"; the stage music plays and speeds up at 0:15; sitting down chirps; +1 blips and +3 chirps; getting hit bonks; studying too long in Stage 2 gives a quick drumroll as the tornado lunges; time's up goes silent, then the drumroll, then the pass or fail jingle; finishing Stage 3 plays the victory song.

## Step 15 — Levels and the bigger study bar
- [x] Mode select becomes **level select** ("CHOOSE YOUR LEVEL", LEVEL 1 / 2 / 3), matching `docs/art/v2/01_level_select.png`
- [x] Each level has its own stages, round lengths, clouds per stage, cloud sizes, speed, notice time, pass marks, hit damage (§17.1)
- [x] Level 3: clouds keep chasing for 3 s after you stop studying
- [x] Cloud start tiles are the cloud's center, clamped inside the room; hurry-up music at 10 s left in Level 1, 15 s in Levels 2–3
- [x] Extra cloud start tiles M3 and E15 for clouds 4 and 5
- [x] The bar holds 150 points; studying 5 per second; chair bonus 15 / 10 / 5 / 5 (§17.2)
- [x] HUD shows "LV1 / LV2 / LV3" in the level's color, then "STAGE N"; the stage intro shows "LEVEL N"
- [x] Finishing the last stage of a level (3 or 5) shows YOU PASSED THE COURSE!!!
- [x] Debug keys 1–5 jump to that stage of the current level (still behind the debug setting); keys above the level's stage count do nothing

**Test:** play Level 1 (30 s rounds, clouds only wander, 3 stages). Choose Level 2 and press 3 (debug keys): 3 medium clouds and a 45 s round. Play Level 3: every cloud is big, and they keep chasing for a moment after you stand up.

## Step 16 — The new room: desks, coffee station, Haruna and Hitomi sitting
- [x] Remove the desk placeholders; draw Haruna's desk, Hitomi's U-shaped desk (gate closed), both office chairs and the coffee station (§17.3), with carpet under the curved pieces
- [x] Haruna sits and types at (18, 4); Hitomi sits and works at (21, 10)
- [x] New solid areas: the coffee station, both desks, Haruna, and the inside of Hitomi's desk
- [x] Compare with `docs/art/v2/00_room_v2.png`

**Test:** walk around the whole room. You can't walk into the coffee station, either desk, Haruna, or inside Hitomi's desk. Nothing else changed.

## Step 17 — The book
- [x] When the student sits, draw `book_<side>` over them (all 4 sides) using `offset_from_seated` (§17.7)

**Test:** sit on chairs on all four sides of a table; the book sits in the student's hands (or on the table for `S` chairs).

## Step 18 — Speech bubbles and Haruna calling out
- [x] A speech bubble helper: white box, 1 px black border, black text, `bubble_tail`, kept on screen (§17.8)
- [x] Haruna calls out every 15 s: hands-up frames for 2 s and the bubble "BE QUIET PLEASE, / PEOPLE ARE STUDYING!" for 2.5 s (§17.4). Blip when a bubble appears

**Test:** stand near Haruna for 30 s: she calls out twice. The bubble never goes off screen. Compare with `docs/art/v2/02_haruna_calls.png`.

## Step 19 — Power-ups part 1: coffee and the headphones
- [x] Item helper: items bob 1 px, one of each per stage, reset every stage and on Restart; grab rules for floor and table items (§17.6)
- [x] **Coffee** in front of the coffee station: 10 s at 1.5× walking and studying
- [x] **Headphones:** at half time, if the bar is under 50%, Haruna tosses them to (17, 6); grabbing them gives 8 s of Mario-star blinking, clouds pass through you and can't notice you
- [x] Sounds from §17.14

**Test:** grab the coffee: you're faster and the bar fills faster for 10 s. Study very little until half time: Haruna drops the headphones. Grab them and walk through a cloud: nothing happens. Study a lot before half time: no headphones.

## Step 20 — Hitomi walks out
- [x] Triggers at 50% and 70% (and 30% in Level 3), each once per stage (§17.5)
- [x] The gate opens (and stays open while she's out), she walks out, "DID YOU STUDY?!" with the pointing frames, then she moves by level (Level 1 wanders, Level 2 comes at you, Level 3 stands on the free chair closest to you), then walks back in
- [x] She's solid, never touches a seated student, never takes points; pushes a standing student 1 tile in Levels 2–3
- [x] Sounds from §17.14

**Test:** in each level, study up to 50%: Hitomi comes out. Level 1: she just wanders. Level 2: she follows you and pushes you. Level 3: she steals the chair next to you. She can't reach you while you're seated. Compare with `docs/art/v2/03_hitomi_out.png`.

## Step 21 — Power-ups part 2: the laptop (Levels 2 and 3)
- [x] Laptop on table T4. Walk up to the table: freeze, "DEADLINE EXTENDED!" box, the timer ticks up +10 (yellow, a blip each second), hold 0.5 s, carry on (§17.6)
- [x] The music follows the time left (back to normal stage music if above the hurry-up time)

**Test:** in Level 2 with about 12 s left, grab the laptop: the timer goes up to about 22 and the hurry-up music changes back. Compare with `docs/art/v2/04_deadline_extended.png`. Level 1 has no laptop.

## Step 22 — Power-ups part 3: the highlighter (Levels 2 and 3)
- [x] Highlighter on table T7: 8 s where every chair gives 15 per second, every chair is drawn green, and the book blinks green

**Test:** grab it, sit on a blue chair: +3 every second. All chairs look green until it ends. Compare with `docs/art/v2/05_highlighter.png`.

## Step 23 — Power-ups part 4: the pizza (Level 3)
- [x] Pizza box on top of bookshelf S2. Bumping the shelf drops it behind the shelf (0.4 s arc), open, at pixel (328, 272)
- [x] For 8 s every cloud goes to the pizza and wanders around it, ignoring you; then it vanishes in 3 noise bubbles and the clouds go back to normal

**Test:** in Level 3, walk into the right bookshelf: the pizza falls, all the giant clouds rush to it, and you can study in peace for 8 s. Compare with `docs/art/v2/06_pizza_lure.png`.

## Step 24 — The new test screen with Haruna and Hitomi
- [x] Portraits on light-blue cards, Haruna asks "DID YOU PASS?" during the drumroll, Hitomi answers in a typed dialogue box, cheering or shaking her head (§17.9)

**Test:** pass a stage and fail one. Compare with `docs/art/v2/07_results_passed.png` and `08_results_failed.png`.

## Step 25 — Score, names and high scores
- [x] Stage and run scores with the level multiplier; "SCORE +N" on the PASSED box (§17.10)
- [x] After every run: YOU SCORED; name entry (up to 10 letters) if it makes that level's top 10
- [x] HIGH SCORES on the title menu, Left / Right between levels; saved to `highscores.json`
- [x] Stage codes per level (§17.11); a code skips level select

**Test:** finish a run, type a name, check HIGH SCORES. Close the game and open it again: the score is still there. Try `GRAMMAR` and `FINALEXAM`. Compare with `docs/art/v2/09_score_entry.png` and `10_high_scores.png`.

## Step 26 — Sound check and playtest
- [x] Every sound in §17.14 plays at the right moment
- [x] Play all three levels start to finish, as the boy and the girl. No crashes
- [x] Tune `settings.py` until Level 1 feels easy, Level 2 fair, and Level 3 like real panic but passable

**Version 2 is done** when you can play all three levels from the title screen to the high score list with no crashes. 🎉

## Step 27 — Ready for the browser
- [x] The main loop is async (`async def main()`, `await asyncio.sleep(0)` every frame, `asyncio.run(main())`), and the desktop game still runs exactly as before (§18.1)
- [x] All sounds load from `.ogg` (falling back to `.wav` if an `.ogg` is missing)
- [x] "Play only the first N seconds" uses a timer that stops the channel, not `maxtime`
- [x] In the browser only: the CLICK TO PLAY screen first; the game scales to fit the page and stays crisp
- [x] `tools/make_web_copy.py --edition site|friends`: copies only the game's `.py` files and `assets/` into `build_web/<edition>/elsc-game/` and sets `EDITION` in that copy's `settings.py` (§18.4)
- [x] `EDITION = "site"` and `SCORE_SERVER_URL = ""` added to `settings.py` (not used yet)

**Test:** `python main.py` still plays normally. Then `pip install pygbag`, `python tools/make_web_copy.py --edition site`, `python -m pygbag build_web/site/elsc-game`, and open http://localhost:8000 in Chrome: CLICK TO PLAY, then the title with music, and a full run with sound, the bonk, the drumroll start and the pass jingle.

## Step 28 — Online high scores
- [x] `online.py`: background requests to `SCORE_SERVER_URL` (browser: JavaScript `fetch` via pygbag's bridge; desktop: `urllib` in a thread), 8 s timeout, never freezing the game; POST bodies are JSON as plain text, and every request includes the edition (§18.2)
- [x] HIGH SCORES screen: LOADING..., the online top 10 for this edition, Left / Right between levels, OFFLINE plus the local list if it fails (§18.3)
- [x] After a run: the qualify check against the online list, name entry, SAVING... then SAVED! (with the list, new score in yellow) or COULD NOT SAVE; show the name the server returns
- [x] `SCORE_SERVER_URL = ""` still works fully offline, as before

**Test:** set up the Google Sheet (`server/SETUP_SCORES.md`) and paste the URL in `settings.py`. On desktop: finish a run, save a name, and see it in the Sheet's **Scores** tab and on the HIGH SCORES screen. Turn off the Wi-Fi: HIGH SCORES shows OFFLINE and the game doesn't freeze. Try a rude name: it saves as PLAYER.

## Step 29 — Counting plays
- [x] A new random session id for every run; `start` after character select (or after a stage code), `finish` when the run ends, each with level, character and edition (§18.2)
- [x] Fire and forget: the game never waits for these

**Test:** play two short runs and check the Sheet: the **Plays** tab has a start and a finish row for each run (edition "site"), and **Summary** counts them.

## Step 30 — Build both editions
- [x] `tools/build_web.py`: runs `make_web_copy.py` for **site** and **friends**, then builds each with pygbag, ending with two upload-ready folders (`build_web/site/elsc-game/build/web/` and `build_web/friends/elsc-game/build/web/`), and prints their sizes
- [ ] Both are under 15 MB, and both work in Chrome, Safari and Edge (CLICK TO PLAY, sound, keyboard, scores)
- [ ] A friends-edition score shows in the friends top 10, not the site's, and the Sheet's Summary shows "Games from the friends link"
- [x] `build_web/` is ignored by git (if the project uses git)

**Test:** `python tools/build_web.py`, then test each folder locally with pygbag. Then follow `docs/PUBLISH_ON_WEBSITE.md` to upload both, and play each from its real link on a second computer.

**The web version is done** when the site edition plays on your website, the friends link works, and both show up in the Google Sheet. 🎉

---

## Step 31 — Touch mode, and a phone page that doesn't move
- [x] Touch mode / keyboard mode: guessed at start-up, decided by the first tap or click, and switching live (§19.1)
- [x] TAP TO PLAY / CLICK TO PLAY by mode
- [x] The game fills the phone's width in portrait (nearest-neighbor, any scale) and fits the height in landscape; the black space below the game is part of the touch area (§19.2)
- [x] No zooming, scrolling, pull-to-refresh, text selection or long-press menus: the viewport tag and CSS from §19.2 are in the built `index.html` (`tools/build_web.py` adds them after pygbag builds)
- [x] A small helper that turns a touch into **game pixels** (256 × 240), so all touch distances in the spec work on every screen size

**Test:** build the site edition and open it on a phone on the same Wi-Fi (pygbag's local address with your computer's IP, or upload it to a test folder). TAP TO PLAY shows; after the tap, the music plays; pinching, dragging and pulling down don't move the page. On the computer it still says CLICK TO PLAY and works with the keyboard.

**Order (decided Oct 5):** Steps 32 → 33 → 35 → 34 → 36, so the shell is built on top of the touch controls and the game is published once at the end.

## Step 32 — Slide anywhere to move, tap the top bar to pause
- [x] The floating stick: thumb down anywhere outside the HUD, 8 directions, 6 px dead zone, the center follows past 24 px, lift = stop (and sit on a chair), only the first finger steers (§19.3)
- [x] The faint dotted ring and thumb dot while the thumb is down (setting `TOUCH_STICK_VISIBLE`)
- [x] Tap the HUD bar to pause (§19.4). In touch mode the stage intro shows "SLIDE ANYWHERE TO MOVE / LIFT TO STOP AND SIT"

**Test:** on a phone, play a full Level 1 run: slide to move in all 8 directions, lift on a chair to sit and study, dodge a cloud, and tap the top bar to pause. Compare with `docs/art/mobile/02_playing.png`.

## Step 33 — Tap every menu, and the letter grid
- [x] Every menu item and every "press Enter" screen works with a tap (§19.4). Taps count on release, only if the finger moved less than 6 px
- [x] The letter grid for names and stage codes in touch mode: A–Z, 0–9, SPACE, DEL, OK; numbers and SPACE greyed out for stage codes; a yellow flash and blip on each tap (§19.5)
- [x] Hints say TAP instead of ENTER in touch mode

**Test:** on a phone, go from TAP TO PLAY through level select, character select, a full run, the test, the score screen and the letter grid (save a name), then HIGH SCORES (switch levels with < >). Then type a stage code with the grid. Nothing should need a keyboard. Compare with `docs/art/mobile/03_tap_menus.png` and `04_name_grid.png`.

## Step 34 — Phone stats, Add to Home Screen, and publish
- [x] `start` and `finish` send `"device": "phone"` or `"computer"` (§19.7)
- [x] `tools/build_web.py` copies `web/app/` (manifest and icons) next to each edition's `index.html` and adds the `<head>` tags from §19.6
- [x] Rebuild both editions, test on **one iPhone (Safari) and one Android phone (Chrome)**, plus a computer, then upload both (`docs/PUBLISH_ON_WEBSITE.md`) *(Oct 6: tested on an iPhone and a computer and uploaded; no Android phone)*
- [ ] "Add to Home Screen" on a phone gives the ELSC icon and opens the game full-screen *(skipped Oct 6: Mike doesn't need it; the files are in the build anyway)*

**Test:** play one game on a phone and one on a computer. In the Google Sheet, the **Plays** tab's **Device** column says "phone" and "computer", and **Summary** counts "Games on phones / tablets". Add the game to a phone's home screen and open it from the icon.

## Step 35 — The Study Pocket shell
- [x] In touch mode and portrait, the game is drawn inside the shell (top, filler, bottom, brand plate), as wide as the phone, crisp, and scaled down on short phones (§19.8)
- [x] OK, BACK, PAUSE and SOUND work, with pressed and muted looks
- [x] The slide pad moves the menu cursor (with repeat) in menus and the letter grid, and steers during play; the thumb also steers anywhere except the buttons and the HUD
- [x] Status light: green running, off paused, red when offline
- [x] Keyboard mode or landscape: no shell (as before)

**Test:** on a phone held upright, do everything with **slide + OK + BACK**: choose a level, choose a character, play a run, enter a name with the letter grid (slide to a letter, OK to type, BACK to delete), and look at HIGH SCORES. Tap PAUSE (the light goes off and the pause menu opens), tap SOUND (silence, red slash), and tap SOUND again. Turn the phone sideways: the plain game, no shell. On the computer: no shell. Compare with `docs/art/handheld/handheld_all.png`.

## Step 36 — Loading screen, then rebuild and publish
- [x] `tools/build_web.py` copies `web/app/handheld_loading.png` and adds the loading layer to both editions' `index.html`; the game hides it on its first frame (§19.8)
- [x] Rebuild both editions, test on one iPhone (Safari) and one Android phone (Chrome), then upload both (`docs/PUBLISH_ON_WEBSITE.md`) *(Oct 6: tested on an iPhone and a computer and uploaded; no Android phone)*

**Test:** open the real link on a phone over mobile data. The yellow device with LOADING... and a red light appears straight away, then TAP TO PLAY with a green light.

## Later (not part of v1)

- **Version 2:** teachers, power-ups, the door, office and extra desk, and the rest of the list in `docs/GAME_SPEC.md` §16
