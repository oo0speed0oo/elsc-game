# Update 04 — The web version (Oct 1, 2026)

The game goes on the website and gets a friends link: **two editions** ("site" and "friends") of the same game. They run in the browser, share high scores online, and count plays. The rules are in `docs/GAME_SPEC.md` **§18**.

Already made and in this pack (don't rewrite them):
- `server/apps_script/Code.gs`: the score server (a Google Sheet + Apps Script). Mike sets it up with `server/SETUP_SCORES.md`
- `web/leaderboard.html`: a high score page for the website. `web/embed_snippet.html`: the code that puts the game in a web page
- `docs/PUBLISH_ON_WEBSITE.md`: how Mike uploads both editions
- `.ogg` versions of the 6 jingles and effects in `assets/sounds/`

**Claude Code:**
1. Update the docs (keep everything already there, including any tuning changes made during playtesting):
   - Append the contents of `docs/GAME_SPEC_18_web.md` (from "## 18." down) to the end of `docs/GAME_SPEC.md`. In its first line, add "§18 (the web version) adds online play and shared high scores". In §16, remove "uploading high scores to a website" and "playing in a web browser", and add "touch controls for phones and tablets, player accounts or logins"
   - In `CLAUDE.md`, say that version 2 is built and we're now making the web version (§18; §17 and §18 win over §1–15), that after Step 27 the game must also run in the browser, and add `server/` and `web/` to the project layout (both are not part of the game)
   - Add Steps 27–30 below to the end of `docs/BUILD_PLAN.md`, before the "Later" section. Keep all the existing ticks
2. Do **Step 27 only**, then stop and tell me how to test it. I'll ask for the next step each time.
3. The desktop game (`python main.py`) must keep working after every step.
4. pygbag changes over time: check its current documentation (pygame-web on GitHub) for the exact commands and the JavaScript bridge before relying on memory.

---

## Step 27 — Ready for the browser
- [ ] The main loop is async (`async def main()`, `await asyncio.sleep(0)` every frame, `asyncio.run(main())`), and the desktop game still runs exactly as before (§18.1)
- [ ] All sounds load from `.ogg` (falling back to `.wav` if an `.ogg` is missing)
- [ ] "Play only the first N seconds" uses a timer that stops the channel, not `maxtime`
- [ ] In the browser only: the CLICK TO PLAY screen first; the game scales to fit the page and stays crisp
- [ ] `tools/make_web_copy.py --edition site|friends`: copies only the game's `.py` files and `assets/` into `build_web/<edition>/elsc-game/` and sets `EDITION` in that copy's `settings.py` (§18.4)
- [ ] `EDITION = "site"` and `SCORE_SERVER_URL = ""` added to `settings.py` (not used yet)

**Test:** `python main.py` still plays normally. Then `pip install pygbag`, `python tools/make_web_copy.py --edition site`, `python -m pygbag build_web/site/elsc-game`, and open http://localhost:8000 in Chrome: CLICK TO PLAY, then the title with music, and a full run with sound, the bonk, the drumroll start and the pass jingle.

## Step 28 — Online high scores
- [ ] `online.py`: background requests to `SCORE_SERVER_URL` (browser: JavaScript `fetch` via pygbag's bridge; desktop: `urllib` in a thread), 8 s timeout, never freezing the game; POST bodies are JSON as plain text, and every request includes the edition (§18.2)
- [ ] HIGH SCORES screen: LOADING..., the online top 10 for this edition, Left / Right between levels, OFFLINE plus the local list if it fails (§18.3)
- [ ] After a run: the qualify check against the online list, name entry, SAVING... then SAVED! (with the list, new score in yellow) or COULD NOT SAVE; show the name the server returns
- [ ] `SCORE_SERVER_URL = ""` still works fully offline, as before

**Test:** set up the Google Sheet (`server/SETUP_SCORES.md`) and paste the URL in `settings.py`. On desktop: finish a run, save a name, and see it in the Sheet's **Scores** tab and on the HIGH SCORES screen. Turn off the Wi-Fi: HIGH SCORES shows OFFLINE and the game doesn't freeze. Try a rude name: it saves as PLAYER.

## Step 29 — Counting plays
- [ ] A new random session id for every run; `start` after character select (or after a stage code), `finish` when the run ends, each with level, character and edition (§18.2)
- [ ] Fire and forget: the game never waits for these

**Test:** play two short runs and check the Sheet: the **Plays** tab has a start and a finish row for each run (edition "site"), and **Summary** counts them.

## Step 30 — Build both editions
- [ ] `tools/build_web.py`: runs `make_web_copy.py` for **site** and **friends**, then builds each with pygbag, ending with two upload-ready folders (`build_web/site/elsc-game/build/web/` and `build_web/friends/elsc-game/build/web/`), and prints their sizes
- [ ] Both are under 15 MB, and both work in Chrome, Safari and Edge (CLICK TO PLAY, sound, keyboard, scores)
- [ ] A friends-edition score shows in the friends top 10, not the site's, and the Sheet's Summary shows "Games from the friends link"
- [ ] `build_web/` is ignored by git (if the project uses git)

**Test:** `python tools/build_web.py`, then test each folder locally with pygbag. Then follow `docs/PUBLISH_ON_WEBSITE.md` to upload both, and play each from its real link on a second computer.

**The web version is done** when the site edition plays on your website, the friends link works, and both show up in the Google Sheet. 🎉
