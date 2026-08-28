# kimi-barehands

Hand-controlled spatial board for fullstack-kimi. Use your webcam to move notes and images around the screen with bare hands — no controllers, no headset.

## Run

```bash
python3 server.py
```

Then open `http://127.0.0.1:8794/` in Chrome and click **Start barehands**.

## Gestures

- **open** — open palm
- **pinch** — thumb and index together
- **point** — only index finger extended
- **fist** — closed hand
- **neutral** — none of the above

## How it works

The browser page runs MediaPipe Hands locally. Detected gestures are posted to `/state`, and the server writes them to `.kimi_hands` in the `state_dir` (usually the `kimi-voice` folder so the agent can read them).

## Config

Edit `kimi-barehands.json`:

```json
{
  "name": "Kimi",
  "state_dir": "~/my-kimi-agent/kimi-voice",
  "port": 8794
}
```

## License

AGPL-3.0-or-later. See root `LICENSE`.
