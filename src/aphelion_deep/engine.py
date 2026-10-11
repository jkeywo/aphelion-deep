"""Strict ordered-deck tutorial interpreter. All decisions come from the script.

The closed handlers below are derived from the bound printed faces and approved
amendments. Unsupported branches raise Blocked; there is no fallback policy.
"""

from __future__ import annotations
from copy import deepcopy
from collections import Counter
import json, re, hashlib
from importlib.resources import files

LOCATIONS = {"C": "Crash Flats", "R": "Reef Gardens", "K": "Kelp Cathedral"}


class Blocked(ValueError):
    pass


def fingerprint(card):
    return hashlib.sha256(
        json.dumps(
            {
                k: card[k]
                for k in (
                    "ID",
                    "Name",
                    "Keywords",
                    "Back Text",
                    "Front Text",
                    "Track Name",
                )
            },
            sort_keys=True,
            ensure_ascii=False,
        ).encode()
    ).hexdigest()


def load_cards():
    return json.loads(
        files("aphelion_deep").joinpath("data/cards.json").read_text(encoding="utf8")
    )


class Engine:
    def __init__(self, script, cards=None):
        self.script = deepcopy(script)
        self.cards = cards or load_cards()
        self.defs = {}
        self.events = []
        self.checkpoints = []
        self.turn = 0
        self.phase = "setup"
        self.used = set()
        self.choices_used = set()
        for c in self.cards:
            prefix = next((k for k, v in LOCATIONS.items() if v == c["Location"]), None)
            if prefix:
                self.defs[prefix + str(c["Source ID"])] = c
        self.state = {
            "locations": {
                k: {
                    "name": v,
                    "deck": sorted(
                        [q for q in self.defs if q[0] == k and q[1:].isdigit()],
                        key=lambda x: int(x[1:]),
                    ),
                    "position": 0,
                    "cards": {},
                    "set_aside": [],
                    "discard": [],
                    "resources": {"Materials": 0, "Coral": 0, "Food": 0, "Biomass": 0},
                    "local_icons": {},
                    "revealed": False,
                    "recipes": [q for q in self.defs if q.startswith(k + "s")],
                }
                for k, v in LOCATIONS.items()
            },
            "players": {
                p: {"hand": [], "at": None, "capabilities": {}}
                for p in ["engineer", "lead", "systems"]
            },
            "reactor": 0,
            "phase": "setup",
            "built": [],
            "card_names": {
                key: {"id": card["ID"], "name": card["Name"]}
                for key, card in self.defs.items()
            },
        }
        self.emit("simulation.started")

    def emit(self, type, keys=(), **data):
        self.refresh()
        self.events.append(
            {
                "turn": self.turn,
                "event_type": type,
                "entity_ids": [self.defs[k]["ID"] for k in keys if k in self.defs],
                "data": data,
            }
        )
        self.checkpoints.append(deepcopy(self.state))

    def need(self, key):
        if key not in self.script["choices"]:
            raise Blocked("Missing script choice: " + key)
        self.choices_used.add(key)
        return self.script["choices"][key]

    def once(self, key):
        key = (self.turn, self.phase, key)
        if key in self.used:
            raise Blocked("Action repeated in phase: " + str(key))
        self.used.add(key)

    def loc(self, l):
        return self.state["locations"][l]

    def people(self, l):
        return [p for p, v in self.state["players"].items() if v["at"] == l]

    def card(self, key):
        return self.loc(key[0])["cards"].get(key)

    def value(self, key):
        return (self.card(key) or {}).get("value", 0)

    def change(self, key, delta):
        c = self.card(key)
        if c is None or "value" not in c:
            raise Blocked("No local track: " + key)
        c["value"] = max(0, min(5, c["value"] + delta))
        if c["value"] == 0 and c["type"] in ("Flora", "Fauna", "Mineral"):
            del self.loc(key[0])["cards"][key]
            self.loc(key[0])["discard"].append(key)

    def keywords(self, key):
        return set(x.strip().lower() for x in self.defs[key]["Keywords"].split(","))

    def has(self, l, word):
        return [k for k in self.loc(l)["cards"] if word.lower() in self.keywords(k)]

    def portable(self, p, crafting=False):
        hand = self.state["players"][p]["hand"]
        ic = Counter()
        for key in hand:
            if key == "C3":
                ic["Power"] += 1
            if key == "R3" or key in ("Cs1", "Rs1"):
                ic["Oxygen"] += 1
            if key in ("R13", "R19", "Cs3"):
                ic["Knowledge"] += 1
            if key == "C13" and crafting:
                ic["Knowledge"] += 2
        return ic

    def icons(self, l, crafting=False):
        ic = Counter(self.loc(l)["local_icons"])
        for p in self.people(l):
            ic.update(self.portable(p, crafting))
        if l == "R":
            if self.value("R10") >= 3:
                ic["Oxygen"] += 1
            if self.value("R16") >= 4:
                ic["Power"] += 1
        if l == "K" and self.loc(l)["revealed"]:
            ic["Oxygen"] += 1
            if self.value("K2") >= 2:
                ic["Oxygen"] += 1
            if self.value("K2") >= 3:
                ic["Pressure"] += 1
            if self.value("K3") >= 2 and any(
                self.value(k) >= 2 for k in self.has(l, "prey")
            ):
                ic["Pressure"] += 1
            if self.card("K5") and self.card("K5").get("flipped"):
                ic["Knowledge"] += int(self.value("K5") >= 3) + int(
                    self.value("K5") >= 5
                )
        if ic["Oxygen"] >= 2:
            ic["Power"] += sum(
                "Rs2" in self.state["players"][p]["hand"] for p in self.people(l)
            )
        return dict(ic)

    def refresh(self):
        self.state["phase"] = self.phase
        for l in LOCATIONS:
            self.loc(l)["capabilities"] = self.icons(l)
        for p in self.state["players"]:
            player = self.state["players"][p]
            player["capabilities"] = dict(self.portable(p))
            if (
                "Rs2" in player["hand"]
                and player["at"]
                and self.icons(player["at"]).get("Oxygen", 0) >= 2
            ):
                player["capabilities"]["Power"] = (
                    player["capabilities"].get("Power", 0) + 1
                )
            player["actions"] = ["Cultivator"] if "R4" in player["hand"] else []
            player["cultivator_used_this_turn"] = (
                "R4" in player["hand"] and ("cultivate", self.turn) in self.used
            )

    def gain(self, key):
        p = self.need(f"{self.turn}:recipient:{key}")
        if p not in self.people(key[0]):
            raise Blocked("Recipient not present: " + key)
        if any(key in x["hand"] for x in self.state["players"].values()):
            raise Blocked("Card already held: " + key)
        self.state["players"][p]["hand"].append(key)
        if key in self.loc(key[0])["set_aside"]:
            self.loc(key[0])["set_aside"].remove(key)
        self.emit("card.gained", [key], recipient=p)

    def gains(self, l):
        eligible = []
        if l == "R":
            if (
                sum(
                    self.value(k) >= 4
                    for k, c in self.loc(l)["cards"].items()
                    if c.get("track") == "Population"
                )
                >= 2
            ):
                eligible.append("R13")
            if self.value("R16") >= 4 and self.value("R18") >= 4:
                eligible.append("R19")
        if l == "C" and len(self.loc(l)["recipes"]) >= 3:
            eligible.append("C13")
        if l == "K" and self.value("K2") >= 5 and self.value("K3") >= 5:
            eligible.append("K7")
        for key in eligible:
            if key in self.loc(l)["set_aside"]:
                self.gain(key)

    def gate(self, key, requirements):
        available = self.icons(key[0])
        met = all(available.get(k, 0) >= v for k, v in requirements.items())
        self.emit(
            "exploration.gate",
            [key],
            requirements=requirements,
            available=available,
            open=met,
        )
        return met

    def cultivate(self, l):
        if self.phase != "Exploration":
            raise Blocked("Cultivator requires Exploration")
        choice = self.need(f"{self.turn}:cultivate")
        if choice is None:
            return
        if choice[0] != l or not self.card(choice):
            return
        if ("cultivate", self.turn) in self.used:
            return
        if (
            "systems" not in self.people(l)
            or "R4" not in self.state["players"]["systems"]["hand"]
            or "flora" not in self.keywords(choice)
        ):
            raise Blocked("Illegal cultivation target")
        self.used.add(("cultivate", self.turn))
        self.change(choice, 1)
        self.emit("player.cultivated", [choice, "R4"], actor="systems")

    def explore(self, l):
        loc = self.loc(l)
        if not self.people(l):
            raise Blocked("Exploration requires players")
        if l == "K" and "K6" in loc["set_aside"]:
            for k in self.has(l, "flora"):
                if "kelp" in self.keywords(k):
                    self.change(k, 1)
            loc["set_aside"].remove("K6")
            loc["discard"].append("K6")
            self.emit("event.bloom", ["K6"])
        self.cultivate(l)
        self.gains(l)
        while loc["position"] < len(loc["deck"]):
            key = loc["deck"][loc["position"]]
            c = self.defs[key]
            kind = c["Card Type"]
            requirements = {
                "R15": {"Oxygen": 2, "Knowledge": 2},
                "C15": {"Oxygen": 1, "Power": 3},
                "K1": {"Oxygen": 2},
            }.get(key)
            if requirements and not self.gate(key, requirements):
                return
            loc["position"] += 1
            if c["Track Name"]:
                match = re.search(
                    r"set (?:its |the )?(?:population|abundance|rations) track to (\d)",
                    c["Back Text"],
                    re.I,
                )
                if key == "K5":
                    loc["set_aside"].append(key)
                elif not match:
                    raise Blocked("Unsupported track setup " + key)
                else:
                    loc["cards"][key] = {
                        "id": c["ID"],
                        "name": c["Name"],
                        "type": kind,
                        "track": c["Track Name"].split()[0],
                        "value": int(match[1]),
                    }
                    if key in ("R9", "C9"):
                        loc["revealed"] = True
            elif key in ("C3", "R3", "R4", "R21"):
                self.gain(key)
            elif key in ("R13", "R19", "C13", "K6", "K7"):
                loc["set_aside"].append(key)
            elif key in ("C14", "R14", "K8"):
                option = self.need(f"{self.turn}:dilemma:{key}")
                if key == "C14" and option == "Restart":
                    loc["local_icons"]["Power"] = loc["local_icons"].get("Power", 0) + 2
                    self.state["reactor"] += 1
                elif key == "R14" and option == "Protect":
                    self.change("R10", 2)
                    self.change("R11", 2)
                elif key == "K8" and option == "Cut it free":
                    self.change("K2", 2)
                    loc["resources"]["Materials"] += 1
                else:
                    raise Blocked(
                        "Unsupported dilemma outcome: " + key + " " + str(option)
                    )
                loc["discard"].append(key)
                self.emit("dilemma.resolved", [key], choice=option)
            elif key == "K1":
                loc["revealed"] = True
                loc["cards"][key] = {
                    "id": c["ID"],
                    "name": c["Name"],
                    "type": "Location",
                }
            elif key == "R20":
                loc["cards"][key] = {"id": c["ID"], "name": c["Name"], "type": "Event"}
            elif key in ("R1", "R2", "R8", "C1", "C2", "C8", "R15", "C15"):
                loc["discard"].append(key)
            else:
                raise Blocked("Unsupported reveal: " + key)
            self.emit("card.revealed", [key], location=l, deck_position=loc["position"])
            self.cultivate(l)
            self.gains(l)

    def feed(self, key, word, amount, gain, loss):
        candidates = self.need(f"{self.turn}:feed:{key}")
        if not isinstance(candidates, list) or len(candidates) != len(set(candidates)):
            raise Blocked("Feeding requires ordered unique targets")
        for k in candidates:
            if k == key or k not in self.has(key[0], word):
                raise Blocked("Illegal feeding target: " + k)
        if sum(self.value(k) for k in candidates) < amount:
            if sum(self.value(k) for k in self.has(key[0], word) if k != key) >= amount:
                raise Blocked("Feeding choice omits available full payment")
            self.change(key, -loss)
            self.emit("ecosystem.starved", [key], required=amount, consumed=0)
            return
        remaining = amount
        for k in candidates:
            n = min(remaining, self.value(k))
            self.change(k, -n)
            remaining -= n
            if not remaining:
                break
        self.change(key, gain)
        self.emit("ecosystem.fed", [key, *candidates], amount=amount)

    def conversion(self, key, multiplier=1):
        choice = self.need(f"{self.turn}:convert:{key}")
        if choice == "grow" and key == "R12":
            self.change(key, 1)
            return
        if (
            not isinstance(choice, dict)
            or set(choice) - {"Materials", "Coral"}
            or any(type(x) != int or x < 0 for x in choice.values())
        ):
            raise Blocked("Invalid conversion")
        amount = sum(choice.values())
        if key == "C12" and "Coral" in choice:
            raise Blocked("Wreckage cannot produce Coral")
        if amount > self.value(key):
            raise Blocked("Insufficient abundance")
        self.change(key, -amount)
        for resource, n in choice.items():
            self.loc(key[0])["resources"][resource] += n * multiplier

    def rations(self, key):
        l = key[0]
        if key == "R9":
            self.change(key, self.icons(l).get("Power", 0))
        if key == "K1":
            self.loc(l)["resources"]["Biomass"] = 1
        for p in self.people(l):
            choice = self.need(f"{self.turn}:eat:{p}")
            if choice == "Food icon":
                if not self.icons(l).get("Food", 0):
                    raise Blocked("No Food icon available")
            elif choice == key and key != "K1":
                if self.value(key) < 1:
                    raise Blocked("Rations exhausted")
                self.change(key, -1)
            elif choice in self.has(l, "flora") and self.value(choice) > 0:
                self.change(choice, -1)
            else:
                raise Blocked("Invalid ration choice for " + p)
            self.emit("player.ate", [key, choice], actor=p, payment=choice)

    def upkeep_card(self, key):
        if not self.card(key):
            raise Blocked("Upkeep target absent: " + key)
        n = self.value(key)
        l = key[0]
        res = self.loc(l)["resources"]
        reactor = self.state["reactor"]
        if key in ("R9", "C9", "K1"):
            self.rations(key)
        elif key == "R10":
            self.change(key, 1 if n == 1 else 2 if 2 <= n <= 4 else 0)
        elif key in ("R11", "C11"):
            if key == "C11":
                if n >= 3 and any(
                    self.value(k) >= 3
                    for k in self.has(l, "wreckage")
                    if self.card(k).get("track") == "Abundance"
                ):
                    res["Materials"] += 1
                if not any(
                    self.value(k) >= 2
                    for k in self.has(l, "wreckage")
                    if self.card(k).get("track") == "Abundance"
                ):
                    self.change(key, -1)
            n = self.value(key)
            if n:
                self.feed(
                    key,
                    "flora" if key == "R11" else "fauna",
                    1 if n <= 2 else 2 if n <= 4 else 3,
                    1 if n <= 2 else 2 if n <= 4 else 0,
                    1 if n <= 2 else 2,
                )
        elif key == "R12":
            self.conversion(key)
        elif key == "C12":
            self.conversion(key, 2)
        elif key == "C10":
            if n >= 2:
                res["Materials"] += 1
            if n >= 4:
                res["Food"] += 1
            if any(
                self.value(k) >= 3
                for k in self.has(l, "wreckage")
                if self.card(k).get("track") == "Abundance"
            ):
                self.change(key, 1)
            if not self.has(l, "wreckage"):
                self.change(key, -1)
        elif key == "R16":
            if self.value("R18") >= 2:
                self.change(key, 1)
            if reactor >= 2:
                self.change(key, -1)
        elif key == "R17":
            if n:
                self.feed(key, "prey", 1 if n <= 3 else 2, 1, 1)
        elif key == "R18":
            if n >= 2:
                res["Materials"] += 1
            if self.value("R16") >= 4:
                self.change(key, 1)
            if reactor >= 3:
                self.change(key, -1)
        elif key == "R20":
            affected = [k for k in self.has(l, "fauna") if self.value(k) >= 3]
            for k in affected:
                self.change(k, -1)
            if not affected:
                del self.loc(l)["cards"][key]
                self.loc(l)["discard"].append(key)
        elif key == "K2":
            if self.value("K4") >= 3:
                self.change(key, 1)
            if reactor >= 3:
                self.change(key, -1)
        elif key == "K3":
            if self.value("K2") >= 3:
                self.change(key, 1)
            if not self.has(l, "flora"):
                self.change(key, -1)
        elif key == "K4":
            if self.value("K3") >= 2:
                self.change(key, 1)
            if not self.has(l, "mineral"):
                self.change(key, -1)
        elif key == "K5":
            self.change(key, 1)
        elif key == "Ks4":
            pass  # passive installed Power, no recurring effect
        else:
            raise Blocked("Unsupported mandatory upkeep " + key)
        self.emit("card.upkeep", [key], location=l)

    def craft(self, key, recipient):
        l = key[0]
        loc = self.loc(l)
        if (
            self.phase != "Upkeep"
            or recipient not in self.people(l)
            or key not in loc["recipes"]
            or key in self.state["built"]
        ):
            raise Blocked("Illegal craft " + key)
        self.once("craft:" + key)
        costs = {"Rs1": 1, "Cs1": 1, "Rs2": 2, "Cs3": 0, "Ks4": 3}
        if key not in costs:
            raise Blocked("Unsupported recipe " + key)
        if key == "Cs3" and self.icons(l, True).get("Power", 0) < 3:
            raise Blocked("Craft requires 3 Power")
        cost = max(0, costs[key] - (1 if self.card("C9") and l == "C" else 0))
        if loc["resources"]["Materials"] < cost:
            raise Blocked("Insufficient Materials for " + key)
        loc["resources"]["Materials"] -= cost
        self.state["built"].append(key)
        loc["recipes"].remove(key)
        if key == "Ks4":
            loc["local_icons"]["Power"] = loc["local_icons"].get("Power", 0) + 2
        else:
            self.state["players"][recipient]["hand"].append(key)
        self.emit("player.crafted", [key], actor=recipient, cost={"Materials": cost})

    def run(self):
        turns = self.script.get("turns")
        if not isinstance(turns, list) or len(turns) != 3:
            raise Blocked("Exactly three declared turns are required")
        for number, t in enumerate(turns, 1):
            self.turn = number
            self.phase = "Exploration"
            if set(t) != {
                "assignments",
                "exploration_order",
                "upkeep_order",
                "crafts",
                "optional_actions",
            }:
                raise Blocked("Missing or unsupported turn fields")
            if set(t["assignments"]) != set(self.state["players"]):
                raise Blocked("All players need destinations")
            for p, l in t["assignments"].items():
                if l not in LOCATIONS:
                    raise Blocked("Unsupported location " + str(l))
                self.state["players"][p]["at"] = l
            if len(set(t["exploration_order"])) != len(t["exploration_order"]) or set(
                t["exploration_order"]
            ) != set(t["assignments"].values()):
                raise Blocked("Exploration order must cover each visited location once")
            self.emit("turn.started", assignments=t["assignments"])
            for l in t["exploration_order"]:
                self.explore(l)
            choice = self.need(f"{self.turn}:cultivate")
            if choice is not None and ("cultivate", self.turn) not in self.used:
                raise Blocked("Cultivation choice was not reachable")
            self.phase = "Upkeep"
            required = {l for l in LOCATIONS if self.loc(l)["revealed"]}
            if set(t["upkeep_order"]) != required:
                raise Blocked(
                    "Upkeep must cover every revealed location, including unoccupied locations"
                )
            for l, order in t["upkeep_order"].items():
                expected = set(self.loc(l)["cards"])
                if len(order) != len(set(order)) or set(order) != expected:
                    raise Blocked(
                        f"Upkeep order for {l} must match revealed cards {sorted(expected)}"
                    )
                for key in order:
                    if self.card(key):
                        self.upkeep_card(key)
                    else:
                        self.emit(
                            "card.no_longer_in_play",
                            [key],
                            reason="Removed by earlier mandatory effect this phase",
                        )
            for key, p in t["crafts"]:
                self.craft(key, p)
            # Explicit opt-out for every optional effect outside crafting/conversion.
            required_optional = []
            for p, player in self.state["players"].items():
                for k in player["hand"]:
                    if k in ("R13", "R21", "K7"):
                        required_optional.append(k)
            if "K5" in self.loc("K")["set_aside"]:
                required_optional.append("K5")
            if self.card("R11"):
                required_optional.append("R11:harvest")
            if set(t["optional_actions"]) != set(required_optional):
                raise Blocked(
                    "Explicit optional decisions required: " + str(required_optional)
                )
            for key, action in t["optional_actions"].items():
                if action != "decline":
                    raise Blocked(
                        "Unsupported optional action: " + key + " " + str(action)
                    )
            self.emit("policy.optional_actions", decisions=t["optional_actions"])
            self.emit("turn.completed")
        extra = set(self.script["choices"]) - self.choices_used
        if extra:
            raise Blocked("Unused script choices: " + str(sorted(extra)))
        return self.state
