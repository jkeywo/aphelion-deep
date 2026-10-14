"""Shared deterministic history for local and browser hosts."""
from copy import deepcopy
import json
from pathlib import Path
from .engine import Blocked
from .interactive import replay


class Session:
    cache_limit = 128

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
            if len(self.cache) > self.cache_limit:
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
        is_trade = prompt is not None and key == prompt["key"] + ":trade"
        options = prompt.get("trades", []) if is_trade else prompt["options"] if prompt else []
        option = next((o for o in options if o["value"] == value), None)
        if not prompt or (key != prompt["key"] and not is_trade) or option is None:
            raise Blocked("Action is unavailable at this history point")
        if len(self.data["nodes"]) >= 5000:
            raise Blocked("History limit reached; export this session and start a new expedition.")
        decision = {"key": key, "value": value}
        result = replay(self.decisions(node) + [decision])
        new_id = str(len(self.data["nodes"]))
        self.data["nodes"].append({"id": new_id, "parent": node,
                                   "label": ("Trade " + result["state"]["card_names"][value["card"]]["name"] + " — " if is_trade else prompt["title"] + " — ") + option["label"], "decision": decision})
        self.data["current"] = new_id
        self.cache[new_id] = result
        if len(self.cache) > self.cache_limit:
            del self.cache[next(iter(self.cache))]
        self.save()

    def checkout(self, node):
        self.result(node)
        self.data["current"] = node
        self.save()


