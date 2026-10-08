# Update 06 — The ELSC Study Pocket (Oct 5, 2026, version 2 of the shell)

On a phone held upright, the game sits inside an **original handheld-console shell**, the **ELSC Study Pocket**:
- A pencil-yellow body, with a **thin bezel so the game screen is as wide as the phone**
- A **slide pad**, a big green **OK** button and a **BACK** button
- Small **PAUSE** and **SOUND** buttons, and a **status light**

It shows players where their thumbs go, lets them use menus with buttons, and makes it obvious whether the game is loading or running. It's our own design, not a copy of any real console.

Pictures: `docs/art/handheld/handheld_all.png` (loading, menus with slide + OK, playing, and an older shorter phone).

Already made and in this pack:
- `assets/sprites/handheld/`: `handheld_top.png` (268 × 280, with the screen hole), `handheld_filler.png` (268 × 1, plain body, repeated on tall phones), `handheld_bottom.png` (268 × 212, pad and buttons), `handheld_parts.png` (buttons up/down, sound-off mark, status lights, the ELSC brand plate) and `handheld_skin.json` (every position)
- `web/app/handheld_loading.png`: the whole shell with "LOADING..." and a red light, for the web page while the game engine downloads
- `art_tools/make_handheld.py` and `make_handheld_mockups.py`: the scripts that drew them

If an older copy of this update was copied in before, delete `assets/sprites/handheld/handheld_skin.png` and `web/app/handheld_skin_loading.png` (they're replaced by the files above).

**Claude Code:**
1. Append the section "## 19.8" below to the end of `docs/GAME_SPEC.md` (replace any earlier 19.8). Add Steps 35–36 below to the end of `docs/BUILD_PLAN.md`, before the "Later" section (replace any earlier 35–36). Keep all the existing ticks and text.
2. If a mobile step (31–34) is in progress, finish it first. Then do **Step 35 only**, stop, and tell me how to test it.
3. Computers (keyboard mode) never show the shell, and the desktop game (`python main.py`) doesn't change.

---

## 19.8 The ELSC Study Pocket (the phone shell)

**When:** touch mode (§19.1) **and** the screen is taller than it is wide. Keyboard mode or landscape: no shell (as in §19.2).

**Building the picture** (all numbers in `handheld_skin.json`, so the art can change without code changes):
- The skin is 268 skin-pixels wide. Its height = the phone's height × (268 ÷ the phone's width), but at least `min_height` (492)
- Draw `handheld_top.png` at the top. Repeat `handheld_filler.png` down to `height − 212`. Draw `handheld_bottom.png` at the bottom
- On tall phones, if the gap between top and bottom is 30 or more, draw the `brand_plate` centered in it
- The game's 256 × 240 screen goes into the hole at (6, 22), drawn under the top piece
- Then draw the status light and any pressed or muted buttons from `handheld_parts.png`
- Scale the whole thing with nearest-neighbor to the phone's width. If the phone is too short for `min_height`, scale it to fit the height instead and center it on black

**The buttons** (circles in the bottom piece; touch radius = `touch_r`, a bit bigger than the drawing; draw the `_down` sprite while a finger is on one):

| Button | Does | Same as |
|---|---|---|
| **OK** (big, green) | Choose the menu item / continue / type the highlighted letter | Enter |
| **BACK** | Go back in menus, delete a letter in the letter grid | Esc in menus, Backspace in the grid |
| **PAUSE** | Open / close the pause menu during play | Esc during play |
| **SOUND** | Sound on / off for the whole game; draw `sound_off_mark` while off (remembered until the page closes) | — |

**The slide pad:**
- **During play:** the floating stick (§19.3). A thumb down **anywhere except the buttons and the HUD** steers, and the slide pad is the natural place. The dotted guide ring shows where the thumb landed
- **In menus and the letter grid:** sliding moves the cursor like the arrow keys. One step when the direction starts; holding it repeats after 0.4 s, then every 0.15 s. So players can do everything with **slide + OK + BACK** without touching the small screen
- Tapping items on the game screen still works too (§19.4)

**Status light:**

| Light | Means |
|---|---|
| Red | Loading (on the web page), or the score server can't be reached (OFFLINE) on the high score screens |
| Green | The game is running |
| Off | Paused |

**Loading:** `tools/build_web.py` adds a full-screen black layer to the built `index.html` showing `handheld_loading.png` (copied next to it), sized to the phone's width and centered, on top of pygbag's own loading bar. The game removes that layer (through pygbag's JavaScript bridge) on its first frame. On computers, the same layer shows the picture smaller in the middle of the page while loading.

**Hints in the shell:** the stage intro's touch hint becomes **"SLIDE ON THE PAD / LIFT TO SIT"**, and menu hints say **"SLIDE + OK"**.

**Settings:** `HANDHELD_SHELL = True` (turn the shell off), and the menu repeat times (0.4 s / 0.15 s).

---

## Step 35 — The Study Pocket shell
- [ ] In touch mode and portrait, the game is drawn inside the shell (top, filler, bottom, brand plate), as wide as the phone, crisp, and scaled down on short phones (§19.8)
- [ ] OK, BACK, PAUSE and SOUND work, with pressed and muted looks
- [ ] The slide pad moves the menu cursor (with repeat) in menus and the letter grid, and steers during play; the thumb also steers anywhere except the buttons and the HUD
- [ ] Status light: green running, off paused, red when offline
- [ ] Keyboard mode or landscape: no shell (as before)

**Test:** on a phone held upright, do everything with **slide + OK + BACK**: choose a level, choose a character, play a run, enter a name with the letter grid (slide to a letter, OK to type, BACK to delete), and look at HIGH SCORES. Tap PAUSE (the light goes off and the pause menu opens), tap SOUND (silence, red slash), and tap SOUND again. Turn the phone sideways: the plain game, no shell. On the computer: no shell. Compare with `docs/art/handheld/handheld_all.png`.

## Step 36 — Loading screen, then rebuild and publish
- [ ] `tools/build_web.py` copies `web/app/handheld_loading.png` and adds the loading layer to both editions' `index.html`; the game hides it on its first frame (§19.8)
- [ ] Rebuild both editions, test on one iPhone (Safari) and one Android phone (Chrome), then upload both (`docs/PUBLISH_ON_WEBSITE.md`)

**Test:** open the real link on a phone over mobile data. The yellow device with LOADING... and a red light appears straight away, then TAP TO PLAY with a green light.
