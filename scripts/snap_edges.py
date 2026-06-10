"""Snap final edge tones (…%) to the end boundary of their phrase-final word."""
import json
from pathlib import Path

jp = Path(__file__).resolve().parent.parent / "assets" / "speech-data.json"
d = json.loads(jp.read_text(encoding="utf-8"))
for ev in d["tobi"]:
    if ev[1].endswith("%") and not ev[1].startswith("%"):
        # host = last word starting at or before the event
        host = max((w for w in d["words"] if w["t0"] - 0.01 <= ev[0]), key=lambda w: w["t0"])
        print(f"{ev[1]} {ev[0]:.3f} -> {host['t1']:.3f} (end of '{host['w']}')")
        ev[0] = host["t1"]
d["tobi"].sort(key=lambda e: e[0])
payload = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
jp.write_text(payload, encoding="utf-8")
jp.with_suffix(".js").write_text("window.SPEECH_DATA=" + payload + ";", encoding="utf-8")
print("done")
