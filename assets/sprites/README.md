# ELSC Game — Sprites

NES-style pixel art drawn from photos of the real ELSC office.

## Rules every sprite follows

- **Tile size:** 16 × 16 pixels (one game tile). Scale up with nearest-neighbor (no smoothing) when drawing on screen
- **Strict NES colors:** only colors from the NES palette, and **at most 3 colors per sprite** plus transparent
- **Transparent background** (PNG with alpha)
- **Light from the top-left**, Zelda-style slightly tilted top-down view

## furniture_sheet.png (approved, draft 3)

A 128 × 128 sprite sheet. `furniture_sheet.json` lists every sprite's name and its `x, y, w, h` in pixels on the sheet.

| Sprite names | Size (tiles) | Notes |
|---|---|---|
| `carpet_a`, `carpet_b` | 1 × 1 | Floor. Checkerboard them: `carpet_a` where (x + y) is even, `carpet_b` where it's odd |
| `table_square` | 2 × 2 | T1, T2, T4–T7 |
| `table_long` | 2 × 6 | Long table |
| `table_small` | 1 × 1 | T3 |
| `chair_<color>_<side>` | 1 × 1 | color: `blue`, `white`, `green`, `red`. side = which side of the table the chair is on: `N` (above), `S` (below), `W` (left), `E` (right). The backrest always faces away from the table |
| `shelf_front_<book>` | 1 × 1 | Bookshelf facing down (top wall). book: `red`, `blue`, `yellow`, `teal` |
| `shelf_north_<book>` | 1 × 1 | Facing up (bottom wall) |
| `shelf_east_<book>` | 1 × 1 | Facing right (left wall, right side of inner shelves S1/S2) |
| `shelf_west_<book>` | 1 × 1 | Facing left (left side of inner shelves S1/S2) |
| `shelf_top` | 1 × 1 | Plain top board (spare, not used in the current map) |
| `whiteboard` | 3 × 3 | Diagonal whiteboard. Draw it with its top-left corner at tile G20 |
| `wall_placeholder` | 1 × 1 | **Placeholder**, waiting for a photo |
| `desk_placeholder` | 1 × 1 | **Placeholder**, waiting for a photo |

## noise_tornado_stage1/2/3.png (approved)

The enemy: a cartoon **fight cloud**. A bouncing ball of dust with angry and yelling faces, fists, feet, books and papers flying out, and black impact marks around it. **It gets bigger every stage**, drawn natively at each size (same pixel size as everything else), with more faces, fists and books as it grows.

| File | Stage | Size | Suggested hitbox (centered) |
|---|---|---|---|
| `noise_tornado_stage1.png` | 1 | 32 × 32 px (2 × 2 tiles) | 20 × 20 px |
| `noise_tornado_stage2.png` | 2 | 48 × 48 px (3 × 3 tiles) | 30 × 30 px |
| `noise_tornado_stage3.png` | 3 | 64 × 64 px (4 × 4 tiles) | 40 × 40 px |

- Each file is 6 frames in a row; its `.json` lists each frame's `x, y, w, h`. Play frames 0 → 5 in a loop at about **10 frames per second**
- The hitbox is smaller than the drawing so near misses feel fair
- Knockback stays **2 tiles** at every size (it does not grow with the cloud)
- NES layering: the dust cloud is one 3-color layer (white, gray, black) and the debris is a second 3-color layer (skin, red, blue) stacked on top. They're already combined in the PNG

## students_sheet.png (approved)

The two playable students, **16 × 16 px** (Link-size). 3 colors each, and never red or blue (those belong to the tornado): black (hair, jeans, shoes, eyes), skin (face, hands, T-shirt) and a blazer color.

- **Boy:** green-teal blazer, short spiky black hair, black backpack
- **Girl:** lilac-pink blazer, long black ponytail with a pink ribbon
- Names: `<boy|girl>_<down|up|left|right>_<stand|walk1|walk2>`. Walk by alternating `walk1` and `walk2`; show `stand` when not moving

## students_seated_sheet.png (approved)

The studying pose, used while the student is touching a chair: sitting, reading an open book.

- Names: `<boy|girl>_seat_<N|S|W|E>_<read1|read2>`, where the side is the side of the table the chair is on. Loop `read1` → `read2` at about 2 fps (a small head nod)
- Each entry in the JSON has `offset_from_chair` (pixels to add to the chair's position) and `draw_chair_on_top` (true for `S`: draw the chair AFTER the student so its backrest hides the student's back)

## effects_sheet.png (approved)

Small effect sprites. `effects_sheet.json` has their positions **and the timing rules** for everything below, so the code doesn't have to guess.

- **Noise bubbles** (`bubble_huh`, `bubble_bang`, `bubble_curse`, `bubble_music`, `bubble_dots`, `bubble_ha`, `bubble_lol`, `bubble_blah`): pop out of the top of the Noise Tornado every ~0.7 s, float up 8 px, blink, and vanish. When it notices you and lunges, 3 pop out at once
- **Chair bonus pop-ups** (`plus_1`, `plus_2`, `plus_3`): RPG-style "+1 / +2 / +3" over the student's head, once per second while studying, showing what that second added. Colored like the chairs: white +1, red +2, green +3
- **Hit flash** and **study bar flash**: done in CODE, not sprites. The color swaps are listed in the JSON (`hit_flash`, `study_bar_flash`)

## font.png (approved)

The game's NES-style font: the same letters used in every menu mockup. 61 characters (A–Z, 0–9 and punctuation), uppercase only.

- White letters on transparent, in 8 × 8 cells, 16 per row. `font.json` gives each character's `x, y`
- Each letter is 5 × 7 px. Draw each character **6 px** after the last one
- **Tint** the white to any NES color in code (menus use white, yellow, gold, gray, red, green, sky blue)
- **Big titles:** scale by 2, 3 or 4 with nearest-neighbor (no smoothing), like the mockups

## The chair bonus rule

Charging is counted in points: **1 point = 5% of the study bar**. Normally a chair gives **+1 per second**. For the **first 2 seconds** after sitting down, a chair gives its bonus instead: **green +3, red +2, white +1, blue +1**. The bonus only comes back when you sit at a **different table** than the one you last got a bonus from. Hopping to another chair at the same table gives +1 only. (Also in `effects_sheet.json` under `chair_bonus`.)

## Color order

Chair colors cycle in this order around the room: blue, white, green, red (same order as the chairs are listed in `docs/GAME_SPEC.md`). Mix the book colors along each shelf so no two neighbors match.

## Drawing order

Carpet first, then shelves, walls and desks, then chairs, then tables, then the whiteboard, then characters and the tornado.

## Remaking the art

The sprites are drawn by code in `art_tools/make_sprites.py`. Run it from inside `art_tools/` to regenerate the sheet and the preview images:

```
pip install pillow numpy
python make_sprites.py
python make_noise_tornado.py
python make_students.py
python make_seated.py
python make_menus.py
python make_effects.py
python make_font.py
python make_inventory.py
```

Run them in that order (later scripts use earlier sheets). `make_menus.py` draws the menu and UI screen mockups into a `menus/` folder.

`make_sprites.py` writes `elsc_furniture_sheet.png` and `.json` next to the script. Copy them here as `furniture_sheet.png` / `furniture_sheet.json`. It also checks the NES rule and stops with an error if any sprite breaks it. `make_noise_tornado.py` (run it second) writes `noise_tornado_stage1.png`, `stage2` and `stage3` with their `.json` files, plus previews. `make_inventory.py` draws `art_inventory.png`: every sprite on one labeled sheet, plus the list of what's still missing. `concepts_funnel_tornado.py` is the earlier funnel-shaped concept, kept for reference only.

## Previews

See `docs/art/`: the approved tile map, the whole room drawn with the sprites, one screen at monitor size, the chairs close up, the sheet at 5× zoom, the Noise Tornado animation (`noise_tornado_preview.gif`), all three tornado sizes on the map (`noise_tornado_sizes_preview.gif`), and the full inventory (`art_inventory.png`). Earlier concepts are in `docs/art/concepts/`.

## Version 2 art (Sept 28, 2026)

Two new sheets. Every sprite is already stacked from up to 3 NES layers (each layer has at most 3 NES colors), so the game draws each one as a single image. Pictures of every new screen are in `docs/art/v2/`.

**`people_v2_sheet.png` / `.json`: Haruna (receptionist) and Hitomi (walking teacher)**
- `hitomi_<down|up|left|right>_<stand|walk1|walk2>`: walking, 16 × 16, like the students
- `hitomi_point1/2`: the "DID YOU STUDY?!" pose (finger wag)
- `hitomi_desk_work1/2`: sitting at her desk facing left, drawn over `office_chair`
- `haruna_type1/2`: at her desk facing right; `haruna_call1/2`: hands up, calling out; `haruna_toss`: dropping the headphones
- `portrait_*` (32 × 32): results and score screens. Draw them on a light-blue card (a white frame filled with `3CBCFC`) so Haruna's black hair shows on the black screen

**`objects_v2_sheet.png` / `.json`: desks, chair, coffee station, power-ups, book**
- Haruna's desk (T4–T7, top to bottom): `haruna_desk_top`, `haruna_desk_monitor`, `haruna_desk_papers`, `haruna_desk_bottom`. `office_chair` at S5, Haruna on it (4 px higher)
- Hitomi's U-shaped desk: `hitomi_desk_top_end` (V9), `hitomi_desk_upper` (U10), `hitomi_desk_monitor` (U11), `hitomi_desk_lower` (U12), `hitomi_desk_gate_closed` / `hitomi_desk_gate_open` (V13). `office_chair` at V11, Hitomi on it (4 px higher). Draw carpet under the curved pieces (they have transparent corners)
- `coffee_station` (32 × 32, 2 × 2 tiles at E2–F3, solid)
- Power-ups: `item_coffee`, `item_headphones`, `item_laptop` (on its table), `item_highlighter` (on its table), `item_pizza_box` (on the shelf, and falling), `item_pizza_open` (on the floor)
- `book_<N|S|W|E>` and `book_<side>_green` (highlighter): drawn over the seated student at the seated sprite's position plus `offset_from_seated`
- `bubble_tail`: the little tail under a speech bubble (the bubble box itself is drawn in code: white fill, 1 px black border, black text)
