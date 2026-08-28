# Troubleshooting

## It says "MOONSHOT_API_KEY not set"

Set the key in your environment:

```bash
export MOONSHOT_API_KEY="..."
```

Or put it in `kimi-voice.json` under `llm.api_key`.

## The talk key doesn't do anything

- Make sure `mic_mode` is `ptt` (push-to-talk).
- Try a different `talk_key`: `home`, `space`, `shift`, `ctrl`, `alt`, or a single letter.
- If pynput cannot access input devices, the bridge falls back to terminal typing mode.

## I get "No input device"

Your microphone may be in use by another app, or sounddevice cannot see it. Check System Settings → Privacy & Security → Microphone.

## The agent replies but I don't hear anything

- If using `pyttsx3`, make sure your system volume is up.
- If using `edge_tts`, make sure `ffmpeg` is installed.
- If using `say`, it only works on macOS.

## The face doesn't move

Check that `kimi-voice.json` has the same `bus_dir` as `kimi-visualizer.json`.

## STT is wrong

- Speak closer to the mic.
- Use a quieter room.
- Switch to `faster_whisper` local model for better offline accuracy.
