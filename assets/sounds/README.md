# ELSC Game — Sounds

Original NES-style sound, made the way the NES does it: two square-wave channels, a triangle bass and a noise drum. Everything is drawn by `art_tools/make_sounds.py`. **10 files, reused all over the game.** The full rules for when each one plays are in `docs/GAME_SPEC.md` §15.

## Music (`pygame.mixer.music`, one at a time, loops)

| File | Length | Plays |
|---|---|---|
| `main_theme.ogg` | 27 s, 144 BPM | Title screen and all menus |
| `stage_music.ogg` | 26 s, 150 BPM | During play, all 3 stages |
| `stage_music_hurry.ogg` | 19 s, 200 BPM | During play, from 15 seconds left (the same song, faster) |
| `victory_song.ogg` | 13 s | "YOU PASSED THE COURSE!!!" |

## Jingles and effects (`pygame.mixer.Sound`, on top of the music)

| File | Length | Plays |
|---|---|---|
| `sfx_cursor.wav` | 0.06 s | Menu cursor, typing a code, Backspace, pause open/close, Esc/back, +1 pop-up |
| `sfx_select.wav` | 0.17 s | Choosing with Enter, sitting down, +2 / +3 pop-ups |
| `jingle_ready.wav` | 2.4 s | Stage intro "READY, SET, STUDY!", and the study bar reaching full |
| `jingle_drumroll.wav` | 2.1 s | "DID YOU PASS?"; its first 0.5 s when the tornado notices you |
| `jingle_passed.wav` | 2.3 s | PASSED!, and a correct stage code |
| `jingle_failed.wav` | 3.0 s | FAILED..., and a wrong stage code; its first 0.4 s when you get hit |

Play just the start of a sound with `sound.play(maxtime=400)` (milliseconds).

Volumes come from the Options screen (MUSIC for the `.ogg` music, SOUND FX for the `.wav` effects, 0–10). If a file is missing, the game runs without it.
