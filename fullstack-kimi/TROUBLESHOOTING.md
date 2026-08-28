# Troubleshooting

This file covers only the problems that live BETWEEN the pieces. Each piece owns its own deeper guide: `kimi-memory-vault/TROUBLESHOOTING.md`, `kimi-voice/TROUBLESHOOTING.md`, `kimi-barehands/TROUBLESHOOTING.md`, `kimi-visualizer/TROUBLESHOOTING.md`.

## I closed the window in the middle of setup

Nothing is lost. Open a new terminal, go back to the toolbox folder (`cd ~/my-kimi-agent/fullstack-kimi`), and run:

```
kimi --continue
```

That reopens your most recent session. Tell it "we got cut off, keep going with the setup."

## The install command opened Kimi Code CLI, but it acts like nothing's there

Then the download step failed before Kimi Code CLI started, and the error is in your terminal scrollback. Type `/exit`, scroll up, and read it.

## Kimi Code CLI says "command not found"

Install Kimi Code CLI first: <https://www.kimi.com/code>. The installer expects the `kimi` command on your PATH.

## The face sits at idle while the voice talks

The wiring is one config line, plus a restart. Check both:

1. `kimi-visualizer/kimi-visualizer.json` should have `"bus_dir"` pointing at your `kimi-voice` folder.
2. Restart the visualizer server after any config change (Ctrl-C the stack, run start.sh again).

## The greeting doesn't speak on launch

The greeting line lives in `kimi-voice/kimi-voice.json` under `"greeting"`. If it is missing or empty, the launch is silent by configuration.

## start.sh says a piece is starting but nothing appears

- The face opens a browser tab automatically. If no tab appears, open `http://127.0.0.1:8790/` yourself and pick your face from the gallery.
- The hands never open a tab automatically: open `http://127.0.0.1:8794/` in Chrome.
- Two stacks can't run at once. If a port is already busy from an earlier session, Ctrl-C the old terminal or close it, then start again.

## My agent forgot who it is

Your agent's identity lives in the `AGENTS.md` (and optional `SYSTEM.md`) in your HOME folder (the folder containing all the tool folders), and Kimi Code CLI only reads it when you open Kimi Code CLI IN that folder. Opening Kimi Code CLI inside one of the tool subfolders boots the tool's own instructions instead.

## I moved my agent folder somewhere else

Everything is wired with paths, so a move breaks the wires. Open Kimi Code CLI in the new location and say: "read fullstack-kimi/fullstack-kimi.md and re-run the wiring phase."

## Updates

`./fullstack-kimi/update.sh` pulls every piece. Your files (your AGENTS.md/KIMI.md, your vault, your notes) are never inside the repos' tracked files, so updates cannot touch them.
