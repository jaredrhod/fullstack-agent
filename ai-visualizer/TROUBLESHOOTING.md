# Troubleshooting

## The server won't start

- `python3: command not found` on Mac or Linux: install Python 3 from python.org or your package manager. On Windows use `run.bat`, which tries the `py` launcher first and plain `python` second.
- `Address already in use`: something else owns port 8790. Change `"port"` in `ai-visualizer.json` and rerun.

## The face just sits at idle

The face is only as alive as the bus it reads. Work down the chain:

1. `./run.sh --mock speaking` and reload. If the face performs now, the pages are fine and the problem is the bus wiring.
2. Check where your voice line writes its signals. backtalk's default is its own repo folder. Either set `bus_dir` here to that folder, or set `signals_dir` there to this folder. Both configs need a restart after editing.
3. While the voice line talks, the bus folder should contain `.voice_state` and `.voice_waveform` with fresh timestamps. `ls -la` them. If they are not updating, the problem is on the voice line's side.

## No thinking sound

- Browsers block audio until you interact with a page once. Click anywhere on the face, then trigger a thinking state.
- Move the mouse: the SND toggle appears bottom left. Make sure it says SND ON.
- If your voice line plays its own thinking sound, this one stays deliberately silent (that is the `.voice_loading_pid` deference working, not a bug).
- `"thinking_sound": false` in the config disables it everywhere.

## The mic meters run flat

The listening ribbon and MIC gauges want microphone permission, which the browser asks for on first load. Denied permission is fine; the meters just stay flat while everything else works. To grant it later, click the padlock in the address bar and allow the microphone.

## It's choppy

The radial and the neural core are the heaviest faces; the board and the rain are lighter. Chrome and Edge render canvas fastest. A smaller window costs less than fullscreen, and closing other heavy tabs helps more than you'd think. For a frame readout, add `?fps=1` to the board's URL; the neural core draws an always-on FPS number in its chrome. F toggles fullscreen in every face.

## In OBS

Add a browser source with the face URL (for example `http://127.0.0.1:8790/faces/board/index.html`) at your canvas size. The server must be running, and OBS renders its own browser, so grant nothing: the mic meters simply run flat there. If you want the thinking sound in the stream, enable "control audio via OBS" on the source.

## The rain face has no face in it

The face only surfaces while the agent is speaking, and it needs `assets/face.png` to exist: a portrait on a black background, PNG. Swap yours in and reload. If the face loads but looks thin, brighten the portrait; the loader reads pixel brightness as presence.

## URL parameters, for poking at things

- `?demo=1` runs the scripted demo turn with no server bus.
- `?demo=1&state=speaking` pins one state (idle, listening, thinking, speaking).
- `?name=NOVA` overrides the display name in demo mode.
- `?fps=1` shows the frame meter on the board.
- `?shot=speaking&t=5000` renders a deterministic still and sets the page title to "ready" (the screenshot harness used to verify these faces).

## Updating

Run `./update.sh` in this folder (macOS), or double-click the `Update` icon if setup left one. On Windows, ask your agent: "pull the latest ai-visualizer and tell me what changed." The updater shows what changed before applying it and can never touch your `ai-visualizer.json`. If an older updater said "couldn't fast-forward" or mentioned local changes, run `./update.sh` once and it clears: it moves your config out of git's sight and everything flows after.
