# fullstack-kimi voice bridge: speech-to-text.

from pathlib import Path


class STT:
    def __init__(self, cfg):
        self.cfg = cfg.get("stt", {})
        self.engine = self.cfg.get("engine", "whisper_api")

    def transcribe(self, wav_path: Path) -> str:
        if self.engine == "whisper_api":
            return self._whisper_api(wav_path)
        if self.engine == "faster_whisper":
            return self._faster_whisper(wav_path)
        raise ValueError(f"unknown stt engine: {self.engine}")

    def _whisper_api(self, wav_path: Path) -> str:
        from openai import OpenAI
        api_key = self.cfg.get("api_key")
        if not api_key:
            raise RuntimeError("stt whisper_api requires an api_key or OPENAI_API_KEY env var")
        client = OpenAI(api_key=api_key)
        with open(wav_path, "rb") as f:
            result = client.audio.transcriptions.create(model=self.cfg.get("model", "whisper-1"), file=f)
        return result.text.strip()

    def _faster_whisper(self, wav_path: Path) -> str:
        from faster_whisper import WhisperModel
        model = WhisperModel(self.cfg.get("model", "base"), device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(wav_path))
        return " ".join(s.text for s in segments).strip()
