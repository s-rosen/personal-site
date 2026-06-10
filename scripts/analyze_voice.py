"""Analyze the voice intro WAV into JSON for the site's Praat-style figure.

Outputs assets/speech-data.json with:
  - broadband spectrogram (dB, quantized uint8, base64)
  - formant tracks F1-F3 (Burg), filtered to high-intensity frames
  - pitch contour (autocorrelation)
  - word intervals from faster-whisper, paired with a hand-written IPA tier

Run:  uv run --no-project --with praat-parselmouth --with faster-whisper python scripts/analyze_voice.py
"""
import base64
import json
import math
from pathlib import Path

import numpy as np
import parselmouth

ROOT = Path(__file__).resolve().parent.parent
WAV = ROOT / "assets" / "voice-intro.wav"
OUT = ROOT / "assets" / "speech-data.json"

# Hand-written broad IPA (GenAm), one entry per spoken word, in order.
IPA = [
    ("Hi", "haɪ"),
    ("I'm", "aɪm"),
    ("Simon", "ˈsaɪmən"),
    ("Rosen", "ˈɹoʊzən"),
    ("I'm", "aɪm"),
    ("a", "ə"),
    ("linguist", "ˈlɪŋɡwɪst"),
    ("who", "hu"),
    ("is", "ɪz"),
    ("interested", "ˈɪntɹəstɪd"),
    ("in", "ɪn"),
    ("solving", "ˈsɑlvɪŋ"),
    ("the", "ði"),
    ("uncanny", "ʌnˈkæni"),
    ("valley", "ˈvæli"),
    ("in", "ɪn"),
    ("synthetic", "sɪnˈθɛtɪk"),
    ("speech", "spitʃ"),
    ("and", "ænd"),
    ("making", "ˈmeɪkɪŋ"),
    ("our", "aʊɚ"),
    ("voice", "vɔɪs"),
    ("agents", "ˈeɪdʒənts"),
    ("more", "mɔɹ"),
    ("reliable", "ɹɪˈlaɪəbəl"),
]

snd = parselmouth.Sound(str(WAV))
dur = snd.get_total_duration()
print(f"duration: {dur:.3f}s")

# ---------- spectrogram (Praat broadband: 5 ms Gaussian window) ----------
FMAX = 5000.0
spec = snd.to_spectrogram(window_length=0.005, maximum_frequency=FMAX,
                          time_step=0.008, frequency_step=62.5)
S = 10 * np.log10(np.maximum(spec.values, 1e-12))  # bins x frames
top = S.max()
DYN = 60.0  # dB dynamic range, Praat default-ish
S = np.clip((S - (top - DYN)) / DYN, 0, 1)
q = (S * 255).astype(np.uint8)  # bins x frames
bins, frames = q.shape
print(f"spectrogram: {bins} bins x {frames} frames")
spec_b64 = base64.b64encode(q.T.tobytes()).decode("ascii")  # frame-major

# ---------- intensity (to filter formant speckles in silence) ----------
intensity = snd.to_intensity(minimum_pitch=75)
def intens_at(t):
    v = intensity.get_value(t)
    return v if v is not None and not math.isnan(v) else -200.0
imax = max(intens_at(t) for t in np.arange(0.05, dur - 0.05, 0.01))

# ---------- formants (Burg) ----------
fmt = snd.to_formant_burg(time_step=0.01, max_number_of_formants=5,
                          maximum_formant=5000.0)
formants = []
for t in np.arange(0.02, dur - 0.02, 0.01):
    if intens_at(t) < imax - 28:
        continue
    row = [round(float(t), 3)]
    ok = True
    for i in (1, 2, 3):
        f = fmt.get_value_at_time(i, t)
        if f is None or math.isnan(f) or f > FMAX:
            ok = False
            break
        row.append(int(round(f)))
    if ok:
        formants.append(row)
print(f"formant points: {len(formants)}")

# ---------- pitch ----------
pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=400)
f0 = []
for t in np.arange(0.02, dur - 0.02, 0.01):
    v = pitch.get_value_at_time(t)
    if v is not None and not math.isnan(v) and v > 0:
        f0.append([round(float(t), 3), int(round(v))])
print(f"pitch points: {len(f0)}")

# ---------- word alignment ----------
from faster_whisper import WhisperModel
model = WhisperModel("base.en", device="cpu", compute_type="int8")
segments, _ = model.transcribe(str(WAV), word_timestamps=True)
heard = []
for seg in segments:
    for w in seg.words:
        heard.append({"w": w.word.strip(), "t0": round(w.start, 3), "t1": round(w.end, 3)})
print("whisper words:", [w["w"] for w in heard])

def norm(s):
    return "".join(c for c in s.lower() if c.isalpha() or c == "'")

words = []
if len(heard) == len(IPA) and all(norm(h["w"]) == norm(g[0]) for h, g in zip(heard, IPA)):
    for h, (g, ipa) in zip(heard, IPA):
        words.append({"w": g, "ipa": ipa, "t0": h["t0"], "t1": h["t1"]})
    print("alignment: exact 1:1 match")
else:
    # sequential best-effort match; flag for manual review
    print("alignment: MISMATCH - whisper heard different words, review needed")
    hi = 0
    for g, ipa in IPA:
        while hi < len(heard) and norm(heard[hi]["w"]) != norm(g):
            hi += 1
        if hi < len(heard):
            words.append({"w": g, "ipa": ipa, "t0": heard[hi]["t0"], "t1": heard[hi]["t1"]})
            hi += 1
    print(f"matched {len(words)}/{len(IPA)} words")

out = {
    "duration": round(dur, 3),
    "fmax": FMAX,
    "spec": {"bins": bins, "frames": frames, "tStep": 0.008, "t0": spec.x1, "b64": spec_b64},
    "formants": formants,
    "pitch": f0,
    "pitchRange": [75, 400],
    "words": words,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB)")
