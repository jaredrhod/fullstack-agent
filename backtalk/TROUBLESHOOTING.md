# Troubleshooting

Written for humans AND for AI assistants. If you're an AI helping someone debug backtalk: read this whole file first, then `logs/backtalk.log`; every load-bearing event (what was heard, what was said, interrupts, engine fallbacks, session rebuilds) is in there. Diagnose from the log, not from guesses.

## Quick fixes

- **`ModuleNotFoundError: No module named 'claude_agent_sdk'` (or any missing module) at launch**: backtalk's Python packages never finished installing, or the environment drifted. From the backtalk folder run `uv sync`, which installs everything from the shipped package list, then launch again. (Launchers updated after this was found in the field run the repair automatically; if yours predates that, update backtalk.) If `uv sync` itself errors, run `uv venv .venv` then `uv pip install -e .` instead.
- **The greeting speaks, then it goes idle and ignores the key (open mic too)**: the step right after the greeting is connecting to Claude Code, the brain, and that connection failed or hung. It is the one startup step that needs a signed-in Claude Code, internet, and available plan usage. The voice line now says this failure out loud and the window stays open with the error; the ladder to fix it: run `claude` in a terminal and confirm a session opens signed in, check your internet, check your plan has usage left. The log agrees: `logs/backtalk.log` ending at "connecting the brain..." with no "brain warm" after it is exactly this failure. Your browser choice has nothing to do with it; the visualizer only displays.
- **Nothing happens when I hold the key (macOS)**: the terminal app needs **Input Monitoring** permission: System Settings → Privacy & Security → Input Monitoring → add your terminal (Terminal, iTerm, etc.), then restart the terminal. The mic prompt is separate and appears on first recording.
- **Mic permission never appeared / recording is silent**: launch from a normal terminal window, not a background service or launcher daemon: the process inherits the *terminal's* microphone permission. Check the input device: `python -m sounddevice` lists them.
- **It records from my headset instead of the mic I wanted (and my headphone audio gets worse while I talk)**: it follows the system default input, and the OS re-points that the moment a headset with a mic connects. On Bluetooth that also drops the headset from high quality into the narrowband call profile, so the music and the voice both degrade mid-sentence. Pin it: set `"mic_device"` in backtalk.json to the input you want, **by name** (`"MacBook Pro Microphone"`). Indices are not stable, so the name is the contract; `python -m sounddevice` lists them. Exact name first, then case-insensitive substring, so `"MacBook Pro"` works too. A name matching nothing falls back to the default and logs every input it did find. (Not `stt_device`, which is the Whisper COMPUTE device, cpu or cuda.)
- **Running under WSL2 and it crashes the moment it tries to speak** (a core dump rather than an error): WSLg puts the audio socket somewhere the audio library does not look. `run.sh` links it on every launch, so this heals itself if you start with `run.sh` rather than calling Python directly. The folder it links into is wiped on reboot, which is why it is redone every time. (Credit where due: found and fixed by shavalejames-blip.)
- **My temp folder is filling up with tiny folders**: the speech engine copies its phoneme library into a fresh temp folder for every voice backend it builds, and the cleanup does not run when the process is KILLED rather than closed, which is what most launchers do. They accumulate forever. The voice line now sweeps its own leftovers at startup, so the total stays at one run's worth. It only ever removes a folder whose entire contents are that one library file. (Credit where due: found and fixed by BigpapaWarren, who had sixty of them.)
- **It stops hearing me after I connect or disconnect a headset** (and looks completely healthy while it does): the audio library caches the device list when it starts, so a device that appears or vanishes afterwards leaves a stale entry behind and every recording after that fails silently. Bluetooth headsets trigger it every time the mic opens, because they flip between listening and call modes. The voice line now rebuilds the audio system and reopens the mic when this happens, and the speaking side survives the rebuild. (Credit where due: found and fixed by CansuKhon.)
- **It hears me but answers slowly**: check `model` in `backtalk.json`. Full-size deep-work models make every reply noticeably slower; the fast tier is the point of a voice loop. Also confirm the model id is the FULL id, never a bare alias; aliases can silently resolve to an older model through the SDK's bundled CLI.
- **First reply after launch is slow**: that's the one-time prompt-cache toll, mostly hidden behind the greeting. Warm turns are the real speed.
- **It starts cold and forgets the last conversation after a restart**: that is the default (a fresh session every launch is predictable). Want it to pick up where it left off? Tell your agent to set `"resume_last_session": true` in backtalk.json. From then on every launch reattaches to the previous conversation, and a stale saved session falls back to fresh with a log line instead of breaking the launch. The saved conversation lives on your machine as a Claude Code transcript (kept for 30 days from last use by default), and a long conversation never dies from length: it compacts itself automatically, older turns becoming a summary while recent ones stay verbatim. Start over any time by saying "clear the session."
- **The voice talks too fast or too slow**: the built-in voice has a pace dial, `"speed"` in backtalk.json. 1.0 is native, 1.15 is brisker, 0.9 is slower. ElevenLabs pace lives in the `master` chain's atempo value instead.
- **Updating, or an update that complains about local changes**: run `./update.sh` in this folder (macOS), or double-click the `Update` icon if setup left one. On Windows, ask your agent: "pull the latest backtalk and tell me what changed." The updater shows what changed before applying it and can never touch your `backtalk.json`. If an older updater said "couldn't fast-forward" or mentioned local changes, run `./update.sh` once and it clears: it moves your config out of git's sight and everything flows after.
- **The voice sounds robotic**: you're hearing Kokoro's base register, or the wrong voice for the language. Try `bm_george`, `bm_daniel`, `am_michael`, `af_heart`. Remember the first letter must match the language pipeline (`b…` British, `a…` American).
- **`espeak` errors when the voice loads**: the system `espeak-ng` package is missing (the pip-bundled build inside the voice engine is broken (known upstream); the system package is the supported path). `brew install espeak-ng` / `sudo apt install espeak-ng`, then re-run.
- **Choppy or slow-motion audio on a weak machine**: lower `stt_model` to `base.en` or `tiny.en`. The playback side already buffers 0.75s ahead specifically so slow machines don't garble.
- **Two voices answering at once**: two copies are running. `./run.sh` kills the previous instance on launch; if you started one some other way, kill it. One body, one mouth.
- **Spotify stays quiet after it stops talking**: the restore is debounced ~0.5s; if the process was force-killed mid-speech the restore can be lost. It self-corrects on the next duck, or nudge the volume by hand.
- **ElevenLabs sounds worse than their website**: their site previews are mastered demo clips; the raw API never matches them. The shipped `master` ffmpeg chain closes the gap; make sure `ffmpeg` is installed, and don't set the style parameter or switch to the multilingual model for English (both make delivery slow and dull).
- **It started asking permission out loud after an update**: that is the new default (safe by default, auto-approve by choice). Say "stop asking for permission" in a voice session and confirm for an immediate, saved flip; or tell your agent to set `"permission_mode": "bypassPermissions"`, which takes effect the next time the voice line starts. The agent writes the config, never you.
- **It asked permission, then said "no answer, so I didn't do it"**: the spoken ask waits about 75 seconds, then treats silence as no. Hold the key and answer with an exact "yes" (or "go ahead", "approved") to approve, "details" to hear the exact command it wants to run, or anything else to deny; a denial's words are passed back to the agent as the reason, so spoken redirections work. Done with the checks entirely? "Stop asking for permission" and "turn off the permission prompts" both work, with a confirm.
- **A voice command didn't trigger**: console phrases match exactly, spoken alone: "clear the session", "compact the session", "switch to the deep model", "back to the fast model", "set effort to low" (or medium, high, max), "usage report", "go hands free" and "push to talk mode" (the microphone), "stop asking for permission" and "start asking again" (approvals). Extra words around them make a normal sentence for the agent instead. That guard is deliberate.
- **"Hands-free" vs auto-approve, because the words matter**: hands-free is the MICROPHONE (always listening, no button; "go hands free" / "push to talk mode"). Auto-approve is PERMISSIONS (act without asking; "stop asking for permission" / "start asking again"). They are separate settings and switch separately.
- **It answers my previous question instead of the one I just asked**: this is the interrupt-desync bug this codebase specifically armors against (`brain.reset_turn`); if you EVER see it, something has changed in the SDK. Grab `logs/backtalk.log` and file an issue; the log will show whether the stale-turn drain ran.

## Windows notes

- **No install.sh or run.sh:** they are Mac and Linux shell scripts. The wizard (`backtalk.md`) performs the install natively on Windows; launch with `uv run python -m backtalk.main`.
- **espeak-ng:** install it with winget or the official installer. backtalk looks for `libespeak-ng.dll` in the usual Program Files locations; if yours lives elsewhere, set `PHONEMIZER_ESPEAK_LIBRARY` to the dll's full path.
- **The ElevenLabs key** lives in the `ELEVENLABS_API_KEY` environment variable for now; Credential Manager support is planned.
- **One copy at a time:** run.sh's single-instance guard is Mac and Linux; on Windows, close the old window before starting a new one, or two voices answer one mic.
- **Speed:** `stt_device: "auto"` uses CUDA when present and CPU otherwise; CPU with `small.en` is plenty fast on a normal machine.

## The voice went robotic again (ElevenLabs users)

That sound is the safety net working: on any ElevenLabs failure, backtalk falls back to the built-in Kokoro voice instead of going mute. The reason is one line in `logs/backtalk.log`; look for `elevenlabs failed`. The usual causes, most common first:

1. **Out of credits.** The free tier's monthly allowance goes fast in real conversation. Check usage on your ElevenLabs dashboard; the starter plan fixes it.
2. **The key isn't reachable.** The keychain item is `backtalk-elevenlabs` (macOS/Linux); on Windows it's the `ELEVENLABS_API_KEY` environment variable, which only newly opened programs can see, so restart the voice line from a fresh window after setting it.
3. **`ffmpeg` missing.** Run `ffmpeg -version`; if that fails, install it (`brew install ffmpeg` / `apt install ffmpeg` / `winget install Gyan.FFmpeg`).
4. **No internet.** The built-in voice covers you until it's back; nothing to fix in backtalk.

## Hands-free listening: the tradeoff

Hands-free listening (the setup question, `"mic_mode": "open"`, the spoken "go hands free", or the `--open-mic` launch flag) listens continuously with voice-activity detection instead of hold-to-talk. Know what you're trading: any speech in the room (a video, music with vocals, another voice assistant) can be transcribed and answered as if it were you. Push to talk is the default because the button is a perfect voice-activity detector and the mic is *closed* the rest of the time. Two things stay true in hands-free: the talk key still works (it interrupts, and holding it always gets you heard over room noise), and spoken permission checks accept only an exact "yes", so stray room audio cannot approve an action. With open speakers, answer permission checks with the button held, or wear headphones. `--barge-in` (interrupting it by talking over it) additionally requires headphones, or it hears its own reply and interrupts itself.

## For AI assistants: the architecture in six lines

```
hold key -> ears.record_held (sounddevice, 16kHz int16)
         -> ears.transcribe (faster-whisper, in-process, local)
         -> brain.ask_stream (warm Claude Agent SDK session,
                              cwd = agent_dir, streams sentences)
         -> mouth.say_chunk (kokoro in-process -> one long-lived
                             OutputStream; ElevenLabs optional)
signals.py mirrors state to .voice_* files (+ optional barehands state/)
permission_mode "ask": gated tools pause the turn and route to a spoken
                       yes/no (main.make_permission_gate). The LIVE
                       auto-approve switch is a gate flag; a session
                       BOOTED in bypassPermissions is real SDK bypass
                       and never consults the gate. The mic mode
                       (_MIC, ptt/open) is a separate axis: one loop,
                       the open mic joins the wait-set in "open" mode,
                       and the talk key works in both
```

Three land mines with warning signs on them; do not "simplify" these away:

1. **The key-repeat filter in `ptt.py`.** The OS fires on_press continuously while a key is held; without the held-state flag, every repeat cancels the reply before it can speak.
2. **The one long-lived output stream in `mouth.py`.** A fresh stream per sentence causes onset blips or dead air on USB interfaces, Bluetooth, and streaming mixers. Interrupts pad silence into the stream; they never close it.
3. **`brain.reset_turn` in `brain.py`.** The SDK has one shared message stream with no query/response pairing; an interrupted turn leaves its leftovers buffered, and without the drain every later answer is off by one question.
4. **The pending-permission routing in `main.py`.** While a spoken permission ask is waiting, the next utterance is the ANSWER: it must never be treated as an interrupt or a new turn, or the paused turn gets cancelled out from under the SDK. The same goes for the live auto-approve switch: the CLI refuses a live flip INTO bypassPermissions (it needs the danger flag at launch), which is why auto-approve is a gate flag instead of an SDK mode change.
5. **The mic generation counter (`_MIC["gen"]`).** A live switch between push-to-talk and hands-free listening bumps it; the open mic's abort callable watches it, and any capture born under an old generation is discarded. Without it, a switch back to push-to-talk leaves an open mic capturing one final utterance that then fires as a ghost turn.

## Verify a working install

1. `./run.sh` → greeting speaks.
2. Hold the key, ask something, release → answer within ~2s.
3. Interrupt mid-reply with the key → it stops within a syllable.
4. Interrupt, then ask something NEW → the answer matches the NEW question (repeat 3×: that's the stream drain proving itself).
5. Ask something that needs a tool ("what's in my notes about X") → it speaks filler within a couple of seconds, then the answer.
6. Type a message in the terminal → spoken reply, same conversation.
7. Say "usage report" → it speaks turns and tokens (plus cost when the API reports one).
8. In ask mode: request a small file write → the spoken permission check plays → "yes" proceeds, and a second attempt answered "no" stands down.
9. Say "goodbye <name>" → sign-off plays, process exits, music restores.
