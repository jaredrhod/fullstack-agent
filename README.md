# June

**June** is a personal AI assistant that runs entirely on your local machine — no subscriptions, no cloud, no payments.

> "Hello, what are we working on today?"

## What you get

Four pieces, each its own open-source component, assembled into one voice agent:

- **The brain:** [Ollama](https://ollama.com) running `qwen2.5:7b` (or `llama3.2`) locally. Fast, private, free.
- **The mouth:** [backtalk](https://github.com/jaredrhod/backtalk) — hold a key, speak, and June answers through your speakers a second later. Hearing and voice run on free local models (Whisper + Kokoro).
- **The face:** [ai-visualizer](https://github.com/jaredrhod/ai-visualizer) — full-screen visualizer that idles, listens, thinks, and speaks in sync with the conversation.
- **The memory:** [ai-memory-vault](https://github.com/jaredrhod/ai-memory-vault) — persistent memory built on plain Markdown files in Obsidian.

## Requirements

- Windows 10/11 (64-bit)
- [Ollama](https://ollama.com) installed
- Python 3.11 (installed via `uv` automatically)
- A microphone and speakers

## Setup

### 1. Start Ollama

Launch Ollama from the Start Menu. Wait for the llama icon to appear in the system tray.

### 2. Pull the model

```powershell
ollama pull qwen2.5:7b
```

This downloads ~4.4 GB. Do it once. (Or use `llama3.2` which is already installed).

### 3. Install dependencies

```powershell
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"
cd backtalk
uv sync --inexact
```

### 4. Launch

Double-click `start.bat` or run:

```powershell
.\start.bat
```

Hold the **Home** key (or say *"go hands free"*) and speak. June answers through your speakers.

Say **"goodbye June"** to hang up.

## Voice console commands

These exact phrases, spoken alone, control the session:

| Phrase | Effect |
|--------|--------|
| `"goodbye June"` | Hang up |
| `"clear the session"` | Reset conversation history |
| `"switch to the deep model"` | Use `qwen2.5:7b` / larger model |
| `"back to the fast model"` | Return to the default model |
| `"go hands free"` | Always-listening mic mode |
| `"push to talk mode"` | Hold-key mic mode (default) |
| `"usage report"` | Spoken token count for this session |

## Configuration

Edit `backtalk/backtalk.json`:

```json
{
  "agent_dir": "d:/Personal/Projects/AI Trials/Friday",
  "name": "June",
  "model": "llama3.2:latest",
  "deep_model": "qwen2.5:7b",
  "ollama_url": "http://localhost:11434/v1",
  "ptt_key": "home",
  "voice": "bm_lewis",
  "stt_model": "small.en",
  "stt_device": "cpu"
}
```

June's personality lives in [`AGENTS.md`](./AGENTS.md).

## Troubleshooting

See [`TROUBLESHOOTING.md`](./TROUBLESHOOTING.md) for common issues. If something breaks, open a chat and describe the problem — June is built to diagnose and fix her own stack.

## License

Code components are licensed under the GNU Affero General Public License v3 or later (AGPL-3.0-or-later). See `LICENSE`.

Built by **Akhil**, powered by open-source tools.
