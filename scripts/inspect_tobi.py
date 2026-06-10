"""Full F0 trace per word + rise/fall metrics in semitones, for ToBI audit."""
import json
import math
from pathlib import Path

d = json.loads((Path(__file__).resolve().parent.parent / "assets" / "speech-data.json").read_text(encoding="utf-8"))
P = d["pitch"]
W = d["words"]

def st(a, b):
    return 12 * math.log2(b / a)

for i, w in enumerate(W):
    pts = [p for p in P if w["t0"] - 0.02 <= p[0] <= w["t1"] + 0.02]
    if not pts:
        print(f"{i:2d} {w['w']:<11} (no voiced frames)")
        continue
    trace = " ".join(str(p[1]) for p in pts)
    mx = max(pts, key=lambda p: p[1])
    mn = min(pts, key=lambda p: p[1])
    # rise into the peak: min before peak time -> peak
    before = [p for p in pts if p[0] <= mx[0]]
    pre_min = min(before, key=lambda p: p[1]) if before else mx
    # also look 100 ms before word onset for a leading low/high
    lead = [p for p in P if w["t0"] - 0.12 <= p[0] < w["t0"]]
    lead_s = f" lead={lead[-1][1]}" if lead else ""
    rel = (mx[0] - w["t0"]) / max(w["t1"] - w["t0"], 1e-6)
    print(f"{i:2d} {w['w']:<11} peak {mx[1]}@{rel:.0%} of word, rise {st(pre_min[1], mx[1]):+.1f}st "
          f"(from {pre_min[1]}), fall-after {st(mx[1], pts[-1][1]):+.1f}st{lead_s}")
    print(f"     {trace}")
