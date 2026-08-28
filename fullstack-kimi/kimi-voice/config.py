# fullstack-kimi voice bridge: configuration loader.

import json
import os
from pathlib import Path

DEFAULT_CONFIG = Path(__file__).parent / "kimi-voice.json"


def load_config():
    path = Path(os.environ.get("KIMI_VOICE_CONFIG", DEFAULT_CONFIG)).expanduser()
    cfg = json.loads(path.read_text(encoding="utf-8"))

    # Resolve paths.
    for key in ("agent_dir", "bus_dir"):
        if key in cfg:
            cfg[key] = str(Path(cfg[key]).expanduser())
    if "extra_dirs" in cfg:
        cfg["extra_dirs"] = [str(Path(d).expanduser()) for d in cfg["extra_dirs"]]

    # Inherit API keys from environment if not set in config.
    llm = cfg.setdefault("llm", {})
    if not llm.get("api_key"):
        llm["api_key"] = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("OPENAI_API_KEY")

    stt = cfg.setdefault("stt", {})
    if not stt.get("api_key"):
        stt["api_key"] = os.environ.get("OPENAI_API_KEY") or os.environ.get("MOONSHOT_API_KEY")

    return cfg
