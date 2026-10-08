# ELSC Game — the high score lists (GAME_SPEC §17.10).
# One top-10 list per level, saved in highscores.json next to main.py so the
# scores are still there after the game is closed. If the file is missing or
# broken, every list simply starts empty.

import json
import os

import settings

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")


def load():
    """Read the lists: {level: [{"name": ..., "score": ...}, ...]}, best first."""
    lists = {level: [] for level in settings.LEVELS}
    try:
        with open(HIGHSCORE_FILE) as f:
            saved = json.load(f)
        for level in lists:
            entries = saved.get(str(level), [])
            lists[level] = [{"name": str(e["name"]), "score": int(e["score"])} for e in entries]
            lists[level].sort(key=lambda e: e["score"], reverse=True)
            del lists[level][settings.HIGH_SCORES_KEPT:]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        lists = {level: [] for level in settings.LEVELS}    # missing or broken: start fresh
    return lists


def save(lists):
    """Write the lists to highscores.json (created the first time it's needed)."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({str(level): entries for level, entries in lists.items()}, f, indent=2)
    except OSError:
        pass                                                # can't save (read-only folder?): keep playing


def makes_the_list(lists, level, score):
    """Would this score get into the level's top 10 (on this computer)?"""
    return qualifies(lists[level], score)


def qualifies(entries, score):
    """Would this score get into a top 10 (best first)? Yes if the list has fewer
    than 10 scores, or the score beats the 10th one."""
    return len(entries) < settings.HIGH_SCORES_KEPT or score > entries[-1]["score"]


def add(lists, level, name, score):
    """Put a new score in its place (best first) and keep only the top 10."""
    entries = lists[level]
    entries.append({"name": name, "score": score})
    entries.sort(key=lambda e: e["score"], reverse=True)
    del entries[settings.HIGH_SCORES_KEPT:]
