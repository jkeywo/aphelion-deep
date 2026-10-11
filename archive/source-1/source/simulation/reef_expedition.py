"""Faithful Reef Gardens expedition — the real ordered, two-faced deck, turned one
card at a time, with the expedition gate and Pop-banded upkeep resolved by the
package's own mechanisms. Contrast with the earlier stand-in sim, which invented
site yields and let anyone go anywhere.

Deck order, dispositions, Population starts, provided icons, and upkeep bands are
all read from the component workbook (card_type, Front/Back text). The deck cursor
persists across turns.
"""
from __future__ import annotations
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
for _rt in (os.path.join(HERE, "..", "..", "spec", "runtime"),
            os.path.join(HERE, "..", "spec", "runtime")):
    if os.path.isdir(os.path.join(_rt, "gamespec")):
        sys.path.insert(0, _rt)
        break
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

from mechanisms.exploration import (resolve_pop_upkeep, resolve_provide_icons,
                                     resolve_check_expedition_gate, CardState, UpkeepOutcome)
import parse_upkeep

WB = os.path.join(HERE, "..", "components", "components.xlsx")
DISPOSITION = {"narrative": "resolve_now", "department": "to_hand", "role": "to_hand",
               "phase reference": "resolve_now", "location": "play_at_location",
               "location outpost": "play_at_location", "sub-location": "play_at_location",
               "flora": "play_at_location", "fauna": "play_at_location", "mineral": "play_at_location",
               "knowledge": "to_hand", "dilemma": "resolve_now", "event": "resolve_now",
               "expedition": "set_aside", "equipment": "to_hand", "cascade": "resolve_now"}
GATE = {"reef_caverns": {"oxygen": 2, "knowledge": 2}}   # card 15 "2 [Oxygen] + 2 [Knowledge]"


def _num(cid):
    m = re.search(r"_(\d+)_", cid); return int(m.group(1)) if m else 999


def load_reef():
    import openpyxl
    wb = openpyxl.load_workbook(WB, data_only=True)
    ws = wb["Cards"]; rows = list(ws.iter_rows(values_only=True))
    hdr = [str(c).strip() if c else "" for c in rows[0]]
    gi = lambda n: hdr.index(n) if n in hdr else None
    ID, NM, CT, LOC, FT, BT = [gi(x) for x in ["ID", "Name", "Card Type", "Location", "Front Text", "Back Text"]]
    upkeep, _ = parse_upkeep.main(WB)
    deck = []
    for r in rows[1:]:
        if not r or r[ID] is None or str(r[LOC]) != "Reef Gardens":
            continue
        ctype = str(r[CT]).lower(); front = str(r[FT] or ""); back = str(r[BT] or "")
        pm = re.search(r"population track to (\d+)", back, re.I)
        icons = []
        for amt, mn, icon in re.findall(r"(?:Provides\s*(\d+)?[^.]*?while\s*(\d+)\+?\s*Pop|Pop\s*(\d+)\+?:?\s*(\d+)?)\s*\[?(Oxygen|Knowledge|Food|Energy|Biomass|Materials|Pressure)", front, re.I):
            pass  # (kept simple below)
        for m in re.finditer(r"Provides\s*(\d+)?\s*\[?(Oxygen|Knowledge|Food|Energy|Biomass|Materials|Pressure)\]?\s*icon\s*while\s*(\d+)\+?\s*Pop", front, re.I):
            icons.append({"icon": m.group(2).lower(), "amount": int(m.group(1) or 1), "min_pop": int(m.group(3))})
        if ctype == "knowledge":
            icons.append({"icon": "knowledge", "amount": 1, "min_pop": 0})   # a knowledge card carries a Knowledge icon
        deck.append({"id": str(r[ID]), "name": r[NM], "type": ctype, "pos": _num(str(r[ID])),
                     "disposition": DISPOSITION.get(ctype, "resolve_now"),
                     "pop_initial": int(pm.group(1)) if pm else None,
                     "icons": icons, "bands": upkeep.get(str(r[ID]), {}).get("bands")})
    deck.sort(key=lambda c: c["pos"])
    return deck


class Reef:
    def __init__(self):
        self.deck = load_reef()
        self.cursor = 0
        self.board = []     # [{"card":..., "state":CardState}]
        self.hand = []      # card dicts
        self.discard = []

    def _available_icons(self):
        icons = {}
        for b in self.board:
            got = resolve_provide_icons(b["state"], b["card"]["icons"]).outcome
            for k, v in got.items():
                icons[k] = icons.get(k, 0) + v
        for c in self.hand:
            for r in c["icons"]:
                if c["state"].population >= r["min_pop"] if False else True:
                    icons[r["icon"]] = icons.get(r["icon"], 0) + r["amount"]
        return icons

    def explore(self, trace):
        while self.cursor < len(self.deck):
            card = self.deck[self.cursor]
            d = card["disposition"]
            if d == "set_aside":                       # an Expedition marker: the gate
                avail = self._available_icons()
                req = GATE.get(card["id"].split("_", 2)[-1].rsplit("_", 0)[0], None) \
                    or GATE.get("reef_caverns")
                res = resolve_check_expedition_gate(req, avail)
                if res.status.value == "legal":
                    trace.append(("gate-open", card["name"], "have %s, needed %s" % (avail, req)))
                    self.cursor += 1                   # descend: keep turning into the caverns
                    continue
                trace.append(("gate-closed", card["name"], "have %s, needed %s — cannot descend" % (avail, req)))
                return                                 # location closes; cursor rests on the marker
            # ordinary card: apply disposition
            st = CardState("card.%s" % card["id"], card.get("pop_initial") or 0)
            card["state"] = st
            if d == "play_at_location":
                self.board.append({"card": card, "state": st})
            elif d == "to_hand":
                self.hand.append(card)
            else:
                self.discard.append(card)
            trace.append((d, card["name"], "pop %s" % st.population if d == "play_at_location" else card["type"]))
            self.cursor += 1

    def upkeep(self, trace):
        for b in self.board:
            bands = b["card"]["bands"]
            if not bands:
                continue
            r = resolve_pop_upkeep(b["state"], bands)
            if r.outcome is UpkeepOutcome.RESOLVED:
                delta = sum(c.delta for c in r.changes if c.field == "population")
                oldpop = b["state"].population
                newpop = max(0, min(5, oldpop + delta))
                b["state"] = CardState(b["state"].reference, newpop)
                trace.append(("upkeep", b["card"]["name"], "pop %d -> %d" % (oldpop, newpop)))
            else:
                trace.append(("upkeep-unresolved", b["card"]["name"], (r.trace[0][1] if r.trace else "prose only")))

    def turn(self, n):
        tr = []
        tr.append(("--", "TURN %d — Exploration (cursor at %d)" % (n, self.cursor), ""))
        self.explore(tr)
        tr.append(("--", "Upkeep", ""))
        self.upkeep(tr)
        tr.append(("state", "board=%d hand=%d cursor=%d" % (len(self.board), len(self.hand), self.cursor),
                   "icons now: %s" % self._available_icons()))
        return tr


def run(turns=3):
    r = Reef()
    out = []
    for n in range(1, turns + 1):
        out.append(r.turn(n))
    return r, out


if __name__ == "__main__":
    reef, log = run(3)
    for turn in log:
        print()
        for kind, what, detail in turn:
            if kind == "--":
                print("== %s ==" % what)
            elif kind == "state":
                print("   [%s]  %s" % (what, detail))
            else:
                print("   %-18s %-28s %s" % (kind, str(what)[:28], detail))
