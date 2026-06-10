"""Compare automatic prosodic-event predictions against the hand ToBI tier.

Usage: python compare_auto.py <eval_results.json> <accent|boundary>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
results_path, kind = sys.argv[1], sys.argv[2]

d = json.loads((ROOT / "assets" / "speech-data.json").read_text(encoding="utf-8"))
W = d["words"]
res = json.loads(Path(results_path).read_text(encoding="utf-8"))
events = [t for t, _tag in next(iter(res.values()))]

def host_word(t):
    for w in W:
        if w["t0"] - 0.02 <= t <= w["t1"] + 0.02:
            return w["w"], w["t0"]
    return None, None

if kind == "accent":
    mine = {}  # word start -> label, for words I accent
    for t, lab in d["tobi"]:
        if "*" in lab:
            w, wt0 = host_word(t)
            if w:
                mine[wt0] = lab
    model_words = {}
    for t in events:
        w, wt0 = host_word(t)
        if wt0 is not None:
            model_words.setdefault(wt0, []).append(t)
    print(f"model events: {len(events)}  on {len(model_words)} words; my accents: {len(mine)}")
    print(f"{'word':<12} {'mine':<8} {'model':<22} verdict")
    for w in W:
        m = mine.get(w["t0"], "")
        a = model_words.get(w["t0"], [])
        astr = ", ".join(f"{t:.2f}" for t in a)
        verdict = "AGREE" if bool(m) == bool(a) else ("model misses" if m else "model adds")
        if m or a:
            print(f"{w['w']:<12} {m:<8} {astr:<22} {verdict}")
    agree = sum(1 for w in W if bool(mine.get(w['t0'])) == bool(model_words.get(w['t0'])))
    print(f"\nword-level agreement on accent presence: {agree}/{len(W)}")
else:
    mine = [(t, lab) for t, lab in d["tobi"] if lab.endswith("%") or lab.endswith("-")]
    print(f"my edge tones: {[(round(t,3), l) for t, l in mine]}")
    print(f"model boundaries: {[round(t,3) for t in events]}")
    for t, lab in mine:
        near = min(events, key=lambda e: abs(e - t)) if events else None
        if near is not None and abs(near - t) < 0.25:
            print(f"  {lab} @ {t:.3f}  <-> model {near:.3f}  (d={1000*(near-t):+.0f} ms)  AGREE")
        else:
            print(f"  {lab} @ {t:.3f}  no model boundary nearby — model misses")
    for e in events:
        if not any(abs(e - t) < 0.25 for t, _ in mine):
            print(f"  model adds boundary @ {e:.3f}")
