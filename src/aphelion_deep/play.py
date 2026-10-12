"""Local player interface. Run from the game workspace: python -m aphelion_deep.play."""
import argparse
from copy import deepcopy
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

from .engine import Blocked
from .interactive import replay


class Session:
    def __init__(self, path, binding):
        self.path, self.binding = Path(path), binding
        self.data = {"version": 1, "binding": binding, "current": "0",
                     "nodes": [{"id": "0", "parent": None, "label": "New expedition", "decision": None}]}
        self.cache = {}
        if self.path.exists():
            self.data = self.validate(json.loads(self.path.read_text(encoding="utf8")))

    def validate(self, data):
        if data.get("version") != 1 or data.get("binding") != self.binding:
            raise Blocked("Saved game uses different source or engine bindings; it cannot run silently against changed rules.")
        nodes = data.get("nodes")
        if not isinstance(nodes, list) or not 1 <= len(nodes) <= 5000:
            raise Blocked("Invalid history length")
        seen = set()
        for i, node in enumerate(nodes):
            if node.get("id") != str(i) or (i == 0 and (node.get("parent") is not None or node.get("decision") is not None)) or (i and node.get("parent") not in seen):
                raise Blocked("Invalid history tree")
            if i and (not isinstance(node.get("decision"), dict) or set(node["decision"]) != {"key", "value"}):
                raise Blocked("Invalid decision")
            seen.add(node["id"])
        if data.get("current") not in seen:
            raise Blocked("Unknown selected history point")
        return data

    def decisions(self, node):
        result = []
        while node != "0":
            item = self.data["nodes"][int(node)]
            result.append(item["decision"])
            node = item["parent"]
        return list(reversed(result))

    def result(self, node):
        if node not in {n["id"] for n in self.data["nodes"]}:
            raise Blocked("Unknown history point")
        if node not in self.cache:
            self.cache[node] = replay(self.decisions(node))
            if len(self.cache) > 128:
                del self.cache[next(iter(self.cache))]
        return self.cache[node]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf8")
        temporary.replace(self.path)

    def view(self):
        node = self.data["current"]
        item = self.data["nodes"][int(node)]
        previous = self.result(item["parent"]) if item["parent"] is not None else None
        result = self.result(node)
        event_start = len(previous["events"]) if previous else 0
        return {**deepcopy(result), "current": node, "history": deepcopy(self.data["nodes"]),
                "previous_state": previous["state"] if previous else None,
                "recent_events": result["events"][event_start:],
                "saved_path": str(self.path)}

    def act(self, node, key, value):
        if node != self.data["current"]:
            raise Blocked("This page is out of date. Reload before choosing an action.")
        prompt = self.result(node)["prompt"]
        option = next((o for o in prompt["options"] if o["value"] == value), None) if prompt else None
        if not prompt or key != prompt["key"] or option is None:
            raise Blocked("Action is unavailable at this history point")
        if len(self.data["nodes"]) >= 5000:
            raise Blocked("History limit reached; export this session and start a new expedition.")
        decision = {"key": key, "value": value}
        result = replay(self.decisions(node) + [decision])
        new_id = str(len(self.data["nodes"]))
        self.data["nodes"].append({"id": new_id, "parent": node,
                                   "label": prompt["title"] + " — " + option["label"], "decision": decision})
        self.data["current"] = new_id
        self.cache[new_id] = result
        if len(self.cache) > 128:
            del self.cache[next(iter(self.cache))]
        self.save()

    def checkout(self, node):
        self.result(node)
        self.data["current"] = node
        self.save()


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
