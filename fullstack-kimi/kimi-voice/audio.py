# fullstack-kimi voice bridge: audio recording and playback.

import io
import threading
import wave
from pathlib import Path

import numpy as np

BUFFER = []
LOCK = threading.Lock()
RECORDING = False
RATE = 16000
CHANNELS = 1


def _callback(indata, frames, time_info, status):
    with LOCK:
        if RECORDING:
            BUFFER.append(indata.copy())


def start_recording():
    global BUFFER, RECORDING
    with LOCK:
        BUFFER = []
        RECORDING = True
    try:
        import sounddevice as sd
        sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype="int16", callback=_callback).start()
    except Exception as exc:
        print(f"[audio input error: {exc}]")


def stop_recording():
    global RECORDING
    with LOCK:
        RECORDING = False
        frames = BUFFER[:]
    if not frames:
        return None
    data = np.concatenate(frames, axis=0)
    wav_path = Path("/tmp/kimi_voice_input.wav")
    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(data.astype(np.int16).tobytes())
    return wav_path


def current_levels():
    with LOCK:
        if not BUFFER:
            return [0.0] * 16
        recent = BUFFER[-3:] if len(BUFFER) >= 3 else BUFFER
    if not recent:
        return [0.0] * 16
    data = np.concatenate(recent, axis=0).astype(np.float32) / 32768.0
    chunk = len(data) // 16
    if chunk == 0:
        return [0.0] * 16
    levels = []
    for i in range(16):
        frame = data[i * chunk:(i + 1) * chunk]
        levels.append(min(1.0, np.sqrt(np.mean(frame ** 2)) * 4))
    return levels


def play_wav(wav_path):
    try:
        import sounddevice as sd
        import soundfile as sf
        data, rate = sf.read(str(wav_path), dtype="float32")
        sd.play(data, rate)
        sd.wait()
    except Exception as exc:
        print(f"[audio playback error: {exc}]")
