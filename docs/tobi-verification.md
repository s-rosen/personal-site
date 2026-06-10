# Automated verification of the hand ToBI transcription

Date: 2026-06-10. Hand tier: 17 events (13 pitch accents, 3 edge tones, 1 %H... 0).
Two independent automatic systems run on `assets/voice-intro.wav`:

- **AuToBI 1.5.1** (Rosenberg) with BURNC/BDC/Games models, recovered via the
  Internet Archive (`tools/autobi/`, gitignored). Java; word boundaries supplied
  from the hand-corrected tier via `scripts/make_textgrid.py`.
- **Wav2ToBI** (Zhai & Cole, Interspeech 2023), checkpoints
  `ReginaZ/Wav2ToBI-PA-Fuzzy` and `ReginaZ/Wav2ToBI-PB-Fuzzy` from HuggingFace,
  run via `tools/wav2tobi/run_one.py` (bypasses the deprecated datasets audio
  pipeline). Comparison: `scripts/compare_auto.py`.

## Phrasing — confirmed twice, independently

| Hand tier | AuToBI | Wav2ToBI |
|---|---|---|
| L-L% @ 1.523 (Rosen) | break 4 @ 1.523, L-L% | boundary @ 1.48 |
| L-L% @ 6.185 (speech) | break 4 @ 6.185, L-L% | boundary @ 6.18 |
| L-L% @ 8.996 (reliable) | break 4 @ 8.996, L-L% | boundary @ 8.90 |

No other IP boundaries detected by either system. Wav2ToBI additionally
suggests *intermediate*-strength boundaries after "linguist" (2.66) and
"agents" (8.10). Notably, the transcriber originally placed an L- after
"linguist" and deleted it on relistening — the model hears it too.

## Pitch accents — Wav2ToBI agrees on 22/25 words

(AuToBI's accent models produced degenerate output — every word accented,
all H* — and were discarded. Type labels below are the hand tier's; Wav2ToBI
detects accent presence only.)

Agreed accented (12): Hi, Simon, Rosen, linguist, interested, solving,
uncanny, valley, synthetic, making, voice, reliable.
Agreed unaccented (10): I'm(1), a, who, is, in(both), the, and, our, more.

Disagreements:

1. **"I'm" (2.04, IP2-initial)** — model hears prominence; hand tier has it
   unaccented (the perceived high judged to arrive on "a"). Relisten candidate.
2. **"speech" (5.88)** — model hears an accent; hand tier deaccents it, making
   "synthetic" nuclear. Strongest relisten candidate (the first-draft analysis
   also had H* here).
3. **"agents" L* missed by the model** — expected failure mode: acoustic
   detectors are trained mostly on H-type prominence and systematically miss
   low accents. The hand L* is supported by a below-interpolation dip to 90 Hz
   on stressed AY-. Keep.

## Resolution (relisten, same day)

1. **"I'm" accepted as prominent** — relabeled the IP2 opening as `L*+H` on
   "I'm" (low star, rise) with the trailing H realized on "a"; "linguist"
   therefore simplifies from `H+!H*` to `!H*`. Encodes the transcriber's
   perceived levels: I'm 1↗3, a 3, linguist 2.
2. **"speech" accepted as accented** — `!H*`, a downstep below synthetic's
   `L+H*` (vowel ~105–116 Hz, well above the range floor), nuclear in IP2.
3. **"agents" `L*` retained** — the model's miss is its known blind spot for
   low accents.

Final tier: 19 events. Both adopted changes were corroborated by Wav2ToBI's
prominence detections (2.04 s, 5.88 s).

## Calibration context

Human inter-transcriber agreement on ToBI: ~80% accent presence, 60–70%
accent type. 22/25 (88%) presence agreement with a model whose published F1
is ~0.79 means the hand tier is at or above the consistency ceiling the task
allows. Tone *types* remain verified only by the transcriber's ear plus the
F0 reasoning recorded in `scripts/analyze_voice.py`.

## Reproduction

```
# AuToBI (Java 21, jars/models in tools/autobi/)
python scripts/make_textgrid.py
java -jar tools/autobi/AuToBI-1.5.1.jar -input_file=tools/autobi/voice-intro.TextGrid \
  -wav_file=assets/voice-intro.wav ... -out_file=tools/autobi/autobi-out.TextGrid

# Wav2ToBI (venv in tools/wav2tobi/.venv, python 3.14 + torch cpu)
cd tools/wav2tobi
.venv/Scripts/python run_one.py ReginaZ/Wav2ToBI-PA-Fuzzy input/voice-intro-16k.wav pa_results.json
LSTM_HIDDEN=256 .venv/Scripts/python run_one.py ReginaZ/Wav2ToBI-PB-Fuzzy input/voice-intro-16k.wav pb_results.json
python ../../scripts/compare_auto.py pa_results.json accent
python ../../scripts/compare_auto.py pb_results.json boundary
```
