"""Serve the boundary editor and persist corrections back into the site data.

Run:  python scripts/align_server.py
Open: http://localhost:8742/scripts/align-editor.html

POST /save with the corrected words array rewrites assets/speech-data.json
and regenerates assets/speech-data.js (what the site loads).
"""
import json
import http.server
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = 8742


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if self.path != "/save":
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", 0))
        incoming = json.loads(self.rfile.read(n).decode("utf-8"))
        # legacy payload was a bare words list; current is {words, tobi}
        if isinstance(incoming, list):
            words, tobi = incoming, None
        else:
            words, tobi = incoming.get("words"), incoming.get("tobi")
        jp = ROOT / "assets" / "speech-data.json"
        data = json.loads(jp.read_text(encoding="utf-8"))
        if words is not None:
            data["words"] = words
        if tobi is not None:
            data["tobi"] = tobi
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        jp.write_text(payload, encoding="utf-8")
        (ROOT / "assets" / "speech-data.js").write_text(
            "window.SPEECH_DATA=" + payload + ";", encoding="utf-8")
        print(f"saved {len(words or [])} words, {len(tobi or [])} tobi events")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


# Threading is required: browsers hold keep-alive connections (esp. for the
# audio element), which deadlocks a single-threaded server.
with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as srv:
    print(f"editor: http://localhost:{PORT}/scripts/align-editor.html")
    srv.serve_forever()
