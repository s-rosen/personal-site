"""Diff the working speech-data.json against the last committed version."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
old = json.loads(subprocess.run(
    ["git", "-C", str(ROOT), "show", "HEAD:assets/speech-data.json"],
    capture_output=True, text=True, encoding="utf-8").stdout)
new = json.loads((ROOT / "assets" / "speech-data.json").read_text(encoding="utf-8"))

print("=== WORD CHANGES ===")
n = 0
for a, b in zip(old["words"], new["words"]):
    if a != b:
        n += 1
        d0 = (b["t0"] - a["t0"]) * 1000
        d1 = (b["t1"] - a["t1"]) * 1000
        print(f"{b['w']:<12} t0 {a['t0']:.3f}->{b['t0']:.3f} ({d0:+.0f} ms)   "
              f"t1 {a['t1']:.3f}->{b['t1']:.3f} ({d1:+.0f} ms)")
print(f"({n} of {len(new['words'])} words changed)" if n else "no word changes")

print()
print("=== TOBI CHANGES ===")
oldt = {tuple(e) for e in old["tobi"]}
newt = {tuple(e) for e in new["tobi"]}
changed = False
for e in sorted(oldt - newt):
    print(f"removed: {e[0]:6.3f}  {e[1]}")
    changed = True
for e in sorted(newt - oldt):
    print(f"added:   {e[0]:6.3f}  {e[1]}")
    changed = True
if not changed:
    print("no tobi changes")

# sanity checks on the new data
print()
print("=== SANITY ===")
issues = []
W = new["words"]
for i, w in enumerate(W):
    if w["t1"] - w["t0"] < 0.02:
        issues.append(f"word '{w['w']}' is only {(w['t1']-w['t0'])*1000:.0f} ms")
    if i and w["t0"] < W[i-1]["t1"] - 0.001:
        issues.append(f"'{W[i-1]['w']}' and '{w['w']}' overlap")
VALID = {"H*", "L*", "L+H*", "L*+H", "H+!H*", "!H*", "L+!H*", "L*+!H",
         "H-", "L-", "!H-", "L-L%", "L-H%", "H-H%", "H-L%", "!H-L%", "%H", "%h", "HiF0"}
for t, lab in new["tobi"]:
    if lab not in VALID:
        issues.append(f"nonstandard label '{lab}' @ {t:.3f}s")
    if not (0 <= t <= new["duration"]):
        issues.append(f"tobi event out of range @ {t}")
starred = [e for e in new["tobi"] if "*" in e[1]]
for t, lab in starred:
    inside = any(w["t0"] - 0.01 <= t <= w["t1"] + 0.01 for w in W)
    if not inside:
        issues.append(f"accent {lab} @ {t:.3f}s falls in a gap between words")
print("\n".join(issues) if issues else "all checks pass")
