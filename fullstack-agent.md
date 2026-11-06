# fullstack-agent: setup (ChatGPT)

You are the user's Cursor / ChatGPT agent, and you are about to assemble a complete one: memory, ChatGPT chat, face, and optional hands. This file is the conductor. Collect every answer ONCE, install the pieces, wire them, and end with a working hello.

Ground rules, binding for the whole run:

- **Plain English.** Assume they may be new to this. One-line explanations for technical names.
- **One question at a time.** Wait for each answer.
- **Never delete, overwrite, or move anything the person built.** Replacements leave the old copy on disk and say so out loud.
- **You do the work.** Run commands, write configs, make edits. They only act when needed (API key, camera permission, password).
- **Brain is ChatGPT.** Use OpenAI (`OPENAI_API_KEY`). Do **not** install Claude Code, the Claude Agent SDK, or upstream `backtalk` (it is Claude-only).

## Phase 0: Find home, and find what already exists

**Prerequisite: git.** Check `git --version`. If missing on Windows, ask before installing: `winget install --id Git.Git -e --source winget --silent --accept-package-agreements --accept-source-agreements`. Use full paths for tools installed mid-session. **Write paths with forward slashes.**

**OpenAI key.** Ensure `.env` exists in this toolbox (from `.env.example`) with `OPENAI_API_KEY`. Never commit `.env`. If the key is missing, ask them to paste it into `.env` before chat will work.

If this repo has no `.git` folder (arrived as a zip): wire it to their fork or keep it local; do not force-reset onto upstream in a way that wipes their ChatGPT changes.

The agent's home is the folder **containing** this toolbox. Confirm that path. If they cloned somewhere accidental, ask where the agent should live, create it, and move this repo inside it.

Then look in the home folder:

- **`AGENTS.md` or `CLAUDE.md` already defines an agent:** ADOPT — keep identity, skip identity questions later.
- **Nothing there:** fresh start.

If their agent lives elsewhere, that folder is home — move this toolbox into it. One home only.

Scanning rules:

1. Old Claude Code project memory (`~/.claude/projects/*/memory/`) may be offered for migration only through ai-memory-vault's own wizard — ask which projects, copy never delete.
2. Existing Obsidian vaults: only the one they choose. Never browse other vaults without permission.
3. Anywhere else on disk: ask before you look.

Ask: "Before this, did you set up a voice system, visualizer, or memory vault? If so, where?"

## Phase 1: The menu

Lead with **"the stack"** as the default:

1. **Memory** — plain-text vault the agent reads/writes (ai-memory-vault + Obsidian).
2. **ChatGPT chat** — typed conversation with your agent's personality (`chatgpt/chat.py`).
3. **Face** — browser visualizer (ai-visualizer).

Optional:

- **Hands** (webcam) — barehands board.

## Phase 2: The one interview

Skip anything already adopted or declined.

1. **Their name** (for the greeting).
2. **Agent identity** (if not adopted): A) Jarvis as-is, B) Jarvis renamed, C) build from scratch. Default A if they shrug.
3. **Vault** (if memory): offer Obsidian-registered vaults by name/path plus "brand new vault". Never move a vault. Obsidian required when memory is chosen — follow ai-memory-vault's install for it.
4. **Default face** (if face): board / radial / rain / neural. Default board.
5. **OpenAI model** (optional): default `gpt-4.1-mini`, or whatever they prefer from their account.

## Phase 3: Install the pieces

Clone chosen pieces as siblings of this toolbox from `github.com/jaredrhod/<name>`:

- `ai-memory-vault`
- `ai-visualizer`
- `barehands`

**Do not clone `backtalk`.**

Adoption rules (unchanged in spirit): reuse active copies via paths; never delete hand-built old installs; offer to COPY a custom visualizer scene into `ai-visualizer/faces/`.

**ChatGPT chat:** already in this toolbox under `chatgpt/`. Run `pip install -r chatgpt/requirements.txt` (or `uv pip install -r chatgpt/requirements.txt`) using a real Python (not the Windows Store stub).

**If memory was declined:** write a short `AGENTS.md` and `CLAUDE.md` in the HOME folder with name, role, personality, welcome line, and that this folder is home.

**Then run each chosen piece's own wizard** (`ai-memory-vault.md`, `ai-visualizer.md`, `barehands.md`) with Phase 2 answers pre-filled. Memory first (and Obsidian Part 1 if needed), then face, then hands.

Also write/update home `AGENTS.md` to match identity (memory vault may write `CLAUDE.md` — keep both in sync when you can).

## Phase 4: Wire the seams

- Confirm toolbox `.env` has `OPENAI_API_KEY` (and optional `OPENAI_MODEL`).
- `ai-visualizer/ai-visualizer.json`: `name` = agent name, `face` = their pick. `bus_dir` can stay default or point at a local state folder under the toolbox if you create one.
- `barehands/barehands.json`: `name` = agent name.
- Append mechanic section to home `AGENTS.md` / `CLAUDE.md` (ask first if adopting):

> ## You are the mechanic
> This agent runs on open tools in this folder (memory vault, chatgpt chat, ai-visualizer, barehands). When something breaks or needs changing, fixing it is YOUR job: read that tool's TROUBLESHOOTING.md / README and repair it. Never send the person off to search the internet.

## Phase 5: The first hello

From the toolbox folder:

- Windows: `start.bat chat`
- macOS/Linux: `./start.sh chat`

Verify ChatGPT replies in character. If face was installed, also start it (`start.bat` / `./start.sh`) and confirm the browser opens.

If chat fails, check `.env` and network; do not guess.

## Phase 6: Hand it over

Shut down anything you started for the test drive.

Optional once: offer Jared's marketing skills repo — only if they want it.

Desktop shortcuts named after their agent:

1. **Chat with \<name\>** → runs toolbox `start.bat chat` / `start.sh chat` (ChatGPT).
2. **Face \<name\>** → `start.bat` / `start.sh` when visualizer installed.
3. **\<name\> barehands** → `start.bat hands` / `start.sh hands` when installed.
4. **Update \<name\>** (macOS) → `./update.sh`. Windows: ask in chat to update.

macOS `.command` files need:

```
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
```

Closing notes:

- Daily habit: open **Cursor in the agent home** (parent folder).
- ChatGPT chat uses `AGENTS.md` / `CLAUDE.md` in that home as identity.
- Ask the agent to fix problems — that is part of its job.
- Discord / videos from upstream still help for face/hands/memory: https://discord.gg/YSdsqMv3V8

Test each shortcut with them, then get out of the way.
