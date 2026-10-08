# Update 05 — Phones and tablets (Oct 3, 2026)

Many players want to play on their phones. The web version (both editions) gets **touch controls with nothing drawn on the screen**: slide a thumb anywhere to move, lift to sit, tap menus, and a letter grid for names. The game detects touch by itself; computers keep the keyboard exactly as now. Rules: `docs/GAME_SPEC_19_mobile.md`. Phone mockups: `docs/art/mobile/`.

Already made and in this pack:
- `docs/GAME_SPEC_19_mobile.md`: the rules (§19)
- `docs/art/mobile/`: phone mockups (tap to play, playing, tapping menus, the letter grid)
- `web/app/`: the Add to Home Screen icons and `manifest.webmanifest`
- `server/apps_script/Code.gs`: updated to also save **phone / computer** for every play (Mike re-deploys it, see the end)

**Claude Code:**
1. Update the docs, keeping everything already there:
   - Append `docs/GAME_SPEC_19_mobile.md` (from "## 19." down) to the end of `docs/GAME_SPEC.md`. In its first lines, add that §19 adds phones and tablets. In §16, remove "touch controls for phones and tablets"
   - In `CLAUDE.md`, say we're now adding phone and tablet play (§19), and that the game must keep working with the keyboard on computers after every step
   - Add Steps 31–34 below to the end of `docs/BUILD_PLAN.md`, before the "Later" section. Keep all the existing ticks
2. Do **Step 31 only**, then stop and tell me how to test it. I'll ask for the next step each time.
3. After every step: `python main.py` still works, and the browser version still works with a keyboard.
4. Check pygbag's current documentation for touch events (pygame `FINGERDOWN` / `FINGERMOTION` / `FINGERUP`, or mouse events from touches) and for its JavaScript bridge. Use whatever works reliably on both iPhone Safari and Android Chrome.

---

## Step 31 — Touch mode, and a phone page that doesn't move
- [ ] Touch mode / keyboard mode: guessed at start-up, decided by the first tap or click, and switching live (§19.1)
- [ ] TAP TO PLAY / CLICK TO PLAY by mode
- [ ] The game fills the phone's width in portrait (nearest-neighbor, any scale) and fits the height in landscape; the black space below the game is part of the touch area (§19.2)
- [ ] No zooming, scrolling, pull-to-refresh, text selection or long-press menus: the viewport tag and CSS from §19.2 are in the built `index.html` (`tools/build_web.py` adds them after pygbag builds)
- [ ] A small helper that turns a touch into **game pixels** (256 × 240), so all touch distances in the spec work on every screen size

**Test:** build the site edition and open it on a phone on the same Wi-Fi (pygbag's local address with your computer's IP, or upload it to a test folder). TAP TO PLAY shows; after the tap, the music plays; pinching, dragging and pulling down don't move the page. On the computer it still says CLICK TO PLAY and works with the keyboard.

## Step 32 — Slide anywhere to move, tap the top bar to pause
- [ ] The floating stick: thumb down anywhere outside the HUD, 8 directions, 6 px dead zone, the center follows past 24 px, lift = stop (and sit on a chair), only the first finger steers (§19.3)
- [ ] The faint dotted ring and thumb dot while the thumb is down (setting `TOUCH_STICK_VISIBLE`)
- [ ] Tap the HUD bar to pause (§19.4). In touch mode the stage intro shows "SLIDE ANYWHERE TO MOVE / LIFT TO STOP AND SIT"

**Test:** on a phone, play a full Level 1 run: slide to move in all 8 directions, lift on a chair to sit and study, dodge a cloud, and tap the top bar to pause. Compare with `docs/art/mobile/02_playing.png`.

## Step 33 — Tap every menu, and the letter grid
- [ ] Every menu item and every "press Enter" screen works with a tap (§19.4). Taps count on release, only if the finger moved less than 6 px
- [ ] The letter grid for names and stage codes in touch mode: A–Z, 0–9, SPACE, DEL, OK; numbers and SPACE greyed out for stage codes; a yellow flash and blip on each tap (§19.5)
- [ ] Hints say TAP instead of ENTER in touch mode

**Test:** on a phone, go from TAP TO PLAY through level select, character select, a full run, the test, the score screen and the letter grid (save a name), then HIGH SCORES (switch levels with < >). Then type a stage code with the grid. Nothing should need a keyboard. Compare with `docs/art/mobile/03_tap_menus.png` and `04_name_grid.png`.

## Step 34 — Phone stats, Add to Home Screen, and publish
- [ ] `start` and `finish` send `"device": "phone"` or `"computer"` (§19.7)
- [ ] `tools/build_web.py` copies `web/app/` (manifest and icons) next to each edition's `index.html` and adds the `<head>` tags from §19.6
- [ ] Rebuild both editions, test on **one iPhone (Safari) and one Android phone (Chrome)**, plus a computer, then upload both (`docs/PUBLISH_ON_WEBSITE.md`)
- [ ] "Add to Home Screen" on a phone gives the ELSC icon and opens the game full-screen

**Test:** play one game on a phone and one on a computer. In the Google Sheet, the **Plays** tab's **Device** column says "phone" and "computer", and **Summary** counts "Games on phones / tablets". Add the game to a phone's home screen and open it from the icon.

**Phones are done** when someone can open the link on a phone, play a whole run with just their thumb, and save their name, without ever seeing a keyboard. 🎉

---

## For Mike: update the score server (once, about 2 minutes, before Step 34)
1. Open your **ELSC Game Scores** Sheet → **Extensions → Apps Script**
2. Replace everything in `Code.gs` with the new `server/apps_script/Code.gs` and click **Save**
3. Choose **setup** in the dropdown → **Run** (this adds the Device column and the new Summary rows; your scores stay)
4. **Deploy → Manage deployments → the pencil icon → Version: New version → Deploy.** The URL stays the same
