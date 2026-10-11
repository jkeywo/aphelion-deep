"""Report: 'cards as data' — capability blocks + the block-driven turn-1 run."""
import os, sys, html
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import reef_turn1_effects as T
from mechanisms import card_effects as CE

board, trace, upkeep = T.run("protect")
icons = CE.available_icons(board)

# The caverns, exercised (gate forced open — a labelled hypothetical).
dboard, dtrace, dupkeep = T.run("protect", descend=True)

# L6: run the block validator over the real blocks so the report shows the gate.
_d = HERE
for _ in range(8):
    for _t in (os.path.join(_d, "tools"), os.path.join(_d, "DSL", "tools")):
        if os.path.isdir(os.path.join(_t, "gsx")):
            sys.path.insert(0, _t); break
    else:
        _d = os.path.dirname(_d); continue
    break
from gsx.card_effects_check import check_card_effects, KNOWN_KEYS
from gsx.yamlblocks import read_objects
from gsx.findings import Report, Severity
_game = os.path.join(HERE, "..", "game")
_objs = []
for _f in ("reef_cards.gamespec.md", "exploration.gamespec.md"):
    _p = os.path.join(_game, _f)
    if os.path.exists(_p):
        _objs.extend(read_objects(_p, Report("parse")))
_l6 = Report("L6")
_nblocks = sum(1 for o in _objs if o.type == "card_effects" and o.id)
check_card_effects(_objs, _l6)
_l6_err = [f for f in _l6.findings if f.severity is Severity.ERROR]
_l6_info = [f for f in _l6.findings if f.severity is Severity.INFO]

SURF,INK,INK2,MUT,GRID="#fcfcfb","#0b0b0b","#52514e","#8a8a86","#e7e6e2"
BLUE,GREEN,WARN,CRIT="#2a78d6","#008300","#eda100","#d03b3b"
KC={"role":GREEN,"action":GREEN,"play":BLUE,"aside":MUT,"dilemma":"#4a3aa7","GATE":CRIT,
    "reveal":INK2,"to_hand":GREEN,"resolve":MUT,"upkeep":BLUE,"upkeep-unresolved":WARN}
def esc(s): return html.escape(str(s))

EXAMPLES = [
("Lead Ecologist — a role passive (an Oxygen icon)",
"""card_effects:
  id: reef_gardens_3_lead_ecologist
  front: { role: true, hidden: true }
  back:
    disposition: to_player_hand
    passive:
      - { provides_icon: { icon: oxygen, amount: 1 } }"""),
("Systems Ecologist — a role passive that is an ACTION",
"""  back:
    passive:
      - { action: { id: cultivator,
            change_track: { track: population,
              target: { type: flora, at: location, choose: player }, delta: 1 } } }"""),
("Shallowwater Filterweed — a conditional icon + Pop-banded upkeep",
"""  front:
    provides_icon:
      - { icon: oxygen, amount: 1, when: { self_pop_ge: 3 } }
    upkeep:
      bands:
        - { pop: 1,   do: [ { change_track: { track: population, target: self, delta: 1 } } ] }
        - { pop: "2-4", do: [ { change_track: { track: population, target: self, delta: 2 } } ] }
  back:
    on_reveal:
      - { disposition: play_at_location }
      - { set_track: { track: population, value: 2 } }"""),
("Spawning Ground — a unanimous dilemma, each option a real effect",
"""  front:
    dilemma:
      choose: unanimous
      options:
        - { id: tag_monitor, label: "Tag & Monitor",
            do: [ { provides_icon: { icon: knowledge, amount: 1 } }, { tuck: { under: outpost } } ] }
        - { id: protect, label: "Protect",
            do: [ { change_track: { track: population, target: card.…filterweed, delta: 2 } },
                  { change_track: { track: population, target: card.…grazers, delta: 2 } } ] }"""),
("Reef Ecologist's Notes — a CONDITIONAL gain",
"""  back:
    on_reveal: [ { disposition: set_beside_deck } ]
    conditional_gain:
      - { to: player_hand, when: { location_cards_pop_ge: { pop: 4, count: 2 } } }"""),
("Reef Caverns — the expedition gate (presence test)",
"""  back:
    gate:
      requires: { oxygen: 2, knowledge: 2 }
      sourced_from: [hand, location]"""),
]

VOCAB=[("disposition","where a turned card goes (hand / play / set_aside / beside_deck / resolve / discard)"),
("provides_icon","{icon, amount, when?} — a presence icon (not consumed), optionally conditional"),
("set_track / change_track","initialise or adjust a card track (population, abundance, …)"),
("passive","persistent effect on a role/card: an icon, or an {action: …}"),
("reveal_cards / each_player_chooses","setup: reveal cards, each player keeps one (assigns roles)"),
("conditional_gain","gain a set-aside card when a condition holds (e.g. two cards at 4+ Pop)"),
("dilemma","{choose: unanimous, options: [{id, label, do:[effects]}]}"),
("choose_one","pick one of several upkeep effects"),
("gate","{requires: {icon: n}, sourced_from, on_meet} — the expedition gate"),
("tuck / instruction / narrative","tuck under a card; read-aloud; flavour (no mechanic)"),
("status: unresolved","an honest, tracked marker for prose not yet encoded"),
]
def cond(): 
    return "; ".join("%s %s"%(k,v if False else "") for k,v in [])

steps="".join(
 '<tr><td><span class=chip style="background:%s1a;color:%s">%s</span></td><td>%s</td><td class=muted>%s</td></tr>'
 %(KC.get(k,INK2),KC.get(k,INK2),esc(k),esc(w),esc(d)) for k,w,d in trace)
up="".join(
 '<tr><td><span class=chip style="background:%s1a;color:%s">%s</span></td><td>%s</td><td class=muted>%s</td></tr>'
 %(KC.get(k,INK2),KC.get(k,INK2),esc(k),esc(w),esc(d)) for k,w,d in upkeep)
ex="".join('<h3>%s</h3><pre>%s</pre>'%(esc(t),esc(code)) for t,code in EXAMPLES)
vocab="".join('<tr><td><code>%s</code></td><td class=muted>%s</td></tr>'%(esc(k),esc(v)) for k,v in VOCAB)

# caverns descent rows (only the caverns-specific traces + upkeep)
_cavern_up = [(k,w,d) for k,w,d in dupkeep if any(s in str(w) for s in
              ("glow_polyp","snapper","calcite","survey","watcher","pollination","bioluminescent"))]
dsteps="".join(
 '<tr><td><span class=chip style="background:%s1a;color:%s">%s</span></td><td>%s</td><td class=muted>%s</td></tr>'
 %(KC.get(k,INK2),KC.get(k,INK2),esc(k),esc(w),esc(d)) for k,w,d in _cavern_up)
dres=esc(dboard.resources)

# L6 validator findings
l6rows="".join(
 '<tr><td><span class=chip style="background:%s1a;color:%s">%s</span></td><td class=muted>%s</td></tr>'
 %(WARN,WARN,esc(f.rule.split(".")[-1]),esc(f.summary)) for f in _l6_info)
l6verdict=("<b>PASS</b> — %d capability blocks; every verb, icon, track and card reference resolves."
           %_nblocks) if not _l6_err else ("<b>FAIL</b> — %d errors."%len(_l6_err))

HTML="""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Cards as data — Reef Gardens</title><style>
 body{{margin:0;background:%(SURF)s;color:%(INK)s;font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
 .wrap{{max-width:820px;margin:0 auto;padding:40px 28px 64px}} h1{{font-size:25px;margin:0 0 4px}}
 h2{{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:%(INK2)s;margin:30px 0 12px;border-bottom:1px solid %(GRID)s;padding-bottom:6px}}
 h3{{font-size:14px;margin:16px 0 4px}} .sub{{color:%(MUT)s;margin:0 0 20px}} p{{color:%(INK2)s}}
 pre{{background:#1c1c1a;color:#e7e6e2;border-radius:9px;padding:12px 14px;font-size:12px;overflow-x:auto;line-height:1.45;margin:0 0 6px}}
 table{{border-collapse:collapse;width:100%%;font-size:13.5px;margin-top:4px}} td{{padding:6px 10px;border-bottom:1px solid %(GRID)s;vertical-align:top}}
 .muted{{color:%(MUT)s}} .chip{{padding:1px 9px;border-radius:20px;font-size:11.5px;font-weight:600}}
 code{{background:rgba(0,0,0,.05);padding:1px 5px;border-radius:4px;font-size:12.5px}}
 .note{{background:rgba(42,120,214,.05);border:1px solid rgba(42,120,214,.25);border-radius:10px;padding:13px 16px;font-size:13.5px;color:%(INK2)s}} b{{color:%(INK)s}}
</style></head><body><div class=wrap>
<h1>Cards as data — capability blocks the sim interprets</h1>
<p class=sub>Each card's rules are captured from its text as a <b>front</b> and a <b>back</b> effect block
(<code>game/reef_cards.gamespec.md</code>). A generic interpreter (<code>mechanisms/card_effects.py</code>)
reads them and works out the turn — no per-card logic in the sim. This is the same Reef Gardens turn 1,
now driven entirely by the data.</p>

<h2>What a capability block looks like</h2>
%(ex)s

<h2>Turn 1, driven by the blocks</h2>
<table>%(steps)s</table>
<div class=note><b>The gate tally is now derived from the data:</b> <code>%(icons)s</code>. Oxygen 2 comes from
the Lead Ecologist's passive icon + the Filterweed the Cultivator pushed to Pop 3; Knowledge 1 comes from the
Notes card, gained because Protect took two cards to 4+ Pop. Need 2 Knowledge → the cavern stays closed — the
tight puzzle, produced by the rules, not hardcoded.</div>

<h2>Upkeep</h2>
<table>%(up)s</table>

<h2>Beyond the gate — the caverns, exercised</h2>
<p>The same interpreter drives cards 16–21. Forcing the gate open (a <b>labelled hypothetical</b>, not a
legal move on this tally) runs the deep's own upkeep verbs: cross-card conditions
(<code>card_track_ge</code>), an apex predator that consumes <b>Prey</b> population, a mineral that
<code>produce_resource</code>s Materials at Abundance 2+, and an Event that <code>remove_self</code>s when it
finds nothing to act on. Resources produced: <code>%(dres)s</code>.</p>
<table>%(dsteps)s</table>
<div class=note style="background:rgba(237,161,0,.06);border-color:rgba(237,161,0,.3)"><b>A rule the encoding
surfaced.</b> The Snapper is an apex predator that eats <b>Prey</b>; the surface Grazers eat <b>Fauna</b>. Run
together, the Grazers' <code>consume_population: {from: {type: fauna}}</code> can eat the Snapper — predator and
prey reversed. That is a concrete, testable content question the executable layer made visible, exactly what it
is for. It's flagged in the block's DESIGN NOTE, not silently resolved.</div>

<h2>gsx validates the blocks themselves</h2>
<p>Because the rules are data, <code>gsx</code> checks them like any contract: %(l6verdict)s Unencoded prose is
not an error — it is an honest, tracked <code>status: unresolved</code> marker (INFO), so the gaps are counted,
not hidden:</p>
<table>%(l6rows)s</table>

<h2>The effect-verb vocabulary (closed set)</h2>
<table>%(vocab)s</table>
<p class=note style="margin-top:12px">Adding a card is now authoring a block, not editing the sim. Encoding a
prose effect means adding its verb here (e.g. the Grazers <code>consume_population</code> / else op, or the
Outpost Rations) — and <code>gsx</code> validates that every verb, icon and reference resolves: a new verb the
interpreter doesn't know fails <b>L6</b>, so the data and the interpreter can't drift apart.</p>

<p class=sub style="margin-top:22px">Reproduce: <code>python3 simulation/reef_turn1_effects.py</code>.
Blocks in <code>game/reef_cards.gamespec.md</code>, interpreter in <code>mechanisms/card_effects.py</code>.</p>
</div></body></html>"""%{"SURF":SURF,"INK":INK,"INK2":INK2,"MUT":MUT,"GRID":GRID,
 "ex":ex,"steps":steps,"up":up,"vocab":vocab,"icons":esc(icons),
 "dsteps":dsteps,"dres":dres,"l6rows":l6rows,"l6verdict":l6verdict}
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,"reef_cards_as_data_report.html")
open(OUT,"w",encoding="utf-8").write(HTML); print("wrote",OUT)
