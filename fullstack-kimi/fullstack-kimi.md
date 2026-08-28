# fullstack-kimi: setup

You are the user's Kimi Code CLI agent, and you are about to assemble a complete one: memory, voice, face, and hands. This file is the conductor. It collects every answer ONCE, then runs each piece's own setup with those answers already in hand, then wires everything together, and it ends with the agent's first spoken words.

This is a Kimi-powered port of [fullstack-agent](https://github.com/jaredrhod/fullstack-agent). The brain is **Kimi Code CLI** — the terminal agent that reads files, runs commands, and calls tools. The other pieces (memory, voice, face, hands) are local services that connect to it.

Ground rules, binding for the whole run:

- **Plain English.** Assume the person installed Kimi Code yesterday. Every technical thing gets a one-line explanation before it gets a name.
- **One question at a time.** Wait for each answer.
- **Never delete, overwrite, or move anything the person built.** Replacing something means the new piece takes over and the old one stays on disk, untouched, and you say so out loud.
- **You do the work.** Run the commands, write the configs, make the edits. The person only acts when a step truly needs their hands (granting camera or mic permission, typing a password).

## Phase 0: Find home, and find what already exists

**Prerequisite check, before anything else: git.** Check with `git --version`. If it's missing, ask first, never silently: "One tool before we build: git, the free program that downloads and updates all the pieces. Want me to install it for you right now?" On a clear yes, install it (the platform-appropriate way) and verify it landed.

**Then, if this repo has no `.git` folder inside it** (it arrived as a zip): convert it into a real clone in place, so the update script can reach it forever after. Inside this folder: `git init -b main`, `git remote add origin https://github.com/jaredrhod/fullstack-kimi`, `git fetch origin`, `git reset --hard origin/main`, `git branch --set-upstream-to=origin/main main`. Nothing the person sees changes; the folder just gains its connection to updates. Do this quietly and move on.

The agent's home is the folder **CONTAINING** this repo. Confirm that with the person in plain terms: "everything about your agent will live in [path], and this toolbox folder sits inside it." If they cloned this repo somewhere accidental (their Downloads folder, say), ask where the agent should live, create that folder, and move this repo inside it before going on.

Then look around the home folder and establish which situation you are in:

- **An `AGENTS.md` or `KIMI.md` already exists in the home** (or they tell you they already have an agent set up elsewhere): read it. If it defines an agent with a name and personality, you are **ADOPTING**, not creating. Say something like "found [name], keeping them exactly as they are," and skip every identity question later.
- **Nothing there:** fresh start. All questions apply.

**If their agent lives somewhere else, THAT folder is the home.** Move this toolbox repo inside it, remove the now-empty folder the install command created, and proceed as an adoption. Never make a second home for an agent that already has one.

Three scanning rules that hold for the whole run:

1. **Old Kimi Code project memory is fair game.** If there are past sessions or project notes the person wants the new memory system to take over, list them and ask which ones to migrate. Migration copies; it never deletes the originals.
2. **Existing Obsidian vaults are off-limits in the new-vault path.** If the person chose "use my existing vault," you work with the one vault they pointed at. If they chose a new vault, you never read any other vault they own.
3. **Everywhere else on their disk: ask before you look.** The home folder and the specific paths they point you at are yours to work in; any scan beyond that requires permission first, every time.

## Phase 1: The menu

Offer the stack, each piece in one plain sentence. **Lead with the easy answer: "the stack" (all three) is the first option and the default.**

1. **The memory**: a filing cabinet of plain text files your AI actually reads and writes, so it remembers you, your work, and every lesson across every session.
2. **The voice**: hold a key, say the thing out loud, and your agent answers through your speakers about a second later.
3. **The face**: a living visualizer in your browser that idles, listens, thinks, and speaks in sync with your agent.

Then mention the optional add-on, once, without pushing it:

- **The hands** *(optional extra, needs a webcam)*: move notes and images around your screen with your bare hands, no controllers, no headset.

## Phase 2: The one interview

Collect every remaining answer now, so no later step ever has to ask. Skip anything Phase 0 already adopted or Phase 1 declined.

1. **Their name.** You will use it in the finale.
2. **The agent's identity** (skip entirely if adopted): offer three doors — A: take a default persona as-is, B: rename it, C: build from scratch. If they shrug, door A.
3. **The vault** (memory piece): Obsidian is required — it is how the person sees and owns their agent's memory. Check `obsidian.json` for existing vaults, offer them by name, and always offer a brand-new vault just for this system. A fresh vault lives at `~/<their name for it>`, directly in the home folder next to the agent folder.
4. **The microphone** (voice piece): push-to-talk (default, mic closed unless a key is held) or hands-free listening (always on). Then, which key. Defaults: push-to-talk, the home key.
5. **The voice engine** (voice piece): built-in/local (free, offline, decent but synthetic) or cloud TTS (natural, needs an account/key). Capture which they want.
6. **The default face** (face piece): board, radial, rain, or neural. Default: board.
7. **Permissions** (voice piece): when their agent wants to do something real mid-conversation, should it ask out loud first and wait for spoken yes/no (default), or run fully auto-approved? Their answer lands in the voice config in Phase 4.

## Phase 3: Install the pieces

Each piece can be used bundled inside this repo or cloned as a sibling from `github.com/jaredrhod/<name>`:
`kimi-memory-vault`, `kimi-voice`, `kimi-visualizer`, `kimi-barehands`.

If the bundled copy exists, use it. Otherwise clone the repo into the home folder.

**The adoption exceptions, checked before each clone:**

- A piece already downloaded from these repos somewhere on the machine, that they actively use: do not duplicate it. Wire to their copy where it stands.
- A stale, unmodified copy sitting outside the home folder is different: prefer a fresh copy inside the home (so the update script reaches it) and leave the old one untouched.

**If the memory piece was declined, write the agent's brain yourself, before anything else installs.** Create a short `AGENTS.md` in the HOME folder carrying the identity from Phase 2: the agent's name, role, personality, and welcome line, plus one line saying this folder is where the agent lives.

**Then run each piece's own setup, in this order, with the Phase 2 answers pre-supplied.** Each repo has a wizard file (`kimi-memory-vault.md`, `kimi-voice.md`, `kimi-barehands.md`, `kimi-visualizer.md`). Read each one and execute it faithfully, with one standing modification: any question the interview already answered gets filled in silently instead of asked again.

1. **kimi-memory-vault** first (it creates the vault and writes the person's `AGENTS.md` / `KIMI.md` into the HOME folder).
2. **kimi-voice** second (it installs Python deps, STT/TTS models, and the push-to-talk listener).
3. **kimi-visualizer** third (no heavy dependencies; seconds).
4. **kimi-barehands** fourth (no dependencies; camera permission happens on first open).

## Phase 4: Wire the seams

This part belongs to this wizard alone. Write these config values, then read each file back to confirm it landed:

- `kimi-voice/kimi-voice.json`: `agent_dir` = the home folder. `name` = the agent's name. Add the vault's path to `extra_dirs`. If hands were installed: `barehands_state_dir` = the `kimi-barehands/state` folder.
- `kimi-voice/kimi-voice.json` greeting: set it to exactly `Hello <their name>, what are we working on today?`
- `kimi-voice/kimi-voice.json`: `permission_mode` = their Phase 2 answer, `"ask"` or `"auto"`; `mic_mode` = their Phase 2 answer, `"ptt"` or `"open"`.
- `kimi-visualizer/kimi-visualizer.json`: `name` = the agent's name. `face` = their pick. `bus_dir` = the kimi-voice folder.
- `kimi-barehands/kimi-barehands.json`: `name` = the agent's name.

Explain the wiring in one sentence as you go: "the voice writes little status notes; the face reads them; that is the whole connection."

Last wire: **make the agent the mechanic.** Append a short section to the `AGENTS.md` in the home folder (for an ADOPTED file, show the person the section and ask before adding it):

> ## You are the mechanic
> This agent runs on open tools that live in this folder (the memory vault, voice, visualizer, hands). When anything breaks, acts strange, or needs changing, fixing it is YOUR job, not the person's: read the relevant tool's TROUBLESHOOTING.md and README, diagnose, and repair it yourself. Never send the person off to search the internet. If they ask how something works, explain it in plain English.

## Phase 5: The first hello

From the home folder, run `./fullstack-kimi/start.sh` (Windows: `fullstack-kimi\start.bat`). What should happen, and what you verify:

1. The face's server starts and the browser opens on their chosen face, with the agent's name on it.
2. The voice line warms up and then SPEAKS: "Hello [their name], what are we working on today?" while the face pulses with the words.
3. Have them hold the talk key and ask their agent anything. Watch the face walk listening, thinking, speaking. First reply lands in a couple of seconds.

If they skipped the voice: the face still opens, and you deliver the greeting yourself, in text, word for word. Nobody's first hello is silent.

If any step fails, each repo has a `TROUBLESHOOTING.md`; work the relevant one with them instead of guessing.

## Phase 6: Hand it over

First, **shut down the finale stack you started in Phase 5**, so the launcher tests below can bind the same ports and nothing you spawned outlives setup. Kill exactly the process IDs you started.

Then, **make the launchers**, so they never have to remember any of this. Shortcuts on their Desktop, named with THEIR agent's name (skip any mode whose pieces they did not install; the Update shortcut is for everyone):

1. **`Chat with <name>`** opens a typed Kimi Code CLI session in the home folder. (macOS: a `.command` file; Windows: a `.bat`.)
2. **`Talk to <name>`** starts the voice and the face.
3. **`<name> barehands`** starts the voice and the hands board.
4. **`Update <name>`** pulls the newest version of every installed piece.

**Every macOS `.command` MUST carry this line right after the shebang, before anything else runs:**

```
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
```

On macOS make each `.command` executable, and warn them once: the first double-click may ask permission; that is macOS being protective, click Open.

Then say the closing pieces, warmly and briefly, WHILE THEY ARE STILL IN THIS SESSION:

- **The daily habit:** the Desktop shortcuts ARE the agent. Chat when they want to type, Talk when they want the voice and the face, barehands when they want the voice and the board.
- **Closing a window never loses anything:** `kimi --continue` in the home folder reopens the most recent session mid-thought. The agent only wakes up as itself when Kimi Code CLI opens in its home folder.
- **If anything ever breaks, acts weird, or confuses you:** ask ME. Open the chat and tell me what is wrong, and I will fix it for you. You never need to search the internet or read a manual.
- **Updating:** double-click `Update <name>` to get the newest version of everything.
- **Where the knobs live:** each piece's config file sits in its own folder, and each piece's README explains its own tricks.

**Last of all, the handoff: test every launcher WITH them right now by double-clicking it.** Never hand over an untested shortcut.

Then get out of the way. The agent runs itself from here.
