# GAME_SPEC §19 (to add to GAME_SPEC.md)

Claude Code: append everything below this line to the end of `docs/GAME_SPEC.md` (see `UPDATE_05_mobile.md`).

---

## 19. Phones and tablets (touch, no on-screen controls)

The **same web version** (both editions) also plays on phones and tablets. **No buttons or D-pad are drawn.** The game notices a touch screen by itself and switches to touch controls; on a computer nothing changes. The desktop game (`python main.py`) is not affected. Mockups: `docs/art/mobile/` (`phone_mockups_all.png`).

### 19.1 Touch mode or keyboard mode (automatic)
- **At start-up** (browser only): ask the page whether the main pointer is a finger, with `matchMedia("(pointer: coarse)").matches` or `navigator.maxTouchPoints > 0` through pygbag's JavaScript bridge. If yes, start in **touch mode**; otherwise **keyboard mode**
- **The first tap or click decides:** a touch on the TAP / CLICK TO PLAY screen = touch mode; a mouse click or key = keyboard mode
- **It switches live:** any key press switches to keyboard mode; any touch switches to touch mode (a tablet with a keyboard, or a touchscreen laptop, just works). Only the hints and the name entry change between modes; everything else accepts both at all times
- The start screen says **"TAP TO PLAY"** in touch mode and **"CLICK TO PLAY"** in keyboard mode

### 19.2 The phone page
- Portrait first. The 256 × 240 game is scaled with nearest-neighbor to the **full width** of the screen (any scale, not only whole numbers), placed near the top. The black space below it is part of the touch area. Landscape also works: scale to fit the height, centered
- **The page never moves:** no pinch-zoom, scrolling, pull-to-refresh, text selection, or long-press menus. The HTML page gets `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">` and CSS `touch-action: none; overscroll-behavior: none; user-select: none; -webkit-touch-callout: none;` on the page and canvas, with a black background
- Sound starts after the first tap (already handled by TAP TO PLAY)

### 19.3 Moving: "slide anywhere" (a floating stick)
- **Put a thumb down anywhere** on the screen except the HUD bar (the black space under the game counts too). That spot becomes the stick's center
- **Slide:** the student walks in that direction, snapped to the 8 directions (like holding arrow keys, including diagonals), at normal speed. Moving less than **6 game pixels** from the center does nothing (dead zone)
- If the thumb goes more than **24 game pixels** from the center, the center follows the thumb, so changing direction stays quick
- **Lift the thumb:** the student stops, and **sits if on a chair**, exactly like letting go of the arrow keys
- Only the first finger steers; other fingers are ignored
- **Faint guide:** a dotted white ring (radius 14) at the center and a small dot under the thumb, drawn only while the thumb is down (setting `TOUCH_STICK_VISIBLE = True`). Mockup: `docs/art/mobile/02_playing.png`
- Distances are in game pixels (the 256 × 240 screen), so it feels the same on every phone. All numbers go in `settings.py`

### 19.4 Tapping (menus and everything else)
- **Any menu item can be tapped:** it moves the cursor there and chooses it, like Enter. This covers the title, level select (tap a box), character select (tap the boy or girl), options (tap a volume segment to set it, tap BACK), pause (CONTINUE / RESTART / SOUND / QUIT TO TITLE), high scores (tap "<" or ">" for the level, tap anywhere else to go back) and stage code
- **"Press Enter" screens** (stage intro, results, course complete, score) continue with **a tap anywhere**
- **Pause during play:** tap the **HUD bar** (the top 64 game pixels). Esc still works
- Taps are measured on release, and only if the finger moved less than 6 game pixels, so a slide never counts as a tap
- In touch mode, the hints change: stage intro **"SLIDE ANYWHERE TO MOVE / LIFT TO STOP AND SIT"**, and "TAP" instead of "ENTER" / "PRESS ENTER" in menu hints

### 19.5 Typing names and stage codes: the letter grid
- In touch mode, the name entry (§17.10, §18.3) and the stage code screen show a **letter grid** under the text box: A–Z and 0–9 in rows of 8, then **SPACE** and **DEL**, and a big **OK** button. Mockup: `docs/art/mobile/04_name_grid.png`
- Cells are at least 24 × 18 game pixels (big enough for a thumb). The tapped cell flashes yellow for 0.1 s, with the menu blip
- Stage codes are letters only: the numbers and SPACE are greyed out there
- In keyboard mode the grid isn't shown; typing works as before. If a key is pressed while the grid is showing, hide it

### 19.6 Add to Home Screen (feels like an app)
- `web/app/` holds `manifest.webmanifest` and the icons `icon-180.png`, `icon-192.png`, `icon-512.png`
- The web build copies these next to `index.html` and adds to its `<head>`: `<link rel="manifest" href="manifest.webmanifest">`, `<link rel="apple-touch-icon" href="icon-180.png">`, `<meta name="apple-mobile-web-app-capable" content="yes">`, `<meta name="mobile-web-app-capable" content="yes">`, `<meta name="theme-color" content="#000000">` and the viewport tag from 19.2. Players use their browser's "Add to Home Screen" and get an ELSC icon that opens full-screen

### 19.7 Phone or computer in the stats
- Every `start` and `finish` request (§18.2) also sends `"device": "phone"` (touch mode when the run started) or `"computer"`. The updated `server/apps_script/Code.gs` saves it in a new **Device** column and counts it in the Summary
- One shared top 10 for phones and computers (for now)
