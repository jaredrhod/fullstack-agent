#!/usr/bin/env python3
# fullstack-kimi barehands: hand-controlled spatial board.
# Copyright (C) 2026 Jared Rhodenizer
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
A tiny server for the barehands hand-tracking board.

Open Chrome to the printed URL. The page uses your webcam and MediaPipe
Hands to track your hand, detect gestures, and write state files that the
agent can read. No controllers, no headset.
"""

import http.server
import json
import os
import socketserver
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DEFAULT_PORT = 8794
DEFAULT_STATE_DIR = HERE.parent / "kimi-voice"


def load_config():
    cfg_path = HERE / "kimi-barehands.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def get_state_dir():
    cfg = load_config()
    d = cfg.get("state_dir")
    if d:
        return Path(d).expanduser()
    return DEFAULT_STATE_DIR


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            index = HERE / "static" / "index.html"
            self.serve_file(index, "text/html")
            return

        if path == "/config":
            self.serve_json(load_config())
            return

        self.directory = str(HERE / "static")
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/state":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
            except Exception:
                data = {}
            state_dir = get_state_dir()
            state_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / ".kimi_hands").write_text(json.dumps(data), encoding="utf-8")
            self.serve_json({"ok": True})
            return
        self.send_error(404)

    def serve_file(self, path, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(path.read_bytes())

    def serve_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    cfg = load_config()
    port = cfg.get("port", DEFAULT_PORT)
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"fullstack-kimi barehands running at http://127.0.0.1:{port}/")
        print(f"state directory: {get_state_dir()}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
