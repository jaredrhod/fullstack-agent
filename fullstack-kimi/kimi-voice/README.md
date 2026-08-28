# kimi-voice

The voice bridge for fullstack-kimi. Hold a key, speak, and the agent answers out loud while the face animates.

## Quick start

1. Set your Moonshot API key:

```bash
export MOONSHOT_API_KEY="your-key"
```

2. Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run:

```bash
./run.sh
```

Hold the configured talk key (default: `home`) to speak. Release to send. Ctrl-C to quit.

## How it works

1. `audio.py` records while the talk key is held.
2. `stt.py` transcribes the recording.
3. `agent.py` sends the text to the Kimi API and gets a reply.
4. `tts.py` speaks the reply.
5. `state.py` writes `.kimi_state` and `.kimi_waveform` so `kimi-visualizer` can animate.

## Config

Edit `kimi-voice.json`:

```json
{
  "name": "Kimi",
  "greeting": "Hello there, what are we working on today?",
  "agent_dir": "~/my-kimi-agent",
  "bus_dir": "~/my-kimi-agent/kimi-voice",
  "mic_mode": "ptt",
  "talk_key": "home",
  "permission_mode": "ask",
  "stt": { "engine": "whisper_api", "model": "whisper-1" },
  "tts": { "engine": "pyttsx3", "rate": 180 },
  "llm": { "backend": "kimi_api", "model": "kimi-k3" }
}
```

## STT engines

- `whisper_api` — OpenAI Whisper API (requires `OPENAI_API_KEY`)
- `faster_whisper` — local Whisper (requires `faster-whisper` installed)

## TTS engines

- `pyttsx3` — local, offline, works everywhere
- `edge_tts` — natural cloud voices (requires `edge-tts` and ffmpeg)
- `say` — macOS built-in

## License

AGPL-3.0-or-later. See root `LICENSE`.
