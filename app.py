"""Symptom Triage Helper: a rule-based expert system.

It gives general triage guidance only (how urgently to seek care). It never
names a diagnosis and is not a substitute for a clinician or emergency services.

Architecture
------------
* Knowledge base ... QUESTIONS (what can be asked) and RULES (IF conditions THEN urgency).
* Working memory .. `facts`, the user's answers so far (a dict).
* Inference engine  forward chaining: every rule whose conditions all hold fires.
                    Conflict resolution: the highest urgency among fired rules wins.
* Question control  asks the next applicable unanswered question, and stops early
                    as soon as an emergency rule fires.
* Explanation ..... "why am I asked this?" (which rules use the answer) and
                    "how was this concluded?" (the rules that fired, in IF-THEN form).
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

from triage import *  # noqa: F401,F403  (re-exported so `import app` keeps working)
from triage import handle_triage

ROOT = Path(__file__).parent


PUBLIC_FILES = {"/", "/index.html", "/robots.txt", "/sw.js", "/manifest.webmanifest"}


class JsonApiMixin:
    """JSON request/response helpers shared by the local server and the Vercel function."""

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0 or length > 20000:
                raise ValueError
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            return None

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


class AppHandler(JsonApiMixin, SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".webmanifest": "application/manifest+json",
        ".js": "text/javascript",
        ".svg": "image/svg+xml",
        ".woff2": "font/woff2",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _is_public(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        return path in PUBLIC_FILES or (path.startswith("/static/") and ".." not in path)

    def do_GET(self):
        # Only serve the site itself, never source files or the .git folder.
        if not self._is_public():
            self.send_error(404)
            return
        super().do_GET()

    def do_HEAD(self):
        if not self._is_public():
            self.send_error(404)
            return
        super().do_HEAD()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def do_POST(self):
        if self.path != "/triage":
            self.send_error(404)
            return
        data = self._read_json()
        if data is None:
            self.send_error(400, "Please send valid JSON")
            return
        status, payload = handle_triage(data)
        if status != 200:
            self.send_error(status, payload)
            return
        self._send_json(payload)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), AppHandler)
    print("Symptom Triage Helper is running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
