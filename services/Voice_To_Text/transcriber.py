import io
import wave
import collections
import sounddevice as sd
import numpy as np
import webrtcvad
from faster_whisper import WhisperModel

# ── Config ───────────────────────────────────────────────────
SAMPLE_RATE    = 16000
CHUNK_MS       = 30        # VAD frame size — must be 10, 20, or 30ms
CHUNK_SIZE     = int(SAMPLE_RATE * CHUNK_MS / 1000)
VAD_AGGRESSION = 2         # 0–3  (higher = less sensitive to silence)
SILENCE_CHUNKS = 30        # ~900ms of silence triggers transcription
MODEL_SIZE     = "small"   # tiny | base | small | medium
LANGUAGE       = "en"      # e.g. "en", "hi", "ne", "fr" — or None for auto-detect
# ─────────────────────────────────────────────────────────────

print("Loading Whisper model... (first run downloads the model weights)")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print("Model ready. Speak — press Ctrl+C to stop.\n")

vad           = webrtcvad.Vad(VAD_AGGRESSION)
ring_buffer   = collections.deque(maxlen=SILENCE_CHUNKS)
voiced_frames = []
triggered     = False


def frames_to_wav_bytes(frames):
    """Convert a list of raw PCM frames to an in-memory WAV file."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # int16 = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(frames))
    buf.seek(0)
    return buf


def audio_callback(indata, frames, time, status):
    global triggered, voiced_frames

    frame = bytes(indata)
    is_speech = vad.is_speech(frame, SAMPLE_RATE)

    if not triggered:
        # Accumulate in ring buffer, wait for enough voiced frames
        ring_buffer.append((frame, is_speech))
        num_voiced = sum(1 for _, s in ring_buffer if s)
        if num_voiced > 0.6 * ring_buffer.maxlen:
            triggered = True
            voiced_frames.extend(f for f, _ in ring_buffer)
            ring_buffer.clear()
    else:
        voiced_frames.append(frame)
        ring_buffer.append((frame, is_speech))
        num_unvoiced = sum(1 for _, s in ring_buffer if not s)
        if num_unvoiced > 0.9 * ring_buffer.maxlen:
            # Silence detected — transcribe the captured utterance
            triggered = False
            wav_buf = frames_to_wav_bytes(voiced_frames)
            segments, _ = model.transcribe(
                wav_buf,
                language=LANGUAGE,
                beam_size=5,
                vad_filter=True,        # whisper's built-in VAD as extra filter
            )
            text = " ".join(s.text.strip() for s in segments)
            if text:
                print(f"  {text}")
            voiced_frames.clear()
            ring_buffer.clear()


with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    blocksize=CHUNK_SIZE,
    callback=audio_callback,
):
    try:
        while True:
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\nStopped.")
        