"""Remove a ToBI event by time+label from speech-data.{json,js}."""
import json
import sys
from pathlib import Path

t, label = float(sys.argv[1]), sys.argv[2]
jp = Path(__file__).resolve().parent.parent / "assets" / "speech-data.json"
d = json.loads(jp.read_text(encoding="utf-8"))
before = len(d["tobi"])
d["tobi"] = [ev for ev in d["tobi"] if not (abs(ev[0] - t) < 0.01 and ev[1] == label)]
print(f"{before} -> {len(d['tobi'])} events")
payload = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
jp.write_text(payload, encoding="utf-8")
jp.with_suffix(".js").write_text("window.SPEECH_DATA=" + payload + ";", encoding="utf-8")
