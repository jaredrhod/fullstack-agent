# fullstack-agent (ChatGPT fork)

> Upstream by [Jared Rhodenizer](https://jaredrhod.com). This fork keeps the same stack (memory, face, hands) but runs the **brain on ChatGPT / OpenAI** instead of Claude Code.

**Runs on:** [Cursor](https://cursor.com) (or any ChatGPT-capable agent) + an OpenAI API key.

Not an agent that writes full-stack code. **An agent that HAS a full stack: memory, voice/chat, and face, plus an optional set of hands.** When setup finishes, your agent knows who it is and can chat through ChatGPT:

> "Hello [you], what are we working on today?"

## What you get

- **The mind: [ai-memory-vault](https://github.com/jaredrhod/ai-memory-vault).** Persistent plain-text memory (identity lands in `AGENTS.md` / `CLAUDE.md`).
- **The mouth (this fork): ChatGPT chat** in `chatgpt/chat.py` — typed conversation with your agent personality via the OpenAI API. (Upstream [backtalk](https://github.com/jaredrhod/backtalk) is Claude Agent SDK–based; this fork does not wire it.)
- **The face: [ai-visualizer](https://github.com/jaredrhod/ai-visualizer).** Full-screen visualizers.
- **The hands (optional): [barehands](https://github.com/jaredrhod/barehands).** Webcam hand board.

Every piece is optional. The wizard asks which ones you want.

## Install

1. Get an [OpenAI API key](https://platform.openai.com/api-keys).
2. Clone this repo (or open your existing copy) in **Cursor**.
3. Copy `.env.example` → `.env` and set `OPENAI_API_KEY`.
4. In Cursor chat in this folder, say: **set me up**

The installer reads `fullstack-agent.md` and walks you through the rest.

### Chat without the full wizard

```powershell
cd chatgpt
pip install -r requirements.txt
python chat.py
```

Or from the toolbox root after setup:

```powershell
.\start.bat chat
```

## After setup

- **Chat:** `start.bat chat` / `./start.sh chat` — typed ChatGPT session using your agent's identity files.
- **Face / hands:** `start.bat` / `start.bat hands` when those pieces are installed.
- **Daily habit:** open Cursor in your **agent home** (the parent of this toolbox), not only inside the toolbox.
- **Updates:** `./update.sh` (macOS/Linux). On Windows, ask your agent to update and tell you what changed.

## License

Copyright (c) 2026 Jared Rhodenizer. ChatGPT fork adaptations by contributors.

Licensed under AGPL-3.0-or-later. See `LICENSE`.
