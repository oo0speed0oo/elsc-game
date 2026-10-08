# ELSC Game — talking to the online score server (GAME_SPEC §18.2).
# Every request runs in the background, so the game never freezes waiting
# for the internet:
#   - in a web browser: JavaScript's fetch(), started through pygbag's bridge
#     to the page (platform.window)
#   - on the desktop: urllib in a background thread
# The game asks each request "are you done yet?" once per frame.
# A request that takes longer than ONLINE_TIMEOUT_SECONDS counts as failed.
# With SCORE_SERVER_URL = "" nothing is ever sent (the game works offline).

import itertools
import json
import random
import string
import sys
import threading
import time
import urllib.parse
import urllib.request

import settings

WEB = sys.platform == "emscripten"

# The little bit of JavaScript the browser runs for us. POST bodies are sent as
# plain text with no custom headers, so the browser doesn't need to ask the
# server for permission first (the Google script couldn't answer that).
JAVASCRIPT = """
window.elscNet = {
    results: {},
    send: function (id, method, url, body, timeoutMs) {
        const stop = new AbortController();
        const timer = setTimeout(() => stop.abort(), timeoutMs);
        const options = {method: method, signal: stop.signal};
        if (method === "POST") options.body = body;
        fetch(url, options)
            .then(answer => answer.text())
            .then(text => { window.elscNet.results[id] = JSON.stringify({ok: true, text: text}); })
            .catch(() => { window.elscNet.results[id] = JSON.stringify({ok: false, text: ""}); })
            .finally(() => clearTimeout(timer));
    },
    take: function (id) {
        const result = window.elscNet.results[id];
        if (result === undefined) return "";
        delete window.elscNet.results[id];
        return result;
    }
};
"""


def new_session():
    """A random 16-character id (letters and numbers) for one run."""
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


class Request:
    """One question to the server. Check .done; then .ok and .data (the answer)."""

    def __init__(self, number):
        self.number = number
        self.started = time.time()
        self.done = False
        self.ok = False
        self.data = None            # the server's answer as a dictionary

    def finish(self, ok, text):
        if self.done:
            return                  # already timed out: a late answer is ignored
        data = None
        if ok:
            try:
                data = json.loads(text)
            except ValueError:
                ok = False          # not JSON (an error page?): count it as failed
        if ok and not (isinstance(data, dict) and data.get("ok")):
            ok = False              # the server answered, but said no
        self.ok, self.data, self.done = ok, data, True


class Online:
    def __init__(self):
        self.url = settings.SCORE_SERVER_URL.strip()
        self.enabled = bool(self.url)
        self.numbers = itertools.count(1)
        self.waiting = []           # requests that aren't done yet
        if self.enabled and WEB:
            import platform         # pygbag's: it reaches the web page
            platform.window.eval(JAVASCRIPT)

    # -----------------------------------------------------------------------
    # Asking
    # -----------------------------------------------------------------------
    def top(self, level):
        """Ask for a level's top 10 (for this edition)."""
        query = urllib.parse.urlencode({"action": "top", "level": level, "edition": settings.EDITION})
        return self.send("GET", self.url + "?" + query)

    def wake_up(self):
        """A tiny question with no real use, sent when the game opens: Google puts
        the score server to sleep when nobody uses it, and waking it can take
        10+ seconds. By the time the player finishes a run, it's awake."""
        return self.send("GET", self.url)

    def post(self, body):
        """Send something to the server (start / finish / score). The edition is added."""
        body = dict(body, edition=settings.EDITION)
        return self.send("POST", self.url, json.dumps(body))

    def send(self, method, url, body=""):
        request = Request(next(self.numbers))
        if not self.enabled:
            request.finish(False, "")          # offline: fails at once, nothing is sent
            return request
        self.waiting.append(request)
        if WEB:
            import platform
            platform.window.elscNet.send(str(request.number), method, url, body,
                                         int(settings.ONLINE_TIMEOUT_SECONDS * 1000))
        else:
            threading.Thread(target=self.desktop_send, args=(request, method, url, body),
                             daemon=True).start()
        return request

    @staticmethod
    def desktop_send(request, method, url, body):
        """Runs in a background thread on the desktop."""
        try:
            data = body.encode("utf-8") if method == "POST" else None
            message = urllib.request.Request(url, data=data, method=method,
                                             headers={"Content-Type": "text/plain;charset=utf-8"})
            with urllib.request.urlopen(message, timeout=settings.ONLINE_TIMEOUT_SECONDS) as answer:
                request.finish(True, answer.read().decode("utf-8", "replace"))
        except Exception:
            request.finish(False, "")          # no internet, timeout, server error...

    # -----------------------------------------------------------------------
    # Every frame
    # -----------------------------------------------------------------------
    def update(self):
        """Collect browser answers, and give up on requests that took too long."""
        still_waiting = []
        for request in self.waiting:
            if WEB and not request.done:
                import platform
                result = str(platform.window.elscNet.take(str(request.number)) or "")
                if result:
                    answer = json.loads(result)
                    request.finish(answer["ok"], answer["text"])
            if not request.done and time.time() - request.started > settings.ONLINE_TIMEOUT_SECONDS:
                request.finish(False, "")      # too slow: counts as failed
            if not request.done:
                still_waiting.append(request)
        self.waiting = still_waiting
