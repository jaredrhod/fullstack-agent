#!/usr/bin/env python3
# fullstack-kimi visualizer: a browser-based face for your agent.
# Copyright (C) 2026 Jared Rhodenizer
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
A tiny static server + state API for the fullstack-kimi face.

The visualizer reads little state files dropped by the voice bridge
(usually the kimi-voice folder) and animates the browser face to match:
    idle -> listening -> thinking -> speaking

Run from the visualizer folder:
    python3 server.py

Then open http://127.0.0.1:8790/ and pick a face.
"""

import http.server
import json
import os
import socketserver
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DEFAULT_PORT = 8790
DEFAULT_BUS_DIR = HERE.parent / "kimi-voice"


def load_config():
    cfg_path = HERE / "kimi-visualizer.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def get_bus_dir():
    cfg = load_config()
    bus = cfg.get("bus_dir")
    if bus:
        return Path(bus).expanduser()
    return DEFAULT_BUS_DIR


def read_state():
    """Read the current voice state from the bus directory."""
    bus = get_bus_dir()
    state_file = bus / ".kimi_state"
    waveform_file = bus / ".kimi_waveform"

    result = {
        "state": "idle",
        "text": "",
        "waveform": [0.0] * 16,
    }

    if state_file.exists():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            result["state"] = data.get("state", "idle")
            result["text"] = data.get("text", "")
        except Exception:
            pass

    if waveform_file.exists():
        try:
            data = json.loads(waveform_file.read_text(encoding="utf-8"))
            result["waveform"] = data.get("levels", [0.0] * 16)
        except Exception:
            pass

    return result


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Keep the terminal quiet except for real errors.
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.serve_gallery()
            return

        if path == "/state":
            self.serve_json(read_state())
            return

        if path == "/config":
            self.serve_json(load_config())
            return

        if path.startswith("/faces/"):
            # /faces/board/ -> serve faces/board/index.html
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[2] == "":
                face_name = parts[1]
                index = HERE / "faces" / face_name / "index.html"
                if index.exists():
                    self.serve_file(index, "text/html")
                    return

        # Fall back to static files under faces/.
        self.directory = str(HERE)
        super().do_GET()

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

    def serve_gallery(self):
        faces = []
        faces_dir = HERE / "faces"
        if faces_dir.exists():
            for item in sorted(faces_dir.iterdir()):
                if item.is_dir() and (item / "index.html").exists():
                    faces.append(item.name)

        html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>fullstack-kimi | pick a face</title>
  <style>
    body {{
      margin: 0; height: 100vh; background: #050505; color: #e0e0e0;
      font-family: system-ui, -apple-system, sans-serif;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}
    h1 {{ font-weight: 300; letter-spacing: 0.1em; margin-bottom: 2rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; max-width: 800px; width: 90%; }}
    a {{
      display: block; padding: 2rem; text-align: center; text-decoration: none;
      color: #0ff; border: 1px solid #0ff3; border-radius: 12px;
      background: #0ff05; transition: all 0.2s;
    }}
    a:hover {{ background: #0ff1; transform: translateY(-3px); }}
    .name {{ font-size: 1.2rem; text-transform: capitalize; }}
  </style>
</head>
<body>
  <h1>fullstack-kimi</h1>
  <div class="grid">
    {''.join(f'<a href="/faces/{f}/"><div class="name">{f}</div></a>' for f in faces)}
  </div>
</body>
</html>"""
        self.serve_response(html, "text/html")

    def serve_response(self, body, content_type):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    config = load_config()
    port = config.get("port", DEFAULT_PORT)

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"fullstack-kimi visualizer running at http://127.0.0.1:{port}/")
        print(f"bus directory: {get_bus_dir()}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
