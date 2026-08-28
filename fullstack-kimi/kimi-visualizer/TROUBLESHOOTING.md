# Troubleshooting

## The browser opens to a gallery instead of a face

The root page is the gallery. Pick a face, or go directly to `/faces/board/`.

## The face is stuck at idle

1. Check that `kimi-visualizer.json` has the right `bus_dir` pointing at your voice bridge folder.
2. Make sure the voice bridge is writing `.kimi_state` and `.kimi_waveform` files.
3. Restart the visualizer server after any config change.

## The face never shows the agent's name

The name comes from `/config`, which reads `kimi-visualizer.json`. Make sure the `name` field is set and restart the server.

## Port already in use

Either another visualizer is running, or something else is using port 8790. Close the other process or change `port` in `kimi-visualizer.json`.
