# Putting ELSC Game online (two editions)

You get **two copies of the same game**, and both are always available:

| Edition | Where it lives | Who plays it | Its high scores |
|---|---|---|---|
| **site** | On your website | Anyone visiting your site | The website's top 10 |
| **friends** | A separate link | People you send the link to | The friends' top 10 |

Both send their plays and scores to **the same Google Sheet** (`server/SETUP_SCORES.md`), tagged "site" or "friends", so the Summary tab shows where people played.

The game runs **in each player's browser**, so your website only sends the files once per player (a few MB, like a page with photos). 20 players at once is no problem; even hundreds would be fine.

---

## 1. Build both editions (on your computer, after Claude Code's Step 30)

In a terminal, in your game folder:

```
pip install pygbag
python tools/build_web.py
```

You get two folders ready to upload:

```
build_web/site/elsc-game/build/web/       <- the website edition
build_web/friends/elsc-game/build/web/    <- the friends edition
```

Each one holds an `index.html` and the game files. **Upload the whole `web` folder's contents**, not just `index.html`.

**Try one on your computer first:** `python -m pygbag build_web/site/elsc-game`, then open **http://localhost:8000** in Chrome.

(The page loads pygbag's small Python engine from the internet when it opens, so players need to be online. That's normal.)

---

## 2. The website edition

**A. Your website can hold files** (WordPress, normal web hosting such as Xserver, Sakura or Lolipop, or anything with FTP or a "File Manager"):
1. In your host's File Manager (or an FTP app like FileZilla), make a folder called **`elsc-game`** in your website's main folder (often `public_html`).
2. Upload everything inside `build_web/site/elsc-game/build/web/` into it.
3. The game is now at **`https://YOUR-SITE/elsc-game/`**.
4. To show it inside a page, paste the code from `web/embed_snippet.html` into that page (WordPress: a **Custom HTML** block). Change the address in it to yours.

**B. Your website is Wix, Squarespace, Jimdo, STUDIO or similar** (they can't hold game files):
1. Go to **app.netlify.com/drop** (free; make an account so the site stays).
2. Drag the folder `build_web/site/elsc-game/build/web` onto the page. You get an address like `https://something.netlify.app`. You can rename it to something like `elsc-game.netlify.app` in the site settings.
3. In your website builder, add an **Embed / HTML / iframe** element and paste the code from `web/embed_snippet.html`, with your Netlify address in it.

---

## 3. The friends edition (a link to give out)

Pick one:

- **Netlify (simplest):** drag `build_web/friends/elsc-game/build/web` onto **app.netlify.com/drop** as a **second** site, and name it something like `elsc-game-friends.netlify.app`. Send that link to friends.
- **itch.io (looks like a real game page):** make a free account, then **Upload new project**:
  - Kind of project: **HTML**
  - Zip the *contents* of `build_web/friends/elsc-game/build/web` and upload the zip
  - Tick **"This file will be played in the browser"**
  - Viewport: **768 × 720**, and turn on the fullscreen button
  - Under visibility, choose **Restricted** with a password, or **Draft** while testing, if you don't want it public yet. Send friends the link (and password)
- **Your own hosting:** the same as 2A, in a second folder called `elsc-game-friends`.

---

## 4. The leaderboard page (optional, for your website)

`web/leaderboard.html` is a ready-made NES-style high score page. It shows the top 10 for each level and how many games have been played.
1. Open it in a text editor, and paste your score server URL where it says `PASTE_YOUR_SCORE_SERVER_URL_HERE`.
2. Website with files: upload it next to the game, for example `https://YOUR-SITE/elsc-game-scores.html`. Wix and similar: paste the whole file into an **Embed HTML** element.
3. It shows the **site** edition's scores. To show the friends' list, add `?edition=friends` to its address.

Opened before the URL is pasted, it shows made-up demo scores so you can see how it looks.

---

## 5. Updating the game later

Rebuild (`python tools/build_web.py`) and upload the new files over the old ones, in both places. High scores and play counts aren't touched; they live in the Google Sheet.

If players still see the old version, they can refresh with **Ctrl + Shift + R** (Mac: **Cmd + Shift + R**).
