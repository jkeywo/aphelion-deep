"""Local player interface. Run from the game workspace: python -m aphelion_deep.play."""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

from .engine import Blocked
from .session import Session


def verify_workspace(root):
    from playtrace.models import DesignSnapshot
    from playtrace.simulation import SimulationConfig
    from .plugin import AphelionPlugin
    snapshot_path = root / "provenance/snapshot.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf8"))
    run = AphelionPlugin().run(DesignSnapshot.model_validate(snapshot.get("snapshot", snapshot)),
                              SimulationConfig.model_validate_json((root / "tutorial.json").read_text()), runner="interactive-preflight")
    if run.blockers:
        raise Blocked("Source validation failed: " + "; ".join(b.message for b in run.blockers))
    digest = hashlib.sha256()
    for path in [snapshot_path, Path(__file__).with_name("engine.py"), Path(__file__).with_name("interactive.py"), Path(__file__).with_name("data") / "bindings.json"]:
        digest.update(path.read_bytes())
    return digest.hexdigest()


def make_server(root, session, port):
    token = secrets.token_urlsafe(32)
    manifest = json.loads((root / "reports/cards/manifest.json").read_text(encoding="utf8"))
    allowed_images = {face["path"] for c in manifest["cards"].values() for k, face in c.items() if k in ("front", "back")}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def respond(self, value, status=200, mime="application/json"):
            body = json.dumps(value, ensure_ascii=False).encode() if mime == "application/json" else value
            self.send_response(status)
            self.send_header("Content-Type", mime + ("; charset=utf-8" if mime.startswith("text/") else ""))
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def trusted(self):
            expected = f"127.0.0.1:{self.server.server_port}"
            return self.headers.get("Host") == expected and self.headers.get("Origin", "http://" + expected) == "http://" + expected

        def do_GET(self):
            if not self.trusted():
                return self.respond({"error": "Local origin required"}, 403)
            path = urlsplit(self.path).path
            if path in ("/", "/play.html"):
                return self.respond((root / "reports/play.html").read_bytes(), mime="text/html")
            if path == "/api/state":
                return self.respond({**session.view(), "token": token, "card_images": manifest["cards"]})
            if path == "/api/export":
                return self.respond(session.data)
            if path.startswith("/cards/") and path[7:] in allowed_images:
                return self.respond((root / "reports/cards" / path[7:]).read_bytes(), mime="image/webp")
            self.respond({"error": "Not found"}, 404)

        def do_POST(self):
            if not self.trusted() or self.headers.get("X-Play-Token") != token:
                return self.respond({"error": "Local session token required"}, 403)
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2_000_000:
                    raise Blocked("Invalid request size")
                data = json.loads(self.rfile.read(length))
                if self.path == "/api/action":
                    session.act(data["node"], data["key"], data["value"])
                elif self.path == "/api/checkout":
                    session.checkout(data["node"])
                else:
                    raise Blocked("Unknown action")
                self.respond({**session.view(), "token": token, "card_images": manifest["cards"]})
            except (Blocked, ValueError, KeyError, TypeError) as exc:
                self.respond({"error": str(exc)}, 400)

    return HTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--session", type=Path, help="Use a separate save file or a downloaded history JSON")
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    session = Session(args.session or root / ".playtrace/player-session.json", verify_workspace(root))
    session.view()
    server = make_server(root, session, args.port)
    url = f"http://127.0.0.1:{server.server_port}/play.html"
    print("Play The Aphelion Deep: " + url, flush=True)
    print("Autosave: " + str(session.path), flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
