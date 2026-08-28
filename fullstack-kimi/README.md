# fullstack-kimi

> **Status:** installer scaffold + working visualizer. `kimi-visualizer` is bundled and runs a browser-based face. The other component repos (`kimi-memory-vault`, `kimi-voice`, `kimi-barehands`) are stubs that will be linked once they are published.

A Kimi-powered port of [fullstack-agent](https://github.com/jaredrhod/fullstack-agent). It gives Kimi Code CLI the same full stack: **memory, voice, face, and optional hands**.

## Why Kimi Code CLI as the brain?

Kimi Code CLI is the terminal agent from Moonshot AI. It reads files, runs shell commands, calls tools, and supports MCP servers. By building around it instead of calling the raw Kimi API, we reuse:

- Session history and resume (`kimi --continue`)
- Tool use and MCP
- Project context via `AGENTS.md`
- The Wire protocol, which lets external programs drive a session

The other pieces connect to Kimi Code CLI through **state files** and the **Wire bridge**.

## What you get

- **The mind: `kimi-memory-vault`.** Persistent memory built on plain text markdown files that Kimi Code reads and writes.
- **The mouth: `kimi-voice`.** Push-to-talk voice input and spoken output. Bridges to Kimi Code CLI over Wire.
- **The face: `kimi-visualizer`.** Browser-based visualizers that idle, listen, think, and speak in sync.
- **The hands: `kimi-barehands` (optional).** Webcam hand-tracking for moving notes and images.

## Install

Requires [Kimi Code CLI](https://www.kimi.com/code) and git. Then one paste into your terminal:

```bash
mkdir -p ~/my-kimi-agent && cd ~/my-kimi-agent && git clone https://github.com/jaredrhod/fullstack-kimi && cd fullstack-kimi && kimi "set me up"
```

The installer asks which pieces you want, sets up the vault, wires the configs, and leaves Desktop shortcuts.

## After setup

- **Chat:** double-click `Chat with <name>` to open a typed Kimi Code CLI session.
- **Talk:** double-click `Talk with <name>` for voice + face.
- **Hands:** double-click `<name> barehands` for voice + hand board.
- **Update:** double-click `Update <name>` to pull the newest versions.

## Differences from fullstack-agent

| fullstack-agent | fullstack-kimi |
|-----------------|----------------|
| Claude Code host | Kimi Code CLI host |
| `CLAUDE.md` identity | `AGENTS.md` + optional `SYSTEM.md` identity |
| `claude --continue` | `kimi --continue` |
| `backtalk` voice bridge | `kimi-voice` Wire bridge |

## License

Copyright (c) 2026 Jared Rhodenizer.

Licensed under the GNU Affero General Public License, version 3 or later (AGPL-3.0-or-later). See the root `LICENSE` file for full terms.
