# Troubleshooting

## The page says "no hand" even though my hand is in frame

- Make sure you are in a well-lit room.
- Move your hand slowly into the center of the frame.
- MediaPipe needs a clear view of your fingers.

## Gestures flicker

The board waits 200ms before committing a gesture change to reduce jitter. Hold the gesture steady.

## Camera permission denied

Check your browser's site permissions and allow camera access. The camera never leaves your machine.

## The agent doesn't see gestures

Check that `kimi-barehands.json` has the same `state_dir` as `kimi-voice/kimi-voice.json`.

## Works only in Chrome

MediaPipe Hands performs best in Chromium-based browsers. Safari and Firefox may have issues.
