"""Print per-word F0 shape to ground a draft ToBI transcription."""
import json
from pathlib import Path

d = json.loads((Path(__file__).resolve().parent.parent / "assets" / "speech-data.json").read_text(encoding="utf-8"))
P = d["pitch"]
prev_t1 = 0
for i, w in enumerate(d["words"]):
    pts = [p for p in P if w["t0"] <= p[0] <= w["t1"]]
    gap = (w["t0"] - prev_t1) * 1000
    prev_t1 = w["t1"]
    if pts:
        mx = max(pts, key=lambda p: p[1])
        mn = min(pts, key=lambda p: p[1])
        print(f"{i:2d} {w['w']:<11} {w['t0']:.2f}-{w['t1']:.2f} gap={gap:4.0f}ms "
              f"f0 {pts[0][1]}->{pts[-1][1]}  max {mx[1]}@{mx[0]:.2f}  min {mn[1]}")
    else:
        print(f"{i:2d} {w['w']:<11} {w['t0']:.2f}-{w['t1']:.2f} gap={gap:4.0f}ms (no voiced frames)")
