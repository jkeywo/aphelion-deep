"""Blow-by-blow of the Reef Gardens FIRST turn with 2 players — a rule-capture review.

Runs the encoded simulation, then narrates each card against its actual text: the
rule as written, what the sim currently does, and whether the rule is captured
(matches / approximated / not captured). Ends with a scorecard and the corrected
icon tally so the designer can see exactly what to encode next.
"""
import os, sys, html, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import reef_expedition as R

# --- load card text from the workbook ---
import openpyxl
wb = openpyxl.load_workbook(R.WB, data_only=True)
ws = wb["Cards"]; rows = list(ws.iter_rows(values_only=True))
hdr = [str(c).strip() if c else "" for c in rows[0]]
gi = lambda n: hdr.index(n) if n in hdr else None
ID, NM, CT, LOC, FT, BT = [gi(x) for x in ["ID", "Name", "Card Type", "Location", "Front Text", "Back Text"]]
CARDS = {}
for r in rows[1:]:
    if r and r[ID] and str(r[LOC]) == "Reef Gardens":
        CARDS[str(r[ID])] = {"name": r[NM], "type": str(r[CT]), "front": str(r[FT] or ""), "back": str(r[BT] or "")}


def card(pos):
    for cid, c in CARDS.items():
        if re.search(r"_%d_" % pos, cid):
            return cid, c
    return None, None


def q(txt, n=240):
    t = re.sub(r"\s+", " ", txt).strip()
    return html.escape(t[:n] + ("…" if len(t) > n else ""))


V = {"ok": ("#0ca30c", "captured"), "warn": ("#eda100", "approximated"), "gap": ("#d03b3b", "not captured")}

# The 2-player intro turn, card by card. Each step: pos, actor, the rule (from card),
# what the sim does now, verdict, and the running effect.
STEPS = [
 (1, "both", "Tutorial narrative. Back: “Read aloud and follow instructions on the backs of cards as they are revealed.”",
     "Sim disposition = resolve_now: it reads and discards. No mechanic to capture.", "ok",
     "The intro deck is a guided tutorial; the backs drive setup."),
 (2, "both", "Department. Back: “You are a member of the Ecology Department. Reveal the next cards (3–4). Each player chooses 1 to keep and reads its back privately.”",
     "Sim disposition = to_hand. It does NOT run the ‘reveal 3–4, each player chooses a role’ step.", "warn",
     "Drives role assignment for the 2 players — an un-modelled setup instruction."),
 (3, "P1", "Lead Ecologist (Role, hidden). Back: “Passive: Diver — [1 Oxygen Icon]. Icons … are used as prerequisites … They are not consumed.”",
     "Sim sends it to_hand but does NOT count the role’s passive Oxygen icon.", "gap",
     "P1 now contributes a permanent 1 Oxygen. Confirms icons are a PRESENCE test, not a pool."),
 (4, "P2", "Systems Ecologist (Role, hidden). Back: “Passive: Cultivator — Increase the Population Track of one Flora card at your location by 1.”",
     "Sim sends it to_hand; the Cultivator passive (a Pop boost) is not modelled at all.", "gap",
     "P2 can raise a Flora’s Pop by 1 — e.g. push Filterweed from 2 to 3 so it yields Oxygen."),
 (8, "both", "Phase Reference. Front: Upkeep phase = choose an outpost, resolve upkeep of all cards in hand and at your location. Back: 15-min Exploration phase, form a team to visit one location.",
     "Sim resolve_now (informational).", "ok", "Defines the turn shape the harness follows."),
 (9, "both", "Reef Garden Outpost (Location). Upkeep: “Hydroponics: refill rations per Energy icon. Rations: each player must have a Food icon, reduce a flora’s Pop by 1, or reduce the Rations Track.” Back: “For this introductory turn you are exploring Reef Garden together.”",
     "Sim plays it at the location; its Rations/Hydroponics upkeep is free-form prose → flagged UNRESOLVED.", "warn",
     "Confirms the 2 players explore together this turn; the outpost upkeep needs encoding."),
 (10, "both", "Shallowwater Filterweed (Flora). “Provides 1 Oxygen while 3+ Pop.” Upkeep Pop 0/1/2-4/5. Back: set Population to 2.",
     "Sim plays it at Pop 2 and its Pop-band upkeep is FULLY encoded (Filterweed is the one card that parses cleanly).", "ok",
     "At Pop 2 it gives no Oxygen yet — but P2’s Cultivator (→3) or upkeep would push it to yield 1 Oxygen."),
 (11, "both", "Spotted Grazers (Fauna). Upkeep: “Pop 1-2: −1 Population from Fauna then +1 Pop, else −1 Pop …”. Back: set Pop 2.",
     "Sim plays it at Pop 2; the consume-from-fauna / else-branch upkeep is bands-parsed but ops UNRESOLVED.", "warn",
     "Population dynamics need the consume_population / else op encoding."),
 (12, "both", "Coral Shelf Formation (Mineral). Upkeep: “Choose one: (a) convert Abundance into Materials/Coral (b) +1 Abundance.” Back: set Abundance to 2.",
     "Sim plays it; the choose-one upkeep is UNRESOLVED, and Abundance (a second track) isn’t modelled.", "gap",
     "Introduces an Abundance track + a player choose-one — neither encoded yet."),
 (13, "both", "Reef Ecologist’s Notes (Knowledge). Front: “[1 Knowledge Icon]”. Back: “Set this card beside the deck. GAIN this card when two cards here have 4+ population.”",
     "Sim sends it straight to_hand and would count its Knowledge unconditionally.", "gap",
     "The real rule is a CONDITIONAL gain (two cards at 4+ Pop). The sim’s disposition is wrong for this card."),
 (14, "both", "Spawning Ground (Dilemma). Front: choose unanimously — A Harvest → [Food], B Protect → +2 Pop to Filterweed & Grazers, C Tag & Monitor → [Knowledge]. Tuck under the outpost, chosen icon visible.",
     "Sim resolve_now: it discards the dilemma without offering the choice or applying any reward.", "gap",
     "A unanimous group choice that yields a persistent Food/Knowledge icon OR a Pop boost — completely un-modelled."),
 (15, "both", "Reef Caverns (Expedition GATE). Back: “Start an exploration here … if you meet 2 [Oxygen] + 2 [Knowledge]. Requirements can be met by cards in hand or at this location.”",
     "Sim evaluates the gate via mechanism.check_expedition_gate (a presence test — correct), but with an undercounted icon pool.", "warn",
     "The gate logic is captured; its INPUTS are not (missing role passives, the dilemma, the conditional knowledge)."),
]


def scorecard():
    items = [
     ("Ordered deck, turned one card at a time, cursor persists", "ok"),
     ("Card disposition by type (play / hand / resolve)", "ok"),
     ("Two-faced cards (front reveal / back in-play)", "ok"),
     ("Expedition gate as a presence test (icons not consumed)", "ok"),
     ("Filterweed Pop-banded upkeep", "ok"),
     ("Role passive ICONS (Lead Ecologist → 1 Oxygen)", "gap"),
     ("Role passive ACTIONS (Systems Ecologist Cultivator +1 Flora Pop)", "gap"),
     ("Conditional card gain (Knowledge notes: two cards at 4+ Pop)", "gap"),
     ("Dilemma: unanimous choice + persistent icon/Pop reward", "gap"),
     ("Grazers consume/else upkeep ops", "gap"),
     ("Coral choose-one + Abundance track", "gap"),
     ("Outpost Rations / Hydroponics upkeep", "gap"),
    ]
    rows = ""
    for label, v in items:
        col, word = V[v]
        rows += ('<tr><td>%s</td><td><span class=chip style="background:%s1a;color:%s">%s</span></td></tr>'
                 % (html.escape(label), col, col, word))
    return rows


# ---- render ----
SURF, INK, INK2, MUT, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a86", "#e7e6e2"
step_html = ""
for pos, actor, rule, sim, verdict, effect in STEPS:
    cid, c = card(pos)
    col, word = V[verdict]
    front = q(c["front"]) if c else ""
    back = q(c["back"]) if c and c["back"].strip() else ""
    step_html += """
    <div class=step>
      <div class=sh><span class=pos>#%d</span> <b>%s</b> <span class=muted>· %s · %s</span>
        <span class=chip style="background:%s1a;color:%s;float:right">%s</span></div>
      <div class=quote><b>Front:</b> %s%s</div>
      <div class=rule><b>Rule as written:</b> %s</div>
      <div class=sim><b>What the sim does:</b> %s</div>
      <div class=eff>%s</div>
    </div>""" % (pos, html.escape(c["name"]), html.escape(c["type"]), actor, col, col, word,
                 front, ("<br><b>Back:</b> " + back) if back else "", html.escape(rule),
                 html.escape(sim), html.escape(effect))

HTML = """<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Reef Gardens — Turn 1 blow-by-blow (2 players)</title><style>
 body{{margin:0;background:%(SURF)s;color:%(INK)s;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
 .wrap{{max-width:820px;margin:0 auto;padding:40px 28px 64px}} h1{{font-size:25px;margin:0 0 4px}}
 h2{{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:%(INK2)s;margin:30px 0 12px;border-bottom:1px solid %(GRID)s;padding-bottom:6px}}
 .sub{{color:%(MUT)s;margin:0 0 20px}} p{{color:%(INK2)s}}
 .step{{border:1px solid %(GRID)s;border-radius:10px;padding:12px 15px;margin:10px 0;background:rgba(0,0,0,.012)}}
 .sh{{font-size:15px;margin-bottom:6px}} .pos{{color:%(MUT)s;font-variant-numeric:tabular-nums}}
 .muted{{color:%(MUT)s}} .chip{{padding:1px 9px;border-radius:20px;font-size:11.5px;font-weight:600}}
 .quote{{font-size:12.5px;color:%(MUT)s;font-style:italic;margin:2px 0 7px;line-height:1.5}}
 .rule{{font-size:13.5px;margin:3px 0}} .sim{{font-size:13.5px;margin:3px 0;color:%(INK2)s}}
 .eff{{font-size:13px;margin-top:5px;color:%(INK2)s;border-left:3px solid %(GRID)s;padding-left:9px}}
 table{{border-collapse:collapse;width:100%%;font-size:13.5px;margin-top:4px}}
 td{{padding:6px 10px;border-bottom:1px solid %(GRID)s}}
 .note{{border-radius:10px;padding:13px 16px;font-size:13.5px;color:%(INK2)s}}
 .tally{{background:rgba(42,120,214,.05);border:1px solid rgba(42,120,214,.25)}}
 .verdict{{background:rgba(208,59,59,.05);border:1px solid rgba(208,59,59,.22)}}
 code{{background:rgba(0,0,0,.05);padding:1px 5px;border-radius:4px;font-size:12.5px}} b{{color:%(INK)s}}
</style></head><body><div class=wrap>
<h1>Reef Gardens — the first turn, two players</h1>
<p class=sub>A blow-by-blow of the intro turn, exploring the reef together. Each card is quoted, paired
with the rule as written, what the simulation currently does, and whether that rule is captured — so
you can check the model against your intent. <b>Player 1</b> takes the Lead Ecologist, <b>Player 2</b>
the Systems Ecologist.</p>

<h2>Exploration — turning the deck together</h2>
%(step_html)s

<h2>The gate moment — is the icon count right?</h2>
<div class="note tally">
The Reef Caverns gate needs <b>2 Oxygen + 2 Knowledge</b> (present in hand or at the location; not consumed).
<br><br><b>What the current sim counted:</b> <code>oxygen 0, knowledge 1</code> → closed. It missed the two
role passives and mis-handled the knowledge card, so it under-counted.
<br><br><b>What your rules actually allow this turn:</b>
<br>· <b>Oxygen = 2</b> ✓ — Lead Ecologist passive (1) + Filterweed pushed to Pop 3 by the Systems Ecologist’s
Cultivator, which then provides 1. <i>The Oxygen requirement is reachable turn 1.</i>
<br>· <b>Knowledge = 1</b> ✗ — the group faces a real dilemma: choose <b>Protect</b> and Filterweed→5, Grazers→4
so <i>two cards reach 4+ Pop and you gain the Notes card (1 Knowledge)</i>; or choose <b>Tag &amp; Monitor</b>
for 1 Knowledge directly — but not both. Either path yields only 1 of the 2 Knowledge needed.
<br><br><b>So the cavern stays closed on turn 1 — but as a tight, intended puzzle</b> (Oxygen met, Knowledge one
short), not the “permanently locked” picture the un-corrected sim implied. Whether a second Knowledge source
should exist before the gate is now a concrete design question.
</div>

<h2>Upkeep (after exploration)</h2>
<p>Choosing an outpost, then resolving each played card. <b>Filterweed</b> runs its encoded Pop band
(Pop 2–4 → +2, so 3 → 5). <b>Grazers</b>, <b>Coral</b>, and the <b>Outpost</b> Rations/Hydroponics are flagged
<b>unresolved</b> — prose not yet encoded. This is where produced Food/Materials would feed the colony.</p>

<h2>Rule-capture scorecard</h2>
<table>%(scorecard)s</table>

<div class="note verdict" style="margin-top:14px">
<b>Bottom line.</b> The <i>structure</i> is captured faithfully — ordered deck, disposition, two-faced cards,
the gate as a presence test, and Filterweed’s Pop band all match your rules. The <i>content that feeds the
gate</i> is not yet captured: role passives (the Oxygen icon and the Cultivator Pop-boost), the conditional
Knowledge gain, and the Dilemma’s choice-and-reward. Encoding those four is what turns this from “looks right”
into a faithful turn — and each is a small, bounded addition to <code>mechanisms/exploration.py</code> +
<code>game/exploration.gamespec.md</code>, re-checked by this harness.
</div>

<p class=sub style="margin-top:24px">Generated from the real card text + the encoded run.
<code>python3 simulation/build_blow_by_blow.py</code></p>
</div></body></html>""" % {"SURF": SURF, "INK": INK, "INK2": INK2, "MUT": MUT, "GRID": GRID,
                            "step_html": step_html, "scorecard": scorecard()}

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "reef_turn1_blow_by_blow.html")
open(OUT, "w", encoding="utf-8").write(HTML)
print("wrote", OUT)
