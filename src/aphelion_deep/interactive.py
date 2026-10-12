"""Deterministic, resumable decisions over the source-bound tutorial engine."""
from copy import deepcopy
from itertools import permutations
from .engine import Engine, Blocked, LOCATIONS
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

    def ask(self, key, title, options, cards=(), note=""):
        options = [{"label": label, "value": value} for label, value in options]
        self.refresh()
        self.prompt = {"key": key, "title": title, "options": options,
                       "cards": list(cards), "note": note}
        if self.cursor == len(self.decisions):
            raise Waiting()
        answer = self.decisions[self.cursor]
        if answer.get("key") != key or not any(answer.get("value") == o["value"] for o in options):
            raise Blocked("Decision no longer matches the available actions: " + key)
        self.cursor += 1
        self.prompt = None
        return deepcopy(answer["value"])

    def before_reveal(self, key):
        answer = self.ask(f"{self.turn}:reveal:{key}", "Explore " + LOCATIONS[key[0]],
                         [("Reveal the next card", "reveal"), ("Finish exploration here", "stop")])
        if answer == "stop":
            raise StopExploring()

    def explore(self, location):
        try:
            super().explore(location)
        except StopExploring:
            pass

    def cultivate(self, location):
        if ("cultivate", self.turn) in self.used:
            return
        holder = next((p for p in self.people(location) if "R4" in self.state["players"][p]["hand"]), None)
        targets = self.has(location, "flora")
        if not holder or not targets:
            return
        target = self.ask(f"{self.turn}:cultivate:{self.loc(location)['position']}",
                          "Use Cultivator now?", [("Keep it available", None)] +
                          [("Cultivate " + self.name(k), k) for k in targets], ["R4", *targets])
        if target:
            self.used.add(("cultivate", self.turn))
            self.change(target, 1)
            self.emit("player.cultivated", [target, "R4"], actor=holder)

    def gains(self, location):
        if self.people(location):
            super().gains(location)

    def gain(self, key):
        if key in self.loc(key[0])["set_aside"]:
            marker = ("offered", self.turn, key)
            if marker in self.used:
                return
            self.used.add(marker)
            if not self.ask(f"{self.turn}:take:{key}", "Take " + self.name(key) + " into a hand?",
                            [("Take the card", True), ("Leave it here this turn", False)], [key]):
                return
        super().gain(key)

    def need(self, key):
        _, kind, subject = key.split(":", 2)
        options = []
        note = ""
        cards = [subject] if subject in self.defs else []
        if kind == "recipient":
            title = "Who takes " + self.name(subject) + "?"
            options = [(PLAYER_NAMES[p], p) for p in self.people(subject[0])]
        elif kind == "dilemma":
            title = "Resolve " + self.name(subject)
            value = {"C14": "Restart", "R14": "Protect", "K8": "Cut it free"}[subject]
            options = [(value, value)]
            note = "Other outcomes are unfinished and are outside this playable slice. Rewind to change the route."
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
        answer = self.ask(key, title, options, cards, note)
        self.script["choices"][key] = answer
        self.choices_used.add(key)
        return answer

    def play(self):
        for turn in range(1, 4):
            self.turn, self.phase = turn, "Exploration"
            assignments = {}
            for p in self.state["players"]:
                assignments[p] = STARTING_LOCATIONS[p] if turn == 1 else self.ask(
                    f"{turn}:move:{p}", "Where will " + PLAYER_NAMES[p] + " go?",
                    [(name, key) for key, name in LOCATIONS.items()])
                self.state["players"][p]["at"] = assignments[p]
            self.emit("turn.started", assignments=assignments)
            remaining = list(dict.fromkeys(assignments.values()))
            while remaining:
                location = self.ask(f"{turn}:explore-order:{len(remaining)}", "Choose the next location to explore",
                                    [(LOCATIONS[k], k) for k in remaining],
                                    note="Fixed landing sites: Fabrication Lead at Crash Flats; both Ecologists at Reef Gardens." if turn == 1 else "")
                remaining.remove(location)
                self.explore(location)
            self.phase = "Upkeep"
            remaining = [k for k in LOCATIONS if self.loc(k)["revealed"]]
            while remaining:
                location = self.ask(f"{turn}:upkeep-location:{len(remaining)}", "Choose the next location for mandatory upkeep",
                                    [(LOCATIONS[k], k) for k in remaining], note="Every revealed location resolves, including unoccupied locations.")
                remaining.remove(location)
                pending = list(self.loc(location)["cards"])
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
                                  [v[0] for _, v in options if v], "Only affordable, implemented recipes with a present recipient are offered.")
                if choice is None:
                    break
                self.craft(*choice)
            optional = [k for p in self.state["players"].values() for k in p["hand"] if k in ("R13", "R21", "K7")]
            if "K5" in self.loc("K")["set_aside"]:
                optional.append("K5")
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
            "prompt": engine.prompt, "status": status, "error": error}
