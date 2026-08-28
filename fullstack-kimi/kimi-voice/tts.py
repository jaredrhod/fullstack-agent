# fullstack-kimi voice bridge: text-to-speech.

import tempfile
from pathlib import Path

import audio


class TTS:
    def __init__(self, cfg):
        self.cfg = cfg.get("tts", {})
        self.engine = self.cfg.get("engine", "pyttsx3")

    def speak(self, text: str):
        if not text:
            return
        if self.engine == "pyttsx3":
            self._pyttsx3(text)
        elif self.engine == "edge_tts":
            import asyncio
            asyncio.run(self._edge_tts(text))
        elif self.engine == "say":
            import subprocess
            subprocess.run(["say", text], check=False)
        else:
            raise ValueError(f"unknown tts engine: {self.engine}")

    def _pyttsx3(self, text: str):
        import pyttsx3
        engine = pyttsx3.init()
        rate = self.cfg.get("rate")
        if rate:
            engine.setProperty("rate", rate)
        voice = self.cfg.get("voice")
        if voice:
            engine.setProperty("voice", voice)
        engine.say(text)
        engine.runAndWait()

    async def _edge_tts(self, text: str):
        import edge_tts
        voice = self.cfg.get("voice", "en-US-AriaNeural")
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            mp3_path = tmp.name
        await communicate.save(mp3_path)
        # Convert to wav for simple playback.
        wav_path = Path(mp3_path).with_suffix(".wav")
        import subprocess
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, str(wav_path)], check=False, capture_output=True)
        audio.play_wav(wav_path)
