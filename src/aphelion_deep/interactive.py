"""Deterministic, resumable decisions over the source-bound tutorial engine."""
from copy import deepcopy
from itertools import permutations, product
from .engine import Engine, Blocked, LOCATIONS, ROLE_OWNERS, DILEMMAS
from .presentation import PLAYER_NAMES


STARTING_LOCATIONS = {"engineer": "C", "lead": "R", "systems": "R"}


class Waiting(Exception):
    pass


class StopExploring(Exception):
    pass


class InteractiveEngine(Engine):
    def __init__(self, decisions):
        self.decisions = decisions
        self.cursor = 0
        self.prompt = None
        super().__init__({"choices": {}})

    def name(self, key):
        return self.defs.get(key, {}).get("Name", key)

    def ask(self, key, title, options, cards=(), note="", **presentation):
        options = [{"label": label, "value": value} for label, value in options]
        while True:
            self.refresh()
            trades = self.trade_options()
            self.prompt = {"key": key, "title": title, "options": options,
                           "cards": list(cards), "note": note, "trades": trades, **presentation}
            if self.cursor == len(self.decisions):
                raise Waiting()
            answer = self.decisions[self.cursor]
            if answer.get("key") == key + ":trade":
                if not any(answer.get("value") == o["value"] for o in trades):
                    raise Blocked("Illegal trade: choose a non-role card in hand and another player here")
                self.trade_card(**answer["value"])
                self.cursor += 1
                continue
            if answer.get("key") != key or not any(answer.get("value") == o["value"] for o in options):
                raise Blocked("Decision no longer matches the available actions: " + key)
            self.cursor += 1
            self.prompt = None
            return deepcopy(answer["value"])

    def trade_options(self):
        if self.phase not in ("Exploration", "Upkeep"):
            return []
        options = []
        for actor, player in self.state["players"].items():
            if not player["at"]:
                continue
            for card in player["hand"]:
                if self.defs[card]["Card Type"] == "Role":
                    continue
                for recipient in self.people(player["at"]):
                    if recipient != actor:
                        options.append({"label": "Give to " + PLAYER_NAMES[recipient],
                                        "value": {"card": card, "actor": actor, "recipient": recipient}})
        return options

    def trade_card(self, card, actor, recipient):
        value = {"card": card, "actor": actor, "recipient": recipient}
        if not any(value == o["value"] for o in self.trade_options()):
            raise Blocked("Illegal trade: choose a non-role card in hand and another player here")
        self.state["players"][actor]["hand"].remove(card)
        self.state["players"][recipient]["hand"].append(card)
        self.emit("card.traded", [card], actor=actor, recipient=recipient,
                  location=self.state["players"][recipient]["at"])

    def take_set_aside(self, key):
        if self.phase != "Exploration" or key not in {"C13", "R13", "R19", "K7"} or key not in self.loc(key[0])["set_aside"] or not self.unlock(key)[0]:
            raise Blocked("Knowledge card is not available to take: " + key)
        self.gain(key)  # Recipient is an explicit decision among players at this site.

    DEFERRED = {"C13", "R13", "R19", "K5", "K6", "K7"}
    GATES = {"R15": {"Oxygen": 2, "Knowledge": 2}, "C15": {"Oxygen": 1, "Power": 3}, "K1": {"Oxygen": 2}}

    def unlock(self, key):
        if key == "C13":
            count = sum("aphelion salvage" in self.keywords(k) for k in self.loc("C")["recipes"])
            return count >= 3, f"Requires 3 Aphelion Salvage recipes here ({count}/3). When ready, choose a player here to take this into their hand."
        if key == "R13":
            count = sum(c.get("track") == "Population" and c.get("value", 0) >= 4 for c in self.loc("R")["cards"].values())
            return count >= 2, f"Requires two cards here with Population 4+ ({count}/2)."
        if key == "R19":
            return self.value("R16") >= 4 and self.value("R18") >= 4, "Requires Glow-Polyp Mat and Echoing Calcite Spires both at 4+."
        if key == "K7":
            return self.value("K2") >= 5 and self.value("K3") >= 5, "Requires Giant Lungweed and Resonating Lure Fish both at Population 5."
        if key == "K5":
            return self.phase == "Upkeep" and self.loc("K")["resources"]["Materials"] >= 2 and bool(self.people("K")), "During Upkeep, spend 2 Materials here to flip and set Scanning to 4."
        return False, "Flips when the next expedition starts here."

    def exploration_actions(self, location):
        options = []
        if ("cultivate", self.turn) not in self.used and any("R4" in self.state["players"][p]["hand"] for p in self.people(location)):
            for actor in self.people(location):
                for target in self.has(location, "flora"):
                    options.append((f"{PLAYER_NAMES[actor]}: cultivate {self.name(target)}", {"action": "cultivate", "card": "R4", "target": target, "actor": actor}))
        for key in self.loc(location)["set_aside"]:
            if key in {"C13", "R13", "R19", "K7"} and self.unlock(key)[0]:
                if self.people(location):
                    options.append(("Take into hand — choose a player", {"action": "take", "card": key}))
        return options

    def table_window(self, location, next_card):
        while True:
            options = ([("Draw the top card", "reveal")] if next_card else []) + [("Finish exploration here", "stop")] + self.exploration_actions(location)
            choice = self.ask(f"{self.turn}:reveal:{next_card or location + '-empty'}", "Explore " + LOCATIONS[location],
                              options, kind="table", location=location)
            if choice in ("reveal", "stop"):
                return choice
            if choice["action"] == "cultivate":
                self.used.add(("cultivate", self.turn))
                self.change(choice["target"], 1)
                self.emit("player.cultivated", [choice["target"], "R4"], actor=choice["actor"])
            elif choice["action"] == "take":
                self.take_set_aside(choice["card"])

    def before_reveal(self, key):
        if self.table_window(key[0], key) == "stop":
            raise StopExploring()
        self.state["drawn_card"] = {"key": key, "face": "back"}
        self.emit("card.drawn", [key])
        if self.defs[key]["Card Type"] == "Phase Reference":
            self.ask(f"{self.turn}:place-reference:{key}", "Put Phase Reference in play",
                     [("Place in play", True)], [key], kind="card-face", face="back",
                     note="Stays here and automatically flips between Exploration and Upkeep.")
            del self.state["drawn_card"]
            return
        if key in self.DEFERRED:
            self.ask(f"{self.turn}:set-aside:{key}", "Set aside " + self.name(key),
                     [("Place beside the deck, back up", True)], [key], kind="card-face", face="back",
                     note=self.unlock(key)[1])
            del self.state["drawn_card"]
            return
        requirements = self.GATES.get(key)
        if requirements and not all(self.icons(key[0]).get(k, 0) >= v for k, v in requirements.items()):
            self.ask(f"{self.turn}:gate:{key}", self.name(key) + " — requirements not met",
                     [("Leave on the deck for a later expedition", True)], [key], kind="card-face", face="back",
                     note="Requires " + ", ".join(f"{v} {k}" for k, v in requirements.items()))
            self.gate(key, requirements)
            del self.state["drawn_card"]
            raise StopExploring()
        self.ask(f"{self.turn}:flip:{key}", "Read the back of " + self.name(key),
                 [("Flip to front", True)], [key], kind="card-face", face="back")
        self.state["drawn_card"]["face"] = "front"
        self.emit("card.flipped", [key])
        label = "Take into " + PLAYER_NAMES[ROLE_OWNERS[key]] + "'s hand" if key in ROLE_OWNERS else "Choose an outcome" if key in DILEMMAS else "Continue with this card"
        self.ask(f"{self.turn}:resolve:{key}", "Read the front of " + self.name(key),
                 [(label, True)], [key], kind="card-face", face="front")
        del self.state["drawn_card"]

    def explore(self, location):
        self.active_location = location
        try:
            super().explore(location)
            if self.loc(location)["position"] == len(self.loc(location)["deck"]):
                self.table_window(location, None)
        except StopExploring:
            pass

    def cultivate(self, location):
        pass  # Players click Cultivator during the exploration action window.

    def gains(self, location):
        pass  # Eligible set-aside cards remain on the table until clicked.

    def activate_drone(self, actor):
        if "K5" not in self.loc("K")["set_aside"] or not self.unlock("K5")[0] or actor not in self.people("K"):
            raise Blocked("Drone requires a present player, Upkeep, and 2 local Materials")
        self.loc("K")["resources"]["Materials"] -= 2
        self.loc("K")["set_aside"].remove("K5")
        c = self.defs["K5"]
        self.loc("K")["cards"]["K5"] = {"id": c["ID"], "name": c["Name"], "type": c["Card Type"], "track": "Scanning", "value": 4, "flipped": True}
        self.emit("card.activated", ["K5"], actor=actor)

    def table_metadata(self):
        result = {}
        for location in LOCATIONS:
            for key, card in self.loc(location)["cards"].items():
                if card["type"] == "Phase Reference":
                    result[key] = {"face": card["face"], "requirement": self.phase + " reference · flips automatically."}
            for key in self.loc(location)["deck"][self.loc(location)["position"]:]:
                result[key] = {"face": "back"}
            for key in self.loc(location)["set_aside"]:
                eligible, requirement = self.unlock(key)
                result[key] = {"face": "back", "requirement": requirement, "eligible": eligible}
            for key in self.loc(location)["recipes"]:
                result[key] = {"face": "back", "requirement": "Craft during Upkeep; costs and requirements apply."}
        if self.state.get("drawn_card"):
            c = self.state["drawn_card"]
            result[c["key"]] = {**result.get(c["key"], {}), "face": c["face"]}
        return {"cards": result, "active_location": getattr(self, "active_location", None)}

    def need(self, key):
        _, kind, subject = key.split(":", 2)
        options = []
        note = ""
        presentation = {}
        cards = [subject] if subject in self.defs else []
        if kind == "recipient" and subject in ROLE_OWNERS:
            recipient = ROLE_OWNERS[subject]
            self.script["choices"][key] = recipient
            self.choices_used.add(key)
            return recipient
        if kind == "recipient":
            title = "Who takes " + self.name(subject) + "?"
            options = [("Give to " + PLAYER_NAMES[p], p) for p in self.people(subject[0])]
            presentation = {"kind": "recipient", "location": subject[0]}
            note = "Choose a player present here. This card goes into their hand."
        elif kind == "dilemma":
            title = "Choose an outcome: " + self.name(subject)
            options = [(c["label"], c["value"]) for c in DILEMMAS[subject] if not c.get("blocked")]
            presentation = {"kind": "dilemma", "choices": deepcopy(DILEMMAS[subject]), "location": subject[0]}
            note = "The players here must agree unanimously. Choose one outcome to apply its consequences."
            self.state["drawn_card"] = {"key": subject, "face": "front"}
        elif kind == "eat":
            location = self.state["players"][subject]["at"]
            title = "Choose food for " + PLAYER_NAMES[subject]
            outpost = {"R": "R9", "C": "C9", "K": "K1"}[location]
            targets = ([outpost] if outpost != "K1" and self.value(outpost) else []) + self.has(location, "flora")
            options = [("Use 1 from " + self.name(k), k) for k in targets if self.value(k)]
            if self.icons(location).get("Food", 0):
                options.append(("Use a Food icon", "Food icon"))
            cards = targets
        elif kind == "convert":
            title = "Choose what to do with " + self.name(subject)
            n = self.value(subject)
            if subject == "R12":
                options.append(("Grow by 1 Abundance", "grow"))
            for materials in range(n + 1):
                for coral in range(n - materials + 1 if subject == "R12" else 1):
                    value = {"Materials": materials}
                    if coral:
                        value["Coral"] = coral
                    label = "Leave unchanged" if not materials + coral else f"Spend {materials + coral} Abundance → {materials * (2 if subject == 'C12' else 1)} Materials, {coral} Coral"
                    options.append((label, value))
        elif kind == "feed":
            title = "Choose feeding order for " + self.name(subject)
            n = self.value(subject)
            word = {"R11": "flora", "C11": "fauna", "R17": "prey"}[subject]
            cost = (1 if n <= 3 else 2) if subject == "R17" else (1 if n <= 2 else 2 if n <= 4 else 3)
            targets = [k for k in self.has(subject[0], word) if k != subject]
            cards += targets
            if sum(self.value(k) for k in targets) < cost:
                options = [("Apply starvation (full feeding cost unavailable)", [])]
            else:
                for size in range(1, len(targets) + 1):
                    for order in permutations(targets, size):
                        if sum(self.value(k) for k in order) >= cost and sum(self.value(k) for k in order[:-1]) < cost:
                            options.append(("Feed from " + " → ".join(self.name(k) for k in order), list(order)))
            note = f"Requires full payment of {cost} Population. Nothing is consumed if the ecosystem cannot pay."
        else:
            raise Blocked("Unsupported decision: " + key)
        if not options:
            raise Blocked(title + ": no legal payment is available. Rewind to an earlier decision.")
        answer = self.ask(key, title, options, cards, note, **presentation)
        if kind == "dilemma":
            del self.state["drawn_card"]
        self.script["choices"][key] = answer
        self.choices_used.add(key)
        return answer

    def assign_players(self, phase):
        locations = [k for k in LOCATIONS if phase == "Exploration" or self.loc(k)["revealed"]]
        if not locations:
            raise Blocked("No revealed site is available for upkeep assignments. Rewind and establish a landing site.")
        players = list(self.state["players"])
        options = []
        for destinations in product(locations, repeat=len(players)):
            assignment = dict(zip(players, destinations))
            label = "; ".join(PLAYER_NAMES[p] + " → " + LOCATIONS[l] for p, l in assignment.items())
            options.append((label, assignment))
        assignments = self.ask(
            f"{self.turn}:assign:{phase}",
            "Assign the expedition" if phase == "Exploration" else "Assign players for upkeep",
            options, kind="assignments", locations=locations,
            initial={p: v["at"] if v["at"] in locations else None for p, v in self.state["players"].items()},
            note="Drag players to sites, then confirm all assignments together. " +
                 ("Every revealed location still resolves upkeep, even with nobody present." if phase == "Upkeep" else "No player moves until you confirm."))
        for p, location in assignments.items():
            self.state["players"][p]["at"] = location
        self.emit("players.assigned", assignments=assignments, phase=phase)
        return assignments

    def play(self):
        for turn in range(1, 4):
            self.turn, self.phase = turn, "Exploration"
            if turn == 1:
                assignments = dict(STARTING_LOCATIONS)
                for p, location in assignments.items():
                    self.state["players"][p]["at"] = location
            else:
                assignments = self.assign_players("Exploration")
            self.emit("turn.started", assignments=assignments)
            remaining = list(dict.fromkeys(assignments.values()))
            while remaining:
                location = self.ask(f"{turn}:explore-order:{len(remaining)}", "Choose the next location to explore",
                                    [(LOCATIONS[k], k) for k in remaining],
                                    note="Fixed landing sites: Fabrication Lead at Crash Flats; both Ecologists at Reef Gardens." if turn == 1 else "")
                remaining.remove(location)
                self.explore(location)
            self.phase = "Upkeep"
            self.assign_players("Upkeep")
            remaining = [k for k in LOCATIONS if self.loc(k)["revealed"]]
            while remaining:
                location = self.ask(f"{turn}:upkeep-location:{len(remaining)}", "Choose the next location for mandatory upkeep",
                                    [(LOCATIONS[k], k) for k in remaining], note="Every revealed location resolves, including unoccupied locations.")
                remaining.remove(location)
                self.active_location = location
                pending = self.upkeep_cards(location)
                while pending:
                    pending = [k for k in pending if self.card(k)]
                    if not pending:
                        break
                    key = self.ask(f"{turn}:upkeep-card:{location}:{len(pending)}", "Resolve upkeep at " + LOCATIONS[location],
                                   [(self.name(k), k) for k in pending], pending)
                    pending.remove(key)
                    self.upkeep_card(key)
            while True:
                options = [("Finish crafting", None)]
                for location in LOCATIONS:
                    for key in self.loc(location)["recipes"]:
                        for p in self.people(location):
                            trial = deepcopy(self)
                            try:
                                trial.craft(key, p)
                            except Blocked:
                                continue
                            cost = trial.events[-1]["data"]["cost"]["Materials"]
                            options.append((f"Craft {self.name(key)} for {PLAYER_NAMES[p]} ({cost} Materials)", [key, p]))
                choice = self.ask(f"{turn}:craft:{len(self.state['built'])}", "Craft equipment", options,
                                  [v[0] if isinstance(v, list) else v["card"] for _, v in options if v], "Click a recipe or set-aside card to use its available Upkeep action.", kind="table-upkeep")
                if choice is None:
                    break
                if isinstance(choice, dict):
                    self.activate_drone(choice["actor"])
                else:
                    self.craft(*choice)
            optional = [k for p in self.state["players"].values() for k in p["hand"] if k in ("R13", "R21", "K7")]
            if self.card("R11"):
                optional.append("R11:harvest")
            for key in optional:
                self.ask(f"{turn}:optional:{key}", "Optional action: " + self.name(key.split(":")[0]),
                         [("Decline this action", "decline")], [key.split(":")[0]],
                         "Executing this optional effect is outside the reviewed tutorial implementation. It cannot be silently applied.")
            self.emit("policy.optional_actions", decisions={k: "decline" for k in optional})
            self.ask(f"{turn}:finish", f"Finish turn {turn}", [("Complete this turn", True)])
            self.emit("turn.completed")
        self.emit("simulation.completed")


def replay(decisions):
    engine = InteractiveEngine(decisions)
    status, error = "playing", None
    try:
        engine.play()
        status = "complete"
    except Waiting:
        pass
    except Blocked as exc:
        status, error = "blocked", str(exc)
        engine.prompt = None
    if engine.cursor != len(decisions):
        raise Blocked("History contains unused or invalid decisions")
    engine.refresh()
    return {"state": engine.state, "turn": engine.turn, "events": engine.events,
            "prompt": engine.prompt, "status": status, "error": error, "table": engine.table_metadata()}
