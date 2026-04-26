"""
assets/generate_tone.py
Generates a simple two-tone alarm WAV so you can run DrowsGuard
without downloading an external sound file.

Usage: python assets/generate_tone.py
Output: assets/alarm.wav
"""

import struct
import wave
import math
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "alarm.wav")

SAMPLE_RATE = 44100
DURATION    = 2.0          # seconds (looped by pygame anyway)
VOLUME      = 0.6          # 0.0 – 1.0
FREQ_A      = 880.0        # Hz — first tone
FREQ_B      = 660.0        # Hz — second tone
BEEP_SECS   = 0.25         # length of each alternating beep


def _sine_samples(freq: float, n_samples: int, rate: int, vol: float) -> list[int]:
    return [
        int(vol * 32767 * math.sin(2 * math.pi * freq * i / rate))
        for i in range(n_samples)
    ]


def generate():
    beep_len = int(SAMPLE_RATE * BEEP_SECS)
    total    = int(SAMPLE_RATE * DURATION)

    samples = []
    t = 0
    toggle = True
    while t < total:
        chunk = min(beep_len, total - t)
        freq  = FREQ_A if toggle else FREQ_B
        samples.extend(_sine_samples(freq, chunk, SAMPLE_RATE, VOLUME))
        t     += chunk
        toggle = not toggle

    with wave.open(OUTPUT, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    print(f"✅  alarm.wav written to {OUTPUT}  ({DURATION}s, {SAMPLE_RATE} Hz)")


if __name__ == "__main__":
    generate()
