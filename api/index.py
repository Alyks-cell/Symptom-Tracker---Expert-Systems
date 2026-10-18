from http.server import BaseHTTPRequestHandler
from pathlib import Path
import json
import sys

# Add root directory to sys.path to import the expert system from app.py
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app import JsonApiMixin, handle_triage  # noqa: E402


class handler(JsonApiMixin, BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?")[0] not in ("/triage", "/api/triage"):
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

    def do_GET(self):
        # Health check
        self._send_json({"status": "ok", "app": "Symptom Triage Helper"})
