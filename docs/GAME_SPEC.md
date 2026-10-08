# ELSC Game — Game Spec (v1 + version 2 + web + phones)

ELSC stands for **English Language Service Center**, the real office this game is based on. This spec is the source of truth for building v1. The art is already finished (see `assets/sprites/README.md`), and preview pictures of every screen are in `docs/art/`.

**Version 2 is built; the web version is being built now.** Sections 1–15 describe v1. **§17 (Version 2) adds to them, §18 (the web version) adds online play and shared high scores, and §19 adds phones and tablets (touch controls in the web version, and the ELSC Study Pocket shell, §19.8). §17, §18 and §19 win wherever they disagree with §1–15.** Build exactly what's here, no extra features. The ideas in §16 are still off limits.

## 1. Concept

An overhead (top-down), NES Zelda-style game. You play a student racing a 1-minute countdown to a test. You walk around the office and sit on chairs to charge your **study meter**. A **Noise Tornado** (a crowd of noisy students, drawn as a cartoon fight cloud) roams the room; when it hits you, you lose a chunk of your meter and get knocked back. When the timer runs out, you take the test and find out if you studied enough to pass. There are 3 stages in the same room, and the tornado gets smarter, faster and bigger each stage.

## 2. Screen, tiles and camera

- **Tile size:** 16 × 16 px
- **Game screen:** 256 × 240 px (the real NES screen size), drawn to an off-screen surface and **scaled up 3× to a 768 × 720 window** with nearest-neighbor (no smoothing). The scale is a setting (2, 3 or 4)
- **HUD:** the top 64 px of the screen (black strip)
- **Play view:** the 256 × 176 px below the HUD = **16 × 11 tiles**
- **Room:** 24 × 24 tiles (384 × 384 px), bigger than one screen in both directions
- **Camera:** follows the student (student centered), but **stops at the room's edges** so nothing outside the room is ever shown
- **FPS:** 60

## 3. Settings (all in `settings.py`)

Every tunable number lives in **one file, `settings.py`**, grouped, with a plain-English comment on each line, so the owner can change a number, save, and play again. Nothing below may be hard-coded anywhere else.

| Setting | Default | Notes |
|---|---|---|
| Window scale | 3 | 2 = 512 × 480, 3 = 768 × 720, 4 = 1024 × 960 |
| Round length | 60 s | |
| Student speed | 90 px/s | ≈ 5.6 tiles per second. Always faster than the tornado |
| Tornado speed | Stage 1: 36 · Stage 2: 54 · Stage 3: 72 px/s | |
| Tornado size | Stage 1: 32 · Stage 2: 48 · Stage 3: 64 px | 2 × 2, 3 × 3, 4 × 4 tiles |
| Tornado hitbox | Stage 1: 20 · Stage 2: 30 · Stage 3: 40 px (square, centered) | Smaller than the drawing so near misses feel fair |
| Notice time | Stage 1: never · Stage 2: 3 s · Stage 3: 1.5 s | Seconds of charging before it notices you |
| Lunge | 0.5 s at 90 px/s | When it notices you (Stages 2–3) |
| Charge | 1 point per second | 1 point = 5% of the bar; the bar holds 20 points |
| Chair bonus | green 3 · red 2 · white 1 · blue 1 points per second | Only for the first 2 s at a new table (see §6) |
| Bonus length | 2 s | |
| Hit damage | 2 points (10%) | |
| Knockback | 32 px (2 tiles) over 0.2 s | Stays 2 tiles at every tornado size |
| Invincible after a hit | 1 s | |
| Pass mark | Stage 1: 50% · Stage 2: 60% · Stage 3: 70% | Hidden from the player |
| Fails before a stage code appears | 5 | |
| Student hitbox | 12 × 12 px, centered in the 16 × 16 sprite | So squeezing between tables doesn't feel sticky |
| Bubble interval | 0.7 s | Noise bubbles from the tornado |
| Bubbles on lunge | 3 | |
| Timer turns red at | 10 s | |
| Debug keys | off | Step 6 adds 1 / 2 / 3 to jump stages; keep behind this setting |
| Noise clouds per mode | Easy: 1 · Normal: 2 · Hard: 3 | Same size, speed and behavior as that stage's cloud (§7) |
| Main theme volume / sound FX volume | 7 / 7 (out of 10) | The Options screen changes these |
| Hurry-up music starts at | 15 s left | Switch to the fast version of the stage music |
| Hit sound length | 0.4 s | The start of `jingle_failed.wav` |
| "Noticed you" sound length | 0.5 s | The start of `jingle_drumroll.wav` |

Balancing (for example pass marks with the chair bonus) is done later by playing and changing these numbers.

## 4. The room

Coordinates are in **tiles**: `(x, y, width, height)` with `(0, 0)` at the top-left of the room; multiply by 16 for pixels. The owner talks about tiles with **grid names**: columns **A–X** (x = 0–23) and rows **1–24** (y = 0–23), so tile (21, 1) is **V2**. Some chairs sit on half tiles (for example 5.5) so they're centered on a table side; that's intended.

### Map (for checking)

`#` bookshelf, `W` wall, `T` table, `D` desk, `c` chair (half-tile chairs rounded down), `B` whiteboard, `P` student start, `X` tornado start, `.` floor. The tables below are the source of truth.

```
     A B C D E F G H I J K L M N O P Q R S T U V W X
  1  # # # # # # # # # # # # # # # # # # W W W W W W
  2  # # # . . . . . . . . . . . . # # . . . . P . W
  3  # # # . . . . . c T T c . . . # # . . . . . W W
  4  # # # . . . . . . T T . . . . # # . . D . . W W
  5  # # # . . . . . c T T c . . . # # . . D . . W W
  6  # # # . . . . . . T T . . . . # # . . D . . W W
  7  # # # . . . . . c T T c . . . # # . . D . . W W
  8  # # # . . . . . . T T . . . . # # . . . . . W W
  9  # # # . . . . . . . . . . . . . . . c . . D W W
 10  # # # . . c . . . . . c . . . . . c T c D . W W
 11  # # # . c T T c . . c T T c . . . . . . D . W W
 12  # # # . . T T . . . . T T . . . . . . . D . W W
 13  # # # . . c . . . . . c . . . . . . . . . D W W
 14  # # # . . . . . . . . . . . . c . . . . . . W W
 15  # # # . . . . . . . . . . . c T T c # # . . W W
 16  # # # . . . c . . . . . . . . T T . # # . . W W
 17  # # # . . c T T c . . . . . . . . . # # . . W W
 18  # # # . . . T T . . c . . . . . . . # # . . W W
 19  # # # . . . . . . c T T c . . c . . # # . . W W
 20  # # # . . . B . . . T T . . c T T c # # . . W W
 21  # # # . . . . B . . c . . . . T T . # # . . W W
 22  # # # . . . . X B . . . . . . c . . # # . . W W
 23  # # # . . . . . . . . . . . . . . . # # . . W W
 24  # # # # # # # # # # # # # # # # # # W W W W W W
```

### Solid objects (block the student; the tornado floats over them)

| Object | x | y | w | h | Sprite |
|---|---|---|---|---|---|
| Left bookshelf (A1–C24) | 0 | 0 | 3 | 24 | `shelf_east_*` on every tile |
| Top bookshelf (D1–R1) | 3 | 0 | 15 | 1 | `shelf_front_*` |
| Bottom bookshelf (D24–R24) | 3 | 23 | 15 | 1 | `shelf_north_*` |
| Inner bookshelf S1 (P2–Q8) | 15 | 1 | 2 | 7 | left column `shelf_west_*`, right column `shelf_east_*` |
| Inner bookshelf S2 (S15–T23) | 18 | 14 | 2 | 9 | left column `shelf_west_*`, right column `shelf_east_*` |
| Wall | 18 | 0 | 6 | 1 | `wall_placeholder` |
| Wall | 23 | 1 | 1 | 1 | `wall_placeholder` |
| Wall | 22 | 2 | 2 | 22 | `wall_placeholder` |
| Wall | 18 | 23 | 4 | 1 | `wall_placeholder` |
| Long table (J3–K8) | 9 | 2 | 2 | 6 | `table_long` |
| T1 (F11–G12) | 5 | 10 | 2 | 2 | `table_square` |
| T2 (L11–M12) | 11 | 10 | 2 | 2 | `table_square` |
| T3, small (S10) | 18 | 9 | 1 | 1 | `table_small` |
| T4 (G17–H18) | 6 | 16 | 2 | 2 | `table_square` |
| T5 (P15–Q16) | 15 | 14 | 2 | 2 | `table_square` |
| T6 (K19–L20) | 10 | 18 | 2 | 2 | `table_square` |
| T7 (P20–Q21) | 15 | 19 | 2 | 2 | `table_square` |
| Small desk D1 (T4–T7) | 19 | 3 | 1 | 4 | `desk_placeholder` on each tile |
| Reception desk D2, middle (U10–U12) | 20 | 9 | 1 | 3 | `desk_placeholder` |
| Reception desk D2, top end (V9) | 21 | 8 | 1 | 1 | `desk_placeholder` |
| Reception desk D2, bottom end (V13) | 21 | 12 | 1 | 1 | `desk_placeholder` |
| Whiteboard (G20, H21, I22) | tiles (6, 19), (7, 20), (8, 21) | | | | one `whiteboard` sprite (48 × 48) drawn at tile (6, 19) |

The whiteboard's collision is those **3 diagonal tiles** only. Bookshelf book colors (`red`, `blue`, `yellow`, `teal`): mix them along each shelf so no two neighbors match. Walls and desks are **placeholders for v1** (real sprites come in v2).

### Chairs (walk-over studying spots), 31 total, all 1 × 1 tile

"Side" = which side of its table the chair is on. Draw each chair with `chair_<color>_<side>`. The bonus is that chair's points per second for the first 2 seconds (§6).

| # | Table | (x, y) | Side | Color | Bonus |
|---|---|---|---|---|---|
| 1 | Long | (8, 2.5) | W | blue | +1 |
| 2 | Long | (8, 4.5) | W | white | +1 |
| 3 | Long | (8, 6.5) | W | green | +3 |
| 4 | Long | (11, 2.5) | E | red | +2 |
| 5 | Long | (11, 4.5) | E | blue | +1 |
| 6 | Long | (11, 6.5) | E | white | +1 |
| 7 | T1 | (5.5, 9) | N | green | +3 |
| 8 | T1 | (5.5, 12) | S | red | +2 |
| 9 | T1 | (4, 10.5) | W | blue | +1 |
| 10 | T1 | (7, 10.5) | E | white | +1 |
| 11 | T2 | (11.5, 9) | N | green | +3 |
| 12 | T2 | (11.5, 12) | S | red | +2 |
| 13 | T2 | (10, 10.5) | W | blue | +1 |
| 14 | T2 | (13, 10.5) | E | white | +1 |
| 15 | T3 | (18, 8) | N | green | +3 |
| 16 | T3 | (17, 9) | W | red | +2 |
| 17 | T3 | (19, 9) | E | blue | +1 |
| 18 | T4 | (6.5, 15) | N | white | +1 |
| 19 | T4 | (5, 16.5) | W | green | +3 |
| 20 | T4 | (8, 16.5) | E | red | +2 |
| 21 | T5 | (15.5, 13) | N | blue | +1 |
| 22 | T5 | (14, 14.5) | W | white | +1 |
| 23 | T5 | (17, 14.5) | E | green | +3 |
| 24 | T6 | (10.5, 17) | N | red | +2 |
| 25 | T6 | (10.5, 20) | S | blue | +1 |
| 26 | T6 | (9, 18.5) | W | white | +1 |
| 27 | T6 | (12, 18.5) | E | green | +3 |
| 28 | T7 | (15.5, 18) | N | red | +2 |
| 29 | T7 | (15.5, 21) | S | blue | +1 |
| 30 | T7 | (14, 19.5) | W | white | +1 |
| 31 | T7 | (17, 19.5) | E | green | +3 |

Every table has exactly one green chair. This layout is decided for v1 (it may be randomized later, but it must always be fair).

### Spawn points

- **Student start:** tile (21, 1) = **V2**, the entrance nook in the top-right corner, facing down
- **Tornado start:** tile (7, 21) = **H22**, at the bottom of the room (keep the whole cloud inside the room; the bigger clouds may need nudging up)
- **Extra clouds (Normal and Hard modes):** cloud 2 starts at tile (4, 2) = **E3** (top left); cloud 3 (Hard only) starts at tile (14, 21) = **O22** (bottom middle). All far from the student's start at V2

### Notes

- The narrow corridor between S2 and the right wall (U14–V23) is a **dead end, kept on purpose** as a danger zone
- The same room is used for all 3 stages

## 5. The student

- The player picks **boy** or **girl** on the character select screen. Both play exactly the same
- Moves with the **arrow keys**, including diagonals (two keys at once) at the same speed as straight movement
- Blocked by bookshelves, walls, tables, desks and the whiteboard; slides along them. Walks over chairs
- Sprites: `<boy|girl>_<down|up|left|right>_<stand|walk1|walk2>`. Alternate `walk1` / `walk2` while moving (about 8 changes per second); show `stand` when stopped, facing the last direction moved

## 6. Studying, the study meter and the chair bonus

- **Studying:** when the student's hitbox touches a chair (any overlap counts) and they are **not moving**, they sit down and study. If touching two chairs, use the one with the most overlap
- While studying, draw the seated sprite instead of the standing one: `<boy|girl>_seat_<side>_<read1|read2>`, looping `read1` → `read2` at about 2 per second, at the chair's position plus `offset_from_chair` from the JSON. For `S` chairs, draw the chair **after** the student (`draw_chair_on_top`)
- Pressing an arrow key stands the student up and walks away
- **Charging:** the meter fills in **points**; 1 point = 5% of the bar and the bar holds 20 points. Studying normally adds **1 point per second**, filling smoothly
- **Chair bonus:** for the **first 2 seconds** of studying at a chair, it adds that chair's bonus instead: **green 3, red 2, white 1, blue 1** points per second
- **The bonus only comes back at a different table:** remember the table where you last got a bonus. Sitting at any chair of that same table gives 1 per second from the start. Sitting at a different table gives the bonus again (and that table becomes the remembered one)
- **Pop-up:** each full second of studying, show `plus_1`, `plus_2` or `plus_3` above the student's head for the points that second added (timing in `effects_sheet.json` → `plus_popup`)
- **Study bar flash:** while studying, the filled part of the HUD bar cycles through the colors in `effects_sheet.json` → `study_bar_flash`
- The meter never goes below empty or above full, and it **resets to empty at the start of every stage**
- **No studying while flashing** after a hit, even if the knockback lands you on a chair

## 7. The Noise Tornado

- **How many:** depends on the mode chosen after Start: **Easy = 1 cloud** (the game as first built), **Normal = 2 clouds**, **Hard = 3 clouds**. In every mode, each stage's clouds all use that stage's size, speed, hitbox and notice time. Every cloud moves on its own (its own random targets) and pops its own noise bubbles. Clouds may overlap each other
- **Noticing with more than one cloud:** when the student has studied for the notice time, **every** cloud notices at once: each one lunges, bursts 3 bubbles and chases. When the student stops studying, they all go back to random mode
- **Getting hit by more than one cloud:** one hit at a time. The 1 second of invincibility protects from all clouds; knockback pushes away from the cloud that hit
- Sprite sheets: `noise_tornado_stage1/2/3.png` (6 frames each, loop at 10 frames per second). Size, speed and hitbox come from the stage (§3)
- **Floats over everything** (it never gets stuck), but stays inside the room
- **Random mode:** picks a random point inside the room, moves to it, then picks another
- **Noticing you (Stages 2 and 3 only):** if the student has been studying without a break for the stage's notice time (3 s / 1.5 s), the tornado notices: it **lunges** (0.5 s at lunge speed), pops **3 noise bubbles at once** (that burst is the warning), then **chases** the student at its normal speed
- **Back to random:** as soon as the student stops studying (stands up or walks off the chair), it returns to random mode and the notice timer resets
- **Stage 1:** random only, never notices you
- **Noise bubbles:** every 0.7 s, a random `bubble_*` sprite pops out of the top of the cloud, floats up 8 px over 0.6 s, blinks twice and disappears
- **No off-screen pointer:** when the tornado is off-screen, the player doesn't see where it is. That's on purpose (tension)

| Stage | Behavior | Notices you after studying for | Speed | Size | Pass mark |
|---|---|---|---|---|---|
| 1 | Random only | never | 36 px/s | 2 × 2 tiles | 50% |
| 2 | Random, lunges and chases once it notices | 3 s | 54 px/s | 3 × 3 tiles | 60% |
| 3 | Random, lunges and chases once it notices | 1.5 s | 72 px/s | 4 × 4 tiles | 70% |

Number of clouds by mode: **Easy 1, Normal 2, Hard 3**, in all three stages. Pass marks are the same in every mode.

## 8. Getting hit (NES Zelda style)

When the tornado's hitbox touches the student's hitbox and the student isn't invincible:

1. The meter loses **2 points (10%)**
2. The student is **knocked back 2 tiles** straight away from the tornado's center, over 0.2 s, and can't steer during the push. The push stops at anything solid; never push the student into or through a table, desk, shelf, wall or the whiteboard
3. For **1 second** the student is invincible, can't study, and **flashes**: every 3 frames, redraw the sprite with its 3 colors swapped, cycling normal → `flash_1` → `flash_2` (color swaps in `effects_sheet.json` → `hit_flash`; the blazer color is the character's own)
4. The round carries on. Getting hit never ends the game

## 9. Timer, the test and results

- Each round lasts **60 seconds**. The HUD timer turns **red** in the last 10 seconds
- At 0: **everything freezes** and a **"TIME'S UP!"** banner appears (about 1.5 s)
- **Results screen:** "THE TEST", your study bar (no numbers, **no pass line**, so the reveal stays tense), then "DID YOU PASS?" (about 1.5 s), then a big **PASSED!** (green) or **FAILED...** (red)
- **Passed Stage 1 or 2:** "ON TO STAGE N...", then that stage's intro. The meter starts empty
- **Passed Stage 3:** the **"YOU PASSED THE COURSE!!!"** screen, then Enter goes back to the title
- **Failed:** add 1 to that stage's fail count, show the stage code if it's earned (§10), then back to the title. The next game starts from Stage 1 unless a stage code is used

## 10. Stage codes

An old-school password system. Codes are fixed and the same for every player, so players can share them.

| Code | Starts the game at | Shown on the FAILED screen after |
|---|---|---|
| `MATHCLASS` | Stage 2 | failing Stage 2 five times |
| `COMPUTERSCIENCECLASS` | Stage 3 | failing Stage 3 five times |

- There's **no Stage 1 code**. Once earned, the code shows on every FAILED screen for that stage
- Fail counts reset when the game is closed (v1)
- **Stage Code screen:** type on the real keyboard (letters only), upper/lower case doesn't matter, Enter checks it, Backspace deletes, Esc goes back. A wrong code shows **"WRONG CODE!"** in red and lets you try again. A right code goes to mode select, then character select, then starts at that stage and continues to the end as normal. Codes and fail counts are shared by all modes

## 11. Screens and game flow

Mockups of every screen are in `docs/art/flow/` (18 screens in play order) and `docs/art/menus/`. Match them.

1. **Title:** "ELSC" logo, "GAME", the tagline "BEAT THE NOISE. PASS THE TEST.", a small scene of students studying with the tornado nearby, and three choices: **START**, **OPTIONS**, **STAGE CODE** (up/down to choose, Enter to select, yellow ">" cursor), plus "(C) 2026 ELSC" at the bottom
2. **Options:** MUSIC and SOUND FX volume bars (0–10, left/right to change), BACK. Sound comes later, so v1 just stores the two numbers
3. **Mode select** (after START): "CHOOSE YOUR MODE" with three boxes: **EASY** (green, "1 NOISE CLOUD"), **NORMAL** (yellow, "2 NOISE CLOUDS"), **HARD** (red, "3 NOISE CLOUDS"), each with that many little clouds. Up/down to choose, Enter to continue, Esc back to the title. The cursor starts on EASY. Mockup: `docs/art/modes/mode_select.png`
4. **Character select:** "CHOOSE YOUR STUDENT", boy and girl on sky-blue cards, left/right to choose, Enter to start
5. **Stage intro:** "EASY MODE" / "NORMAL MODE" / "HARD MODE" in its color, then "STAGE N", "READY, SET, STUDY!", "PASS MARK: ???" (about 2 seconds)
6. **Play** (60 s round)
7. **Time's up** → **Results** (§9)
8. Next stage, the course complete screen, or back to the title

**Flow in short:** Title → Start → Mode select → Character select → Stage 1 → Stage 2 → Stage 3. The chosen mode stays for the whole run (all 3 stages)

**Pause (Esc during play):** everything freezes (timer too) and a box shows **CONTINUE / RESTART / SOUND / QUIT TO TITLE**. Restart starts the **current stage** over (full timer, empty meter, everyone back at their start). Sound opens the same volume screen as Options.

## 12. HUD (always on screen during play)

The black 64 px strip above the play view:

- **Top left:** "STAGE N" followed by the mode in its color (EASY green, NORMAL yellow, HARD red), and below it the chosen character's standing sprite with their name (BOY / GIRL). Mockup: `docs/art/modes/stage2_play_hard.png`
- **Top middle:** "TIME" and the seconds left, big (the font at 3×), red in the last 10 s
- **Top right:** "STUDY" and a **fighting-game-style bar**: white frame, dark inside, yellow fill with small segment ticks. **No numbers**

## 13. Text

All text uses the NES font sprite sheet `font.png` (uppercase only, 6 px per letter, tinted to any color, scaled 2–4× for big titles). See `assets/sprites/README.md`.

## 14. Drawing order

Carpet → bookshelves, walls, desks → chairs → tables → whiteboard → student (a student seated on an `S` chair is drawn before that chair) → tornado → noise bubbles and "+" pop-ups → HUD → menus and banners.

## 15. Sound

All sound is **original NES-style chiptune** in `assets/sounds/` (see its README). There are only **10 files, reused all over the game**, NES-style. Music files (`.ogg`) play with `pygame.mixer.music` (one at a time, streamed); jingles and effects (`.wav`) play with `pygame.mixer.Sound`, so they can play on top of the music.

### Music (one at a time)

| File | Plays | How |
|---|---|---|
| `main_theme.ogg` | Title screen and every menu (Options, Stage Code, mode select, character select) | Loops. Keeps playing smoothly between menus. Fades out (~0.5 s) when a stage intro starts |
| `stage_music.ogg` | During play, all 3 stages | Starts when play begins (after the stage intro), loops |
| `stage_music_hurry.ogg` | During play, from **15 seconds left** | The same song, faster. Switch to it at 15 s left and loop it until time's up |
| `victory_song.ogg` | The "YOU PASSED THE COURSE!!!" screen | Loops until the player presses Enter |

- **Pause:** pause the music (`pygame.mixer.music.pause()`), and resume it on Continue. Restart starts the stage music over
- **Time's up:** stop the music the moment everything freezes

### Jingles and effects (on top of the music)

| File | Plays when |
|---|---|
| `sfx_cursor.wav` | A menu cursor moves; each letter typed in the stage code; Backspace; opening and closing the pause menu; Esc to go back; a **+1** pop-up |
| `sfx_select.wav` | Choosing something with Enter; **sitting down** on a chair; a **+2** or **+3** pop-up |
| `jingle_ready.wav` | The stage intro ("READY, SET, STUDY!"), and when the study bar reaches **full** |
| `jingle_drumroll.wav` | The results screen while "DID YOU PASS?" builds up; and **only its first 0.5 s** when the tornado **notices you** (lunge). If several clouds notice at once, play it once |
| `jingle_passed.wav` | The PASSED! reveal, and a **correct stage code** |
| `jingle_failed.wav` | The FAILED... reveal, and a **wrong stage code**; and **only its first 0.4 s** as the "bonk" when you **get hit** |

Playing only the start of a sound: `sound.play(maxtime=400)` (milliseconds).

- **Options:** MUSIC sets the volume of the 4 music files; SOUND FX sets the volume of the 6 `.wav` files (0–10, 0 = silent). Changes take effect right away
- If any sound file is missing, the game must still run, just without that sound
- **Not in v1:** tornado crowd noise, a ticking clock and a school bell were considered and left out to keep the game clean

## 16. Not planned yet (off limits)

Do **not** build these:

- **Ideas for later:** pathfinding (the tornado steering around furniture), more enemy types, extra obstacles and harder rooms, more characters to choose from, a retro on-screen keyboard for codes, camera zoom, an SNES-style art upgrade, real wall sprites, a pamphlet rack, a school bell, a glass door in the wall, saving fail counts between sessions, player accounts or logins
- **Later sound ideas:** tornado crowd noise that gets louder as it gets closer, a ticking clock, a school bell at time's up


## 17. Version 2

Everything in this section is new in version 2. Where it disagrees with §1–15, **this section wins**. The art is finished: `people_v2_sheet` and `objects_v2_sheet` in `assets/sprites/` (see the README's "Version 2 art"). Mockups of every new screen are in `docs/art/v2/` (`00_room_v2.png` is the whole room with everything in place). Every number below goes in `settings.py`.

### 17.1 Levels (the modes are now called Levels)

The mode select becomes **level select** ("CHOOSE YOUR LEVEL", mockup `v2/01_level_select.png`). EASY / NORMAL / HARD become **LEVEL 1 / LEVEL 2 / LEVEL 3** (green / yellow / red), each box showing its second line ("3 STAGES - 1 TO 3 CLOUDS", "5 STAGES - 1 TO 5 CLOUDS", "5 STAGES - GIANT CLOUDS"). The HUD shows **"LV1 / LV2 / LV3"** in the level's color, then "STAGE N" (mockups `v2/02`–`06`). The stage intro shows "LEVEL N" in its color instead of "EASY MODE".

| | Level 1 (Easy) | Level 2 (Normal) | Level 3 (Hard) |
|---|---|---|---|
| Stages | 3 | 5 | 5 |
| Round length | 30 s, 30 s, 40 s | 45 s every stage | 60 s every stage |
| Clouds (by stage) | 1, 2, 3 | 1, 2, 3, 4, 5 | 1, 2, 3, 4, 5 |
| Cloud size (by stage) | small, medium, big (as v1) | small, small, medium, medium, big | big in every stage |
| Cloud speed | 36 / 54 / 72 px/s by stage (as v1) | 54 px/s | 72 px/s |
| Notices you after studying for | never (wander only) | 3 s | 1.5 s |
| After you stop studying | — | back to random right away (as v1) | **keeps chasing for 3 more seconds**, then back to random |
| Pass marks (by stage) | 50%, 60%, 70% | 50%, 55%, 60%, 65%, 70% | 55%, 60%, 65%, 70%, 75% |
| A hit takes | 15 points | 20 points | 20 points |
| Invincible after a hit | 1 s | 1 s | 1.5 s |
| Score multiplier | ×1 | ×2 | ×3 |

- **Sizes:** small = `noise_tornado_stage1` (32 px, hitbox 20), medium = `stage2` (48 px, hitbox 30), big = `stage3` (64 px, hitbox 40)
- **Cloud start tiles** (cloud 1 to 5): H22 (7, 21), E3 (4, 2), O22 (14, 21), M3 (12, 2), E15 (4, 14). The start tile is the cloud's **center**; then clamp the cloud inside the room (big clouds would otherwise stick out). They float over everything, so starting over furniture is fine
- **Hurry-up music** starts at **10 s left in Level 1** (short rounds) and **15 s left in Levels 2 and 3**. The timer still turns red at 10 s
- Everything else about clouds is as §7 (all clouds notice at once, one hit at a time, knockback 2 tiles). How long you're invincible after a hit is in the table above
- The "keeps chasing" time in Level 3 resets if you sit down again

### 17.2 The bigger study bar (all levels)

- The bar holds **150 points** (it was 20). It looks exactly the same on screen; it just fills slower
- Studying gives **5 points per second**. Chair bonus for the first 2 s at a new table: **green 15, red 10, white 5, blue 5** points per second (same table rule as §6)
- Pop-ups keep the same art: `plus_1` for a normal second, `plus_2` for a red-chair second, `plus_3` for a green-chair (or highlighter) second. Pick the pop-up from the rate **before** the coffee boost (coffee doesn't change which pop-up shows)
- Keep bar points as decimals (coffee gives 7.5 per second); scores round down
- A hit takes the level's damage (table above). The meter never goes below 0 or above 150
- Pass marks are a percentage of 150

### 17.3 The room: new objects

Coordinates are tiles (x, y), as in §4. Mockup: `v2/00_room_v2.png`.

| Object | Where | Sprite(s) | Solid for the student? |
|---|---|---|---|
| **Coffee station** | (4, 1), 2 × 2 tiles (E2–F3) | `coffee_station` | yes |
| **Haruna's desk** (replaces D1) | x 19, y 3–6 (T4–T7) | top to bottom: `haruna_desk_top`, `haruna_desk_monitor`, `haruna_desk_papers`, `haruna_desk_bottom` | yes |
| **Haruna's chair + Haruna** | (18, 4) (S5) | `office_chair`, Haruna drawn on it 4 px higher | yes (she's a person) |
| **Hitomi's U-shaped desk** (replaces D2) | V9 (21, 8), U10 (20, 9), U11 (20, 10), U12 (20, 11), V13 (21, 12) | `hitomi_desk_top_end`, `hitomi_desk_upper`, `hitomi_desk_monitor`, `hitomi_desk_lower`, `hitomi_desk_gate_closed` / `_open` | yes, **always**, including the gate (only Hitomi walks through it) |
| **Inside Hitomi's desk** | V10–V12 (21, 9–11) | carpet, `office_chair` at (21, 10), Hitomi on it 4 px higher | yes (the student can never go in) |

- Draw carpet under the curved desk pieces (they have see-through corners)
- The old `desk_placeholder` tiles are gone. Walls stay as they are

### 17.4 Haruna (receptionist, sits at her desk)

- Always sits at (18, 4) facing her desk: loop `haruna_type1` / `haruna_type2` (2 per second)
- **Calls out every 15 s:** `haruna_call1` / `haruna_call2` (4 per second) for 2 s, with a speech bubble **"BE QUIET PLEASE, / PEOPLE ARE STUDYING!"** (2 lines) for 2.5 s (mockup `v2/02_haruna_calls.png`). She calls out in every level. It's just for fun and tension; it changes nothing
- **Drops the headphones** (all levels): when **half the round's time is gone**, if the bar is **under 50%**, she plays `haruna_toss` (0.4 s) and `item_headphones` appears on the floor at (17, 6). Once per stage at most. They stay until picked up or the stage ends

### 17.5 Hitomi (teacher, walks out and gets in the way)

- At her desk: sits at (21, 10) facing left, looping `hitomi_desk_work1` / `work2` (2 per second)
- **She comes out** when the bar first reaches **50%** and again when it first reaches **70%** in each stage. In Level 3 also at **30%**. Each trigger happens once per stage. If she's already out when a trigger happens, that trigger is skipped
- **Walking out:** the gate opens (`hitomi_desk_gate_open`) and **stays open while she's out** (it's still solid for the student). She walks from (21, 10) down through (21, 12) to (21, 13) and says **"DID YOU STUDY?!"** (speech bubble, 2 s) while playing `hitomi_point1` / `point2` (4 per second) for 1 s. Then she moves (below). When her time is up she walks back to (21, 13), walks in to her chair, and the gate closes. If the student is standing on (21, 13) when she wants to pass, she waits
- **Walking:** `hitomi_<dir>_<frame>` like the students. She walks on the floor, straight toward her target (no pathfinding): she's blocked by furniture like the student and slides along things. **If she's stuck for 1 s**, she walks to a random floor spot for 2 s, then goes back to her normal target. She walks over chairs
- **She's solid** for the student (hitbox 12 × 12). **She can never touch a seated student**: she treats a seated student as a wall and walks around
- **More annoying each level:**

| Level | How she moves | Speed | Out for | When she bumps a standing student |
|---|---|---|---|---|
| 1 | Wanders to random floor spots | 40 px/s | 6 s | Just blocks (she stops) |
| 2 | Walks toward the student | 60 px/s | 8 s | Pushes the student back 1 tile, away from her center (0.15 s, no damage, no flashing; stops at anything solid like the §8 knockback) |
| 3 | Goes to the **free chair closest to the student** and **stands on it** for 2 s (nobody can sit there while she's on it), then picks the next one | 75 px/s | 10 s | Pushes the student back 1 tile |

- She **never takes points**. Clouds float over her (they don't interact)
- Mockup: `v2/03_hitomi_out.png`

### 17.6 Power-ups (Zelda style)

Items sit on the floor, a table or a shelf. **Grabbing** a floor item = the student's hitbox touches the item's 12 × 12 center box. **Grabbing** a table item = the student's hitbox, grown by 2 px, touches that table (so walking up to it or sitting at it both work). Items bob up and down 1 px (about 2 per second) so they read as power-ups. Only one of each per stage, and they all reset at the start of every stage (and on Restart).

| Power-up | Levels | Where it waits (from the start of each stage) | What it does |
|---|---|---|---|
| **Coffee** `item_coffee` | 1, 2, 3 | Floor in front of the coffee station, drawn at pixel (72, 48) | **10 s**: walk **1.5× faster** and study **1.5× faster** (all study points, bonus included) |
| **Headphones** `item_headphones` | 1, 2, 3 | Dropped by Haruna at (17, 6), only if you're struggling (§17.4) | **8 s**, like Mario's star: the student **blinks** (cycle the hit-flash colors every 3 frames, every 2 frames in the last 2 s), clouds **pass right through** (no hits) and **can't notice you**. Studying works as normal |
| **Laptop** `item_laptop` | 2, 3 | On table T4 (6, 16), drawn at pixel (104, 264) | **+10 seconds.** Everything freezes, a box pops up "DEADLINE EXTENDED!" / "+10 SEC", and the HUD timer (in yellow) **ticks up one second at a time** (every 0.1 s) until +10, holds 0.5 s, then play goes on. Mockup `v2/04_deadline_extended.png` |
| **Highlighter** `item_highlighter` | 2, 3 | On table T7 (15, 19), drawn at pixel (248, 312) | **8 s**: **every chair gives 15 points per second** the whole time you sit (not just the first 2 s), every chair is drawn as `chair_green_<side>`, and the book blinks green (§17.7). Mockup `v2/05_highlighter.png` |
| **Pizza** `item_pizza_box` → `item_pizza_open` | 3 | On top of bookshelf S2, drawn at pixel (296, 221) | **Bump the shelf** (the student's own arrow-key movement is blocked by bookshelf S2, x 18–19, y 14–22, from any side; being knocked or pushed into it doesn't count): the box drops off behind the shelf (0.4 s arc) and lands **open** on the floor at pixel (328, 272), in the corridor between the shelf and the wall. For **8 s every cloud goes to the pizza** and wanders within 1.5 tiles of it, ignoring the student (no noticing, no chasing). After 8 s it **vanishes** in a burst of 3 noise bubbles and the clouds go back to normal. Mockup `v2/06_pizza_lure.png` |

- The coffee and the highlighter can run at the same time (they multiply: 15 × 1.5)
- Laptop: the music follows the time left (back to the normal stage music if the time goes above the hurry-up time)
- Level 1 has no laptop, highlighter or pizza (don't draw them)

### 17.7 The book

Whenever the student is seated, draw `book_<side>` over them at the seated sprite's position plus `offset_from_seated` (all 4 sides, all levels). While the highlighter is active, the book blinks between `book_<side>` and `book_<side>_green` (4 per second).

### 17.8 Speech bubbles

- **In the room:** a white box with a 1 px black border, black text (the font), 4 px padding, and `bubble_tail` under it pointing at the speaker's head. Keep the whole bubble on screen (slide it sideways if needed, the tail stays over the speaker). No names
- **On the results screen:** see 17.9

### 17.9 The test (results) with Haruna and Hitomi

Replaces the §9 results screen. Mockups `v2/07_results_passed.png` and `v2/08_results_failed.png`.

1. "THE TEST" and the study bar (as before, no numbers, no pass line)
2. **Haruna** (`portrait_haruna_talk` at 2×, left) asks **"DID YOU PASS?"** in a speech bubble while the drumroll plays (~1.5 s), alternating `portrait_haruna_smile` / `talk` (4 per second)
3. **Hitomi** (right, 2×) answers in a Zelda-style dialogue box at the bottom (black, white border) with her small portrait inside. The text types out letter by letter (about 30 letters per second):
   - Passed: `portrait_hitomi_cheer1` / `cheer2`, **"YOU PASSED!"** (green, 2×), "ON TO STAGE N..." (on the last stage: "COURSE COMPLETE!", then YOU PASSED THE COURSE!!!) and "SCORE +N" (yellow)
   - Failed: `portrait_hitomi_sorry1` / `sorry2`, **"YOU FAILED..."** (red, 2×), "SEE YOUR SCORE" (the mockup says "BACK TO THE TITLE"; this text wins), and the stage code if it's earned (yellow)
- **Portraits sit on a card:** a 2 px white frame filled with sky blue `3CBCFC`, so Haruna's black hair shows

### 17.10 Score and high scores

- **Stage score** = (bar points at the test × 10 + 1,000 if passed) × the level multiplier. It shows on the PASSED box as "SCORE +N"
- **Run score** = all stage scores added up
- **After every run** (after the last FAILED, or after "YOU PASSED THE COURSE!!!"): "LEVEL N COMPLETE!" (only if you finished it), **"YOU SCORED"** and the number (4×, yellow). Mockup `v2/09_score_entry.png`
- **If it's in that level's top 10:** "NEW HIGH SCORE!" and **type your name**: up to **10 letters**, letters, numbers and spaces, typed on the real keyboard like a stage code (Backspace deletes, Enter saves). An empty name saves as "PLAYER". Otherwise Enter goes back to the title
- **HIGH SCORES** is a new title menu item (START / HIGH SCORES / OPTIONS / STAGE CODE): the top 10 of one level, with **"< LEVEL N >"** and Left / Right to switch levels, Esc back. Mockup `v2/10_high_scores.png`
- Saved in **`highscores.json`** next to `main.py` (created when first needed), so they stay after closing the game. If the file is missing or broken, start with empty lists
- Write numbers without commas (the font has no thousands comma)

### 17.11 Stage codes (now per level)

| Code | Level | Starts at |
|---|---|---|
| `MATHCLASS` | 1 | Stage 2 |
| `COMPUTERSCIENCECLASS` | 1 | Stage 3 |
| `GRAMMAR` | 2 | Stage 3 |
| `VOCABULARY` | 2 | Stage 5 |
| `PRESENTATION` | 3 | Stage 3 |
| `FINALEXAM` | 3 | Stage 5 |

- Each code shows on the FAILED screen after failing **its stage** of **its level** 5 times (as §10)

- A code **picks its level**, so a right code skips level select and goes straight to character select. Runs started with a code still count for high scores
- Fail counts are per level and stage (while the game runs)

### 17.12 Game flow (v2)

Title → START → **level select** → character select → stages of that level → (last stage passed) YOU PASSED THE COURSE!!! → **score** → title. A FAILED stage → **score** → title. Title → HIGH SCORES → title.

### 17.13 Drawing order (v2)

Carpet → bookshelves, walls, desks, coffee station → chairs and office chairs → tables → items on tables and the shelf → whiteboard → items on the floor → Haruna and seated Hitomi → the student (a student on an `S` chair before that chair) and the book → walking Hitomi → clouds → noise bubbles, "+" pop-ups and speech bubbles → HUD → boxes, menus and banners.

### 17.14 Sound (no new files, NES-style reuse)

| Moment | Sound |
|---|---|
| A power-up appears (headphones dropped) | `sfx_select.wav` |
| Grabbing any power-up | the first **0.6 s** of `jingle_passed.wav` |
| DEADLINE EXTENDED: each +1 second tick | `sfx_cursor.wav` |
| Bumping the pizza shelf | the first **0.4 s** of `jingle_failed.wav` (the bonk) |
| Pizza eaten (vanishes) | `sfx_cursor.wav` |
| Hitomi's gate opens (she comes out) / closes (she's back in) | `sfx_select.wav` / `sfx_cursor.wav` |
| A speech bubble appears | `sfx_cursor.wav` |
| Results dialogue box typing | `sfx_cursor.wav` every 2 letters |
| Hitomi pushes you | the first **0.2 s** of `jingle_failed.wav` |
| Typing your name | as the stage code (cursor blip per letter, select on Enter) |
| Score screen | `jingle_ready.wav` when the score appears; `jingle_passed.wav` on NEW HIGH SCORE! |

### 17.15 New settings (all in `settings.py`, with plain-English comments)

Everything in the tables above, plus: bar size 150; study 5 points per second; chair bonus 15 / 10 / 5 / 5; Haruna call every 15 s (bubble 2.5 s); headphones check at half time, under 50%, lasting 8 s; coffee 10 s at 1.5×; laptop +10 s (tick every 0.1 s); highlighter 8 s; pizza lure 8 s within 1.5 tiles; Hitomi triggers 50% / 70% (and 30% in Level 3), her speeds, times out and 1-tile push; Level 3 extra chase 3 s; item bob 1 px; score ×10 per point, +1,000 per pass, multipliers ×1 / ×2 / ×3; top 10 per level; name up to 10 letters.

## 18. The web version (play on the website, shared high scores, play counting)

The game runs **in the player's web browser** (built with **pygbag**, which turns a pygame game into a web page), and the high scores are **shared by everyone** through a small score server (a Google Sheet + Google Apps Script, see `server/SETUP_SCORES.md`). The desktop game (`python main.py`) must keep working exactly as before.

**Two editions, always available:** the same game is built twice. **`site`** goes on Mike's website; **`friends`** is a separate link Mike gives to friends. Each edition has **its own top 10**, and every play is tagged with its edition, so Mike can see where people played. The only difference between them is the `EDITION` setting.

### 18.1 Running in a browser
- The main loop becomes **async** (pygbag's rule): `async def main()` with `await asyncio.sleep(0)` once per frame, started with `asyncio.run(main())`. The same code runs on desktop
- **CLICK TO PLAY:** in the browser only (`sys.platform == "emscripten"`), the first screen is black with the ELSC logo and a blinking **"CLICK TO PLAY"**. Browsers block sound and the keyboard until the page is clicked; after the click, go to the title screen as normal
- **Sounds use `.ogg`:** every sound now has an `.ogg` version in `assets/sounds/` (the 6 jingles and effects were converted; same names, same lengths). Load `.ogg` everywhere (desktop too), and use the `.wav` only if the `.ogg` is missing
- **"Only the first N seconds" of a sound** (§15, §17.14): don't rely on `play(maxtime=...)`, which may not work in the browser. Play it, then stop that channel after N seconds with a timer
- **Screen size:** scale the 256 × 240 game with nearest-neighbor to fit the browser page while staying crisp (a whole-number scale if one fits, otherwise the biggest scale that fits)
- **Esc** still pauses. If the browser also leaves fullscreen on Esc, that's fine
- **Keyboard only**, as before (no phones or tablets for now)
- The browser has nowhere to keep files between visits, so the local `highscores.json` is only used on desktop, or when the score server can't be reached

### 18.2 The score server (shared high scores and play counting)
- New setting **`SCORE_SERVER_URL`** in `settings.py`. Empty `""` = offline: the game works exactly as now with the local `highscores.json`
- New setting **`EDITION`** in `settings.py`: `"site"` (default) or `"friends"`. Sent with every request below as `"edition"` (a GET adds `&edition=site`)
- The server's API is already written (`server/apps_script/Code.gs`):

| Request | Sends | Gets back |
|---|---|---|
| `GET URL?action=top&level=N&edition=E` | — | `{"ok":true,"level":N,"top":[{"name":"MIKE","score":12340}, ...]}` (up to 10, best first) |
| `GET URL?action=stats&edition=E` | — | `{"ok":true,"plays":123,"plays_today":7,"best":{...}}` |
| `POST URL`, JSON body sent as **plain text** (no custom headers, so the browser allows it) | `{"action":"start","session":S,"level":N,"character":"boy"}` | `{"ok":true}` |
| `POST URL` | `{"action":"finish","session":S,"level":N,"character":"girl","stage":3,"score":4520,"completed":false}` | `{"ok":true}` |
| `POST URL` | `{"action":"score","session":S,"level":N,"score":12340,"name":"MIKE"}` | `{"ok":true,"name":"MIKE","rank":1,"top":[...]}` or `{"ok":false,"error":"..."}` |

- **Session:** a random 16-character id (letters and numbers) made when a **run** starts, new for every run (each run can save one score). The server refuses a score sent less than 25 s after its `start`
- **Never freeze the game waiting for the internet.** Every request runs in the background (browser: JavaScript `fetch` through pygbag's JavaScript bridge; desktop: `urllib` in a background thread) with a **15 s timeout** (`ONLINE_TIMEOUT_SECONDS`). The game checks for answers each frame.
- **Wake the server up early:** Google puts the score server to sleep when nobody uses it, and waking it can take 10+ s. So when the game opens it sends one small request in the background (the answer isn't used); by the time a run ends the server is awake
- When requests go out: `start` when a run begins (right after character select, or after a stage code); `finish` when the run ends (the last FAILED, or after YOU PASSED THE COURSE!!!); then `score` if the player saves a name. `stage` = the last stage they played; `score` = the run score; `completed` = passed the level's last stage

### 18.3 High score screens with the server
- **HIGH SCORES (title menu):** shows **"LOADING..."** while it asks for that level's top 10, then the list. Left / Right loads another level. If the server can't be reached: **"OFFLINE"** in red under the title and the local list
- **After a run:** while "YOU SCORED" shows, ask the server for that level's top 10. If the score makes the top 10 (beats the 10th score, or the list has fewer than 10), show NEW HIGH SCORE! and the name entry (§17.10). If the server can't be reached, use the local list. NEW HIGH SCORE! (or PRESS ENTER) appears only once the answer is in: when the server answers, or after the 15 s timeout (then with the local list)
- **Saving:** after Enter, show **"SAVING..."**, then **"SAVED!"** (green) and the top 10 with the new score in yellow, or **"COULD NOT SAVE"** (red) if it failed (on desktop it's then saved locally). Enter goes back to the title
- The server cleans names (uppercase letters, numbers and spaces, up to 10) and replaces rude names with PLAYER. Show the name the server sends back

### 18.4 Building for the web
- `tools/make_web_copy.py --edition site` (or `--edition friends`) copies **only what the game needs** (the game's `.py` files and `assets/`) into `build_web/site/elsc-game/` (or `build_web/friends/elsc-game/`) and sets `EDITION` in that copy's `settings.py`. Players don't download the docs, art tools and pictures
- `tools/build_web.py` makes both editions in one go: the two copies, then a pygbag build of each (steps in `docs/PUBLISH_ON_WEBSITE.md`). The result is two folders of web files to upload. Target: under 15 MB each
- The leaderboard page for the website (`web/leaderboard.html`) and the embed code (`web/embed_snippet.html`) are already made

## 19. Phones and tablets (touch, no on-screen controls)

The **same web version** (both editions) also plays on phones and tablets. **No buttons or D-pad are drawn.** The game notices a touch screen by itself and switches to touch controls; on a computer nothing changes. The desktop game (`python main.py`) is not affected. Mockups: `docs/art/mobile/` (`phone_mockups_all.png`).

### 19.1 Touch mode or keyboard mode (automatic)
- **At start-up** (browser only): ask the page whether the main pointer is a finger, with `matchMedia("(pointer: coarse)").matches` or `navigator.maxTouchPoints > 0` through pygbag's JavaScript bridge. If yes, start in **touch mode**; otherwise **keyboard mode**
- **The first tap or click decides:** a touch on the TAP / CLICK TO PLAY screen = touch mode; a mouse click or key = keyboard mode
- **It switches live:** any key press switches to keyboard mode; any touch switches to touch mode (a tablet with a keyboard, or a touchscreen laptop, just works). Only the hints and the name entry change between modes; everything else accepts both at all times
- The start screen says **"TAP TO PLAY"** in touch mode and **"CLICK TO PLAY"** in keyboard mode

### 19.2 The phone page
- Portrait first. The 256 × 240 game is scaled with nearest-neighbor to the **full width** of the screen (any scale, not only whole numbers), placed near the top. The black space below it is part of the touch area. Landscape also works: scale to fit the height, centered
- **The game's picture fills the whole phone screen** (decided Oct 3): on a touch screen the picture we draw is 256 game pixels wide (portrait) and as tall as the phone's shape needs, with the 256 × 240 game near the top and black below. So the thumb guide (19.3) shows anywhere, also below the game. On computers it stays 256 × 240
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
- In touch mode, the hints change: stage intro **"SLIDE ANYWHERE TO MOVE / LIFT TO STOP AND SIT"** (on the stage intro only, not under the game while playing; decided Oct 3), and "TAP" instead of "ENTER" / "PRESS ENTER" in menu hints

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

### 19.8 The ELSC Study Pocket (the phone shell)

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

**Loading:** `tools/build_web.py` adds a full-screen black layer to the built `index.html` showing `handheld_loading.png` (copied next to it), sized to the phone's width and centered, on top of pygbag's own loading bar. The game removes that layer (through pygbag's JavaScript bridge) on its first frame. **Phones only** (changed Oct 6): computers keep pygbag's normal loading screen, no handheld picture. pygbag's message box stays on top of the layer and taps go through it, because pygbag may ask "Ready to start! Please click/touch page" before the game starts.

**Hints in the shell:** the stage intro's touch hint becomes **"SLIDE ON THE PAD / LIFT TO SIT"**, and menu hints say **"SLIDE + OK"**.

**Settings:** `HANDHELD_SHELL = True` (turn the shell off), and the menu repeat times (0.4 s / 0.15 s).
