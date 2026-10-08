# Update 03 — Version 2 (Sept 28, 2026)

Version 2 adds Levels 1–3 (with more stages), a bigger study bar, Haruna and Hitomi, the coffee station, five power-ups, a new test screen, and high scores. The rules are in `docs/GAME_SPEC.md` **§17** (it wins over §1–15 where they disagree). The new art is in `assets/sprites/people_v2_sheet` and `objects_v2_sheet` (read the "Version 2 art" part of `assets/sprites/README.md`). Pictures of every new screen are in `docs/art/v2/`.

No new sound files: version 2 reuses the 10 sounds we have (§17.14).

**Claude Code:**
1. Add Steps 15–26 below to the end of `docs/BUILD_PLAN.md`, before the "Later" section. Keep all the existing ticks.
2. Make sure Steps 0–14 are done. If one isn't, tell me which before starting.
3. Do **Step 15 only**, then stop and tell me how to test it. I'll ask for the next step each time.
4. Keep every existing feature working. All new numbers go in `settings.py` with plain-English comments.

---

## Step 15 — Levels and the bigger study bar
- [ ] Mode select becomes **level select** ("CHOOSE YOUR LEVEL", LEVEL 1 / 2 / 3), matching `docs/art/v2/01_level_select.png`
- [ ] Each level has its own stages, round lengths, clouds per stage, cloud sizes, speed, notice time, pass marks, hit damage (§17.1)
- [ ] Level 3: clouds keep chasing for 3 s after you stop studying
- [ ] Cloud start tiles are the cloud's center, clamped inside the room; hurry-up music at 10 s left in Level 1, 15 s in Levels 2–3
- [ ] Extra cloud start tiles M3 and E15 for clouds 4 and 5
- [ ] The bar holds 150 points; studying 5 per second; chair bonus 15 / 10 / 5 / 5 (§17.2)
- [ ] HUD shows "LV1 / LV2 / LV3" in the level's color, then "STAGE N"; the stage intro shows "LEVEL N"
- [ ] Finishing the last stage of a level (3 or 5) shows YOU PASSED THE COURSE!!!
- [ ] Debug keys 1–5 jump to that stage of the current level (still behind the debug setting); keys above the level's stage count do nothing

**Test:** play Level 1 (30 s rounds, clouds only wander, 3 stages). Choose Level 2 and press 3 (debug keys): 3 medium clouds and a 45 s round. Play Level 3: every cloud is big, and they keep chasing for a moment after you stand up.

## Step 16 — The new room: desks, coffee station, Haruna and Hitomi sitting
- [ ] Remove the desk placeholders; draw Haruna's desk, Hitomi's U-shaped desk (gate closed), both office chairs and the coffee station (§17.3), with carpet under the curved pieces
- [ ] Haruna sits and types at (18, 4); Hitomi sits and works at (21, 10)
- [ ] New solid areas: the coffee station, both desks, Haruna, and the inside of Hitomi's desk
- [ ] Compare with `docs/art/v2/00_room_v2.png`

**Test:** walk around the whole room. You can't walk into the coffee station, either desk, Haruna, or inside Hitomi's desk. Nothing else changed.

## Step 17 — The book
- [ ] When the student sits, draw `book_<side>` over them (all 4 sides) using `offset_from_seated` (§17.7)

**Test:** sit on chairs on all four sides of a table; the book sits in the student's hands (or on the table for `S` chairs).

## Step 18 — Speech bubbles and Haruna calling out
- [ ] A speech bubble helper: white box, 1 px black border, black text, `bubble_tail`, kept on screen (§17.8)
- [ ] Haruna calls out every 15 s: hands-up frames for 2 s and the bubble "BE QUIET PLEASE, / PEOPLE ARE STUDYING!" for 2.5 s (§17.4). Blip when a bubble appears

**Test:** stand near Haruna for 30 s: she calls out twice. The bubble never goes off screen. Compare with `docs/art/v2/02_haruna_calls.png`.

## Step 19 — Power-ups part 1: coffee and the headphones
- [ ] Item helper: items bob 1 px, one of each per stage, reset every stage and on Restart; grab rules for floor and table items (§17.6)
- [ ] **Coffee** in front of the coffee station: 10 s at 1.5× walking and studying
- [ ] **Headphones:** at half time, if the bar is under 50%, Haruna tosses them to (17, 6); grabbing them gives 8 s of Mario-star blinking, clouds pass through you and can't notice you
- [ ] Sounds from §17.14

**Test:** grab the coffee: you're faster and the bar fills faster for 10 s. Study very little until half time: Haruna drops the headphones. Grab them and walk through a cloud: nothing happens. Study a lot before half time: no headphones.

## Step 20 — Hitomi walks out
- [ ] Triggers at 50% and 70% (and 30% in Level 3), each once per stage (§17.5)
- [ ] The gate opens (and stays open while she's out), she walks out, "DID YOU STUDY?!" with the pointing frames, then she moves by level (Level 1 wanders, Level 2 comes at you, Level 3 stands on the free chair closest to you), then walks back in
- [ ] She's solid, never touches a seated student, never takes points; pushes a standing student 1 tile in Levels 2–3
- [ ] Sounds from §17.14

**Test:** in each level, study up to 50%: Hitomi comes out. Level 1: she just wanders. Level 2: she follows you and pushes you. Level 3: she steals the chair next to you. She can't reach you while you're seated. Compare with `docs/art/v2/03_hitomi_out.png`.

## Step 21 — Power-ups part 2: the laptop (Levels 2 and 3)
- [ ] Laptop on table T4. Walk up to the table: freeze, "DEADLINE EXTENDED!" box, the timer ticks up +10 (yellow, a blip each second), hold 0.5 s, carry on (§17.6)
- [ ] The music follows the time left (back to normal stage music if above the hurry-up time)

**Test:** in Level 2 with about 12 s left, grab the laptop: the timer goes up to about 22 and the hurry-up music changes back. Compare with `docs/art/v2/04_deadline_extended.png`. Level 1 has no laptop.

## Step 22 — Power-ups part 3: the highlighter (Levels 2 and 3)
- [ ] Highlighter on table T7: 8 s where every chair gives 15 per second, every chair is drawn green, and the book blinks green

**Test:** grab it, sit on a blue chair: +3 every second. All chairs look green until it ends. Compare with `docs/art/v2/05_highlighter.png`.

## Step 23 — Power-ups part 4: the pizza (Level 3)
- [ ] Pizza box on top of bookshelf S2. Bumping the shelf drops it behind the shelf (0.4 s arc), open, at pixel (328, 272)
- [ ] For 8 s every cloud goes to the pizza and wanders around it, ignoring you; then it vanishes in 3 noise bubbles and the clouds go back to normal

**Test:** in Level 3, walk into the right bookshelf: the pizza falls, all the giant clouds rush to it, and you can study in peace for 8 s. Compare with `docs/art/v2/06_pizza_lure.png`.

## Step 24 — The new test screen with Haruna and Hitomi
- [ ] Portraits on light-blue cards, Haruna asks "DID YOU PASS?" during the drumroll, Hitomi answers in a typed dialogue box, cheering or shaking her head (§17.9)

**Test:** pass a stage and fail one. Compare with `docs/art/v2/07_results_passed.png` and `08_results_failed.png`.

## Step 25 — Score, names and high scores
- [ ] Stage and run scores with the level multiplier; "SCORE +N" on the PASSED box (§17.10)
- [ ] After every run: YOU SCORED; name entry (up to 10 letters) if it makes that level's top 10
- [ ] HIGH SCORES on the title menu, Left / Right between levels; saved to `highscores.json`
- [ ] Stage codes per level (§17.11); a code skips level select

**Test:** finish a run, type a name, check HIGH SCORES. Close the game and open it again: the score is still there. Try `GRAMMAR` and `FINALEXAM`. Compare with `docs/art/v2/09_score_entry.png` and `10_high_scores.png`.

## Step 26 — Sound check and playtest
- [ ] Every sound in §17.14 plays at the right moment
- [ ] Play all three levels start to finish, as the boy and the girl. No crashes
- [ ] Tune `settings.py` until Level 1 feels easy, Level 2 fair, and Level 3 like real panic but passable

**Version 2 is done** when you can play all three levels from the title screen to the high score list with no crashes. 🎉
