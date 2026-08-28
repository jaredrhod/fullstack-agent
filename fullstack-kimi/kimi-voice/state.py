# fullstack-kimi voice bridge: state file writer for the visualizer.

import json
import threading
from pathlib import Path


class StateWriter:
    def __init__(self, bus_dir: Path):
        self.bus_dir = Path(bus_dir)
        self.bus_dir.mkdir(parents=True, exist_ok=True)
        self.current_state = "idle"
        self.current_text = ""
        self.lock = threading.Lock()

    def _write(self):
        state_file = self.bus_dir / ".kimi_state"
        with self.lock:
            state_file.write_text(
                json.dumps({"state": self.current_state, "text": self.current_text}),
                encoding="utf-8",
            )

    def set_idle(self):
        with self.lock:
            self.current_state = "idle"
            self.current_text = ""
        self._write()

    def set_listening(self):
        with self.lock:
            self.current_state = "listening"
            self.current_text = ""
        self._write()

    def set_thinking(self):
        with self.lock:
            self.current_state = "thinking"
            self.current_text = ""
        self._write()

    def set_speaking(self, text: str):
        with self.lock:
            self.current_state = "speaking"
            self.current_text = text
        self._write()

    def write_waveform(self, levels):
        wf = self.bus_dir / ".kimi_waveform"
        wf.write_text(json.dumps({"levels": levels}), encoding="utf-8")
