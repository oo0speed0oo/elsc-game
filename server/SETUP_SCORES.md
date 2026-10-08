# Set up the online high scores (Google Sheet) — about 10 minutes

The shared high scores and the play counter live in a **Google Sheet** that only you can open. A small Google script (`server/apps_script/Code.gs`) sits in front of it and talks to the game. It's free, and there's no server to look after.

You need a Google account. Do this once, on any computer.

## 1. Make the Sheet
1. Go to **sheets.google.com** and make a **Blank spreadsheet**.
2. Click "Untitled spreadsheet" at the top left and name it **ELSC Game Scores**.

## 2. Add the script
1. In the Sheet's menu: **Extensions → Apps Script**. A new tab opens with a file called `Code.gs`.
2. Click "Untitled project" at the top and name it **ELSC Score Server**.
3. Select everything in `Code.gs` and delete it.
4. Open `server/apps_script/Code.gs` from the game folder (any text editor), copy **all** of it, and paste it in.
5. Click the **Save** icon (the floppy disk).

## 3. Run the setup once
1. At the top of the editor there's a dropdown next to "Run" / "Debug". Choose **setup**.
2. Click **Run**.
3. Google asks for permission (it's your own script, so this is normal):
   - **Review permissions** → choose your account
   - "Google hasn't verified this app" → **Advanced** → **Go to ELSC Score Server (unsafe)** → **Allow**
4. Go back to the Sheet tab. You now have three tabs at the bottom: **Plays**, **Scores** and **Summary**.

## 4. Put it online
1. In the script tab: **Deploy → New deployment**.
2. Click the gear next to "Select type" → **Web app**.
3. Description: `ELSC scores`
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Click **Deploy**, then copy the **Web app URL**. It ends in `/exec`. Keep it safe; this is your **score server URL**.

## 5. Check that it works
Paste your URL into a browser with `?action=stats` at the end, like this:

```
https://script.google.com/macros/s/XXXXXXXX/exec?action=stats
```

You should see something like `{"ok":true,"plays":0,"plays_today":0,"best":{"1":null,"2":null,"3":null}}`. That means it works.

## 6. Give the URL to the game and the leaderboard page
- In the game's `settings.py`: `SCORE_SERVER_URL = "your URL"` (Claude Code adds this setting in Step 28)
- In `web/leaderboard.html`: paste it where it says `PASTE_YOUR_SCORE_SERVER_URL_HERE`

## Seeing who plays
Open the Sheet any time:
- **Summary:** games started (all time, today, last 7 days), each level, boy or girl, how many finished each level, and the best scores
- **Plays:** one row per game start and finish, with the time, level, character, how far they got and their score
- **Scores:** every high score saved (time, level, name, score)

To clear out your own test games, just delete those rows.

## If you change the script later
**Deploy → Manage deployments → the pencil icon → Version: New version → Deploy.** The URL stays the same.

## Good to know
- The Sheet itself stays private. Only the script's web address is public, and it can only add plays and scores and read the top 10.
- **Light cheat protection:** scores above the game's maximum are refused; a score has to come at least 25 seconds after its game started; and each game can save only one score.
- Rude names are saved as **PLAYER**. You can add more words to `BAD_PARTS` in the script.
- Google's free limits are far beyond what a class or an office will use.
