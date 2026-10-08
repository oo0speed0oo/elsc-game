# GAME_SPEC §18 (to add to GAME_SPEC.md)

Claude Code: append everything below this line to the end of `docs/GAME_SPEC.md` (see `UPDATE_04_web.md`).

---

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
- **Never freeze the game waiting for the internet.** Every request runs in the background (browser: JavaScript `fetch` through pygbag's JavaScript bridge; desktop: `urllib` in a background thread) with an **8 s timeout**. The game checks for answers each frame
- When requests go out: `start` when a run begins (right after character select, or after a stage code); `finish` when the run ends (the last FAILED, or after YOU PASSED THE COURSE!!!); then `score` if the player saves a name. `stage` = the last stage they played; `score` = the run score; `completed` = passed the level's last stage

### 18.3 High score screens with the server
- **HIGH SCORES (title menu):** shows **"LOADING..."** while it asks for that level's top 10, then the list. Left / Right loads another level. If the server can't be reached: **"OFFLINE"** in red under the title and the local list
- **After a run:** while "YOU SCORED" shows, ask the server for that level's top 10. If the score makes the top 10 (beats the 10th score, or the list has fewer than 10), show NEW HIGH SCORE! and the name entry (§17.10). If the server can't be reached, use the local list
- **Saving:** after Enter, show **"SAVING..."**, then **"SAVED!"** (green) and the top 10 with the new score in yellow, or **"COULD NOT SAVE"** (red) if it failed (on desktop it's then saved locally). Enter goes back to the title
- The server cleans names (uppercase letters, numbers and spaces, up to 10) and replaces rude names with PLAYER. Show the name the server sends back

### 18.4 Building for the web
- `tools/make_web_copy.py --edition site` (or `--edition friends`) copies **only what the game needs** (the game's `.py` files and `assets/`) into `build_web/site/elsc-game/` (or `build_web/friends/elsc-game/`) and sets `EDITION` in that copy's `settings.py`. Players don't download the docs, art tools and pictures
- `tools/build_web.py` makes both editions in one go: the two copies, then a pygbag build of each (steps in `docs/PUBLISH_ON_WEBSITE.md`). The result is two folders of web files to upload. Target: under 15 MB each
- The leaderboard page for the website (`web/leaderboard.html`) and the embed code (`web/embed_snippet.html`) are already made
