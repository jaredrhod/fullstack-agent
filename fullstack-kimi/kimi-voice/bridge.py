#!/usr/bin/env python3
# fullstack-kimi voice bridge: push-to-talk agent voice.
# Copyright (C) 2026 Jared Rhodenizer
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Main loop for the fullstack-kimi voice bridge.

Hold the configured talk key to record speech, release to send it to the
agent, then listen as the agent thinks out loud and the face animates.

The bridge writes two state files for the visualizer:
    .kimi_state     -> {"state": "idle|listening|thinking|speaking", "text": "..."}
    .kimi_waveform  -> {"levels": [...]}
"""

import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

import audio
import state
import stt
import tts
from agent import Agent
from config import load_config


class VoiceBridge:
    def __init__(self):
        self.cfg = load_config()
        self.agent = Agent(self.cfg, approve_callback=self._approve_tool)
        self.stt = stt.STT(self.cfg)
        self.tts = tts.TTS(self.cfg)
        self.bus_dir = Path(self.cfg.get("bus_dir", "~")).expanduser()
        self.bus_dir.mkdir(parents=True, exist_ok=True)
        self.state = state.StateWriter(self.bus_dir)
        self.listening = False
        self.running = True
        self.talk_key = self.cfg.get("talk_key", "home")
        self.permission_mode = self.cfg.get("permission_mode", "ask")
        self._approval_received = False
        self._waiting_for_approval = False

        signal.signal(signal.SIGINT, self._on_signal)
        signal.signal(signal.SIGTERM, self._on_signal)

    def _on_signal(self, signum, frame):
        print("\nshutting down...")
        self.running = False
        self.state.set_idle()
        sys.exit(0)

    def _approve_tool(self, name, description):
        if self.permission_mode == "auto":
            return True
        # ask mode: speak the request and wait briefly for the talk key.
        msg = f"May I run {name}?"
        print(f"[asking permission] {msg}")
        self.state.set_speaking(msg)
        self.tts.speak(msg)
        self.state.set_thinking()
        # Simple timeout-based approval: wait up to 5 seconds for the talk key.
        self._approval_received = False
        self._waiting_for_approval = True
        deadline = time.time() + 5
        while time.time() < deadline and self.running:
            if self._approval_received:
                self._approval_received = False
                self._waiting_for_approval = False
                print(f"[approved] {name}")
                return True
            time.sleep(0.05)
        self._waiting_for_approval = False
        print(f"[denied by timeout] {name}")
        return False

    def _on_press(self, key):
        if not self._key_matches(key, self.talk_key):
            return
        if self._waiting_for_approval:
            self._approval_received = True
            return
        if not self.listening:
            self.listening = True
            audio.start_recording()
            self.state.set_listening()
            print("[listening]")

    def _on_release(self, key):
        if self._key_matches(key, self.talk_key) and self.listening:
            self.listening = False
            self.state.set_thinking()
            print("[thinking]")

            wav_path = audio.stop_recording()
            if wav_path is None:
                self.state.set_idle()
                return

            try:
                text = self.stt.transcribe(wav_path)
            except Exception as exc:
                print(f"[stt error: {exc}]")
                self.tts.speak("I didn't catch that.")
                self.state.set_idle()
                return

            if not text or not text.strip():
                self.state.set_idle()
                return

            print(f"you: {text}")

            try:
                reply = self.agent.respond(text)
            except Exception as exc:
                print(f"[agent error: {exc}]")
                self.tts.speak("I'm having trouble thinking right now.")
                self.state.set_idle()
                return

            print(f"{self.cfg.get('name', 'agent')}: {reply}")
            self.state.set_speaking(reply)
            self.tts.speak(reply)
            self.state.set_idle()

    def _key_matches(self, key, name):
        # Handle both pynput Key objects and raw key names.
        try:
            from pynput.keyboard import Key
            if name == "home":
                return key == Key.home
            if name == "space":
                return key == Key.space
            if name == "shift":
                return key == Key.shift
            if name == "ctrl":
                return key == Key.ctrl
            if name == "alt":
                return key == Key.alt
            if hasattr(key, "char") and key.char:
                return key.char.lower() == name.lower()
        except Exception:
            pass
        return False

    def _waveform_thread(self):
        while self.running:
            levels = audio.current_levels()
            if self.listening or self.state.current_state == "speaking":
                self.state.write_waveform(levels)
            time.sleep(0.05)

    def run(self):
        print(f"fullstack-kimi voice bridge")
        print(f"hold [{self.talk_key}] to talk, Ctrl-C to quit")

        # Optional spoken greeting on launch.
        greeting = self.cfg.get("greeting")
        if greeting:
            self.state.set_speaking(greeting)
            self.tts.speak(greeting)
            self.state.set_idle()

        threading.Thread(target=self._waveform_thread, daemon=True).start()

        try:
            from pynput.keyboard import Listener
            with Listener(on_press=self._on_press, on_release=self._on_release) as listener:
                while self.running:
                    listener.join(timeout=0.1)
        except Exception as exc:
            print(f"[keyboard listener error: {exc}]")
            print("falling back to terminal input mode. Type your message and press Enter.")
            while self.running:
                try:
                    text = input("> ")
                    if text.strip():
                        self.state.set_thinking()
                        reply = self.agent.respond(text)
                        print(f"{self.cfg.get('name', 'agent')}: {reply}")
                        self.state.set_speaking(reply)
                        self.tts.speak(reply)
                        self.state.set_idle()
                except EOFError:
                    break


def main():
    bridge = VoiceBridge()
    bridge.run()


if __name__ == "__main__":
    main()
