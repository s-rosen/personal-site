"""Write a Praat TextGrid (words tier) from speech-data.json for AuToBI etc."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "assets" / "speech-data.json").read_text(encoding="utf-8"))
W = d["words"]
dur = d["duration"]

# build a gapless interval sequence (TextGrid needs full coverage)
ivs = []
cur = 0.0
for w in W:
    if w["t0"] > cur + 1e-4:
        ivs.append((cur, w["t0"], ""))
    ivs.append((w["t0"], w["t1"], w["w"]))
    cur = w["t1"]
if cur < dur - 1e-4:
    ivs.append((cur, dur, ""))

out = []
out.append('File type = "ooTextFile"')
out.append('Object class = "TextGrid"')
out.append("")
out.append("xmin = 0")
out.append(f"xmax = {dur}")
out.append("tiers? <exists>")
out.append("size = 1")
out.append("item []:")
out.append("    item [1]:")
out.append('        class = "IntervalTier"')
out.append('        name = "words"')
out.append("        xmin = 0")
out.append(f"        xmax = {dur}")
out.append(f"        intervals: size = {len(ivs)}")
for i, (a, b, t) in enumerate(ivs, 1):
    out.append(f"        intervals [{i}]:")
    out.append(f"            xmin = {a}")
    out.append(f"            xmax = {b}")
    out.append(f'            text = "{t}"')

target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tools" / "autobi" / "voice-intro.TextGrid"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"wrote {target} ({len(ivs)} intervals)")
