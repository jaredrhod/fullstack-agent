# kimi-visualizer

The browser-based face for fullstack-kimi. It shows an animated visualizer that idles, listens, thinks, and speaks in sync with the agent's voice state.

## Faces

- **board** — living circuit board (default)
- **radial** — concentric wave rings
- **rain** — digital rain
- **neural** — pulsing neuron network

## Run

```bash
python3 server.py
```

Then open http://127.0.0.1:8790/ and pick a face.

## How it works

The server reads state files from the `bus_dir` (usually the `kimi-voice` folder):

- `.kimi_state` — JSON like `{"state": "listening|thinking|speaking|idle", "text": "..."}`
- `.kimi_waveform` — JSON like `{"levels": [0.0, 0.2, ...]}`

The browser polls `/state` several times a second and animates the face accordingly.

## Config

Edit `kimi-visualizer.json`:

```json
{
  "name": "Kimi",
  "face": "board",
  "bus_dir": "~/my-kimi-agent/kimi-voice",
  "port": 8790
}
```

## License

AGPL-3.0-or-later. See root `LICENSE`.
