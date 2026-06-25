"""Derive the break-index tier from the words + ToBI tiers.

One index per word-end boundary (MAE_ToBI breaks tier):
  4 — where the tones tier has a final edge tone (…%)
  2 — perceived disjuncture without a tonal boundary; the two spots where
      Wav2ToBI heard intermediate-strength boundaries and the hand tier's
      L- was deleted on relistening (docs/tobi-verification.md)
  1 — every other word boundary
"""
import json
from pathlib import Path

DISJUNCTURE_2 = {"linguist", "agents"}

jp = Path(__file__).resolve().parent.parent / "assets" / "speech-data.json"
d = json.loads(jp.read_text(encoding="utf-8"))
edge_times = [ev[0] for ev in d["tobi"] if ev[1].endswith("%") and not ev[1].startswith("%")]

d["breaks"] = []
for w in d["words"]:
    if any(abs(t - w["t1"]) < 0.01 for t in edge_times):
        bi = "4"
    elif w["w"] in DISJUNCTURE_2:
        bi = "2"
    else:
        bi = "1"
    d["breaks"].append([w["t1"], bi])
    print(f"{w['w']:>12} | {bi} @ {w['t1']:.3f}")

payload = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
jp.write_text(payload, encoding="utf-8")
jp.with_suffix(".js").write_text("window.SPEECH_DATA=" + payload + ";", encoding="utf-8")
print("done")
