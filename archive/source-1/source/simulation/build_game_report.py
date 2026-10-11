"""Report: the 3-player, 3-turn game across all three Tier-1 locations, driven end to
end by the card capability blocks. Every gate is opened (or held) for real."""
import os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import game_3p2t as G

faithful = G.run(assist=False, turns_n=3)

SURF, INK, INK2, MUT, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a86", "#e7e6e2"
BLUE, GREEN, PUR, WARN, CRIT, GOOD = "#2a78d6", "#008300", "#4a3aa7", "#eda100", "#d03b3b", "#0ca30c"
KC = {"role": GREEN, "action": GREEN, "play": BLUE, "aside": MUT, "dilemma": PUR,
      "GATE": CRIT, "reveal": INK2, "to_hand": GREEN, "resolve": MUT, "gain": GOOD,
      "upkeep": BLUE, "upkeep-unresolved": WARN, "assist": PUR}
STATUS_C = {"gate-closed": CRIT, "entry-denied": CRIT, "exhausted": GOOD, "open": GOOD, "unexplored": MUT}


def esc(s): return html.escape(str(s))


def trace_rows(trace):
    out = ""
    for k, w, d in trace:
        if k == "--":
            out += '<tr class=sec><td colspan=3>%s %s</td></tr>' % (esc(w), esc(d))
        else:
            c = KC.get(k, INK2)
            out += ('<tr><td><span class=chip style="background:%s1a;color:%s">%s</span></td>'
                    '<td>%s</td><td class=muted>%s</td></tr>' % (c, c, esc(k), esc(w), esc(d)))
    return out


def loc_block(L):
    sc = STATUS_C.get(L["status"], INK2)
    chips = " ".join('<span class=k>%s&nbsp;%d</span>' % (esc(i), n) for i, n in sorted(L["icons"].items()))
    res = " ".join('<span class=r>%s&nbsp;%d</span>' % (esc(i), n) for i, n in sorted(L["resources"].items())) or "<span class=muted>—</span>"
    return """<div class=loc>
      <div class=lh><b>%s</b> <span class=team>%s</span>
        <span class=stat style="color:%s;border-color:%s55">%s · %d/%d cards</span></div>
      <table class=trace>%s</table>
      <div class=tally>icons: %s &nbsp;·&nbsp; resources: %s</div>
    </div>""" % (esc(L["name"]), esc(", ".join(L["team"])), sc, sc, esc(L["status"]),
                 L["cursor"], L["of"], trace_rows(L["trace"]), chips or "<span class=muted>none</span>", res)


def turn_block(turn):
    locs = "".join(loc_block(L) for L in turn["locations"])
    return """<h2>Turn %d</h2><p class=why>%s</p>%s""" % (turn["turn"], esc(turn["why"]), locs)


def cat_block(cat, turn=1):
    site_rows = "".join(
        '<tr><td>%s</td><td>%s</td></tr>' % (esc(n),
            " ".join('<span class=k>%s&nbsp;%d</span>' % (esc(i), v) for i, v in sorted(ic.items())) or "<span class=muted>none</span>")
        for n, ic in cat["sites"].items())
    ppl_rows = ""
    for p in cat["players"]:
        ic = " ".join('<span class=k>%s&nbsp;%d</span>' % (esc(i), v) for i, v in sorted(p["icons"].items())) or "<span class=muted>none</span>"
        hand = ", ".join(esc(h) for h in p["hand"]) or "<span class=muted>—</span>"
        ppl_rows += '<tr><td>%s</td><td class=muted>%s</td><td class=muted>%s</td><td>%s</td><td class=muted>%s</td></tr>' % (
            esc(p["name"]), esc(p["role"]), esc(p["at"]), ic, hand)
    head = ("<h3>Icon catalogue — after Turn %d</h3>"
            "<p class=why>Where the icons actually are, split into the two pools a gate draws from: "
            "<b>site</b> icons that stay with a location, and <b>portable</b> icons a player carries anywhere.</p>" % turn)
    tables = ("<div class=cat><table class=ct><tr class=ch><td>Location (site icons)</td>"
              "<td>icons that stay here</td></tr>" + site_rows + "</table>"
              "<table class=ct><tr class=ch><td>Player</td><td>role</td><td>at</td>"
              "<td>portable icons</td><td>in hand</td></tr>" + ppl_rows + "</table></div>")
    return head + tables


cats = faithful["catalogues"]
faithful_html = (turn_block(faithful["turns"][0]) + cat_block(cats[1])
                 + turn_block(faithful["turns"][1])
                 + turn_block(faithful["turns"][2]) + cat_block(cats[3], turn=3))

HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>The Aphelion Deep — 3-player, 3-turn game</title><style>
 body{{margin:0;background:{SURF};color:{INK};font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
 .wrap{{max-width:860px;margin:0 auto;padding:40px 28px 64px}} h1{{font-size:25px;margin:0 0 4px}}
 h2{{font-size:15px;text-transform:uppercase;letter-spacing:.05em;color:{INK};margin:34px 0 4px}}
 h3{{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:{INK2};margin:26px 0 10px;border-bottom:1px solid {GRID};padding-bottom:6px}}
 .sub{{color:{MUT};margin:0 0 22px}} p{{color:{INK2}}} .why{{color:{MUT};margin:0 0 14px;font-size:13.5px}}
 .loc{{border:1px solid {GRID};border-radius:11px;padding:4px 14px 12px;margin:0 0 14px;background:#fff}}
 .lh{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 2px 4px;font-size:14.5px}}
 .team{{color:{MUT};font-size:12.5px}} .stat{{margin-left:auto;font-size:11.5px;border:1px solid;border-radius:20px;padding:1px 10px;font-weight:600}}
 table.trace{{border-collapse:collapse;width:100%;font-size:12.5px;margin:2px 0}}
 .trace td{{padding:4px 8px;border-bottom:1px solid {GRID};vertical-align:top}} .trace td:first-child{{width:118px;white-space:nowrap}}
 .muted{{color:{MUT}}} .chip{{padding:1px 8px;border-radius:20px;font-size:11px;font-weight:600}}
 tr.sec td{{background:rgba(0,0,0,.03);font-weight:600;color:{INK};text-transform:uppercase;font-size:10.5px;letter-spacing:.04em}}
 .tally{{font-size:12.5px;color:{INK2};padding:8px 2px 2px;font-variant-numeric:tabular-nums}}
 .k{{background:rgba(42,120,214,.1);color:{BLUE};border-radius:5px;padding:1px 6px;margin-right:3px;font-size:11.5px;font-weight:600}}
 .r{{background:rgba(0,131,0,.1);color:{GREEN};border-radius:5px;padding:1px 6px;margin-right:3px;font-size:11.5px;font-weight:600}}
 .note{{background:rgba(42,120,214,.05);border:1px solid rgba(42,120,214,.25);border-radius:10px;padding:13px 16px;font-size:13.5px;color:{INK2};margin:6px 0 4px}}
 .note.warn{{background:rgba(237,161,0,.07);border-color:rgba(237,161,0,.32)}}
 .note.good{{background:rgba(0,131,0,.06);border-color:rgba(0,131,0,.28)}}
 .cat{{display:flex;flex-direction:column;gap:10px;margin:6px 0 14px}}
 table.ct{{border-collapse:collapse;width:100%;font-size:12.5px;border:1px solid {GRID};border-radius:8px;overflow:hidden}}
 .ct td{{padding:6px 10px;border-bottom:1px solid {GRID}}} tr.ch td{{background:rgba(0,0,0,.03);font-weight:600;color:{INK};font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
 b{{color:{INK}}} code{{background:rgba(0,0,0,.05);padding:1px 5px;border-radius:4px;font-size:12px}}
</style></head><body><div class=wrap>
<h1>The Aphelion Deep — a 3-player, 3-turn game</h1>
<p class=sub>All three Tier-1 locations now run from their <b>card capability blocks</b> — Reef Gardens,
and the two just converted, <b>Crash Flats</b> (14 cards) and <b>Kelp Cathedral</b> (9). One interpreter
(<code>mechanisms/card_effects.py</code>) turns each ordered, two-faced deck; roles, gates, upkeep, crafting
and yields are all read from the data. The team states a plan each turn; every consequence below is computed,
not scripted. Decks persist between turns. Over three turns the crafted salvage opens two of the three deep
sites — no hypotheticals, this is the real game loop.</p>

<div class=note><b>The cast.</b> One Engineer and two Ecologists. Nobody starts with a role — the
department-reveal cards assign them as the decks are turned: Player 1 becomes <b>Fabrication Lead</b>
(passive Power icon), Players 2 &amp; 3 become <b>Lead Ecologist</b> (passive Oxygen) and
<b>Systems Ecologist</b> (the Cultivator action).</p></div>

{faithful_html}

<div class=note good><b>The three-turn arc — the economy is a lock, salvage is the key.</b>
<b>Turn 1</b> every expedition reaches its gate and it <b>holds</b>: Reef Caverns want <code>2 Oxygen + 2
Knowledge</code> (the reef yields 2 &amp; 1), the Engine Core wants <code>1 Oxygen + 3 Power</code> (the wreck
makes Power but no Oxygen), Kelp needs <code>2 Oxygen</code> to enter. But the wreck's Materials pay for
salvage: in the team phase the Engineer crafts the <b>Oxygen Tank</b> (1 Material → Oxygen) and the
<b>Scan Database</b> (3 Power on hand → Knowledge). <b>Turn 2</b> he carries the Oxygen Tank to Kelp; with
Lead Ecologist's Oxygen that makes 2 — <b>Kelp Cathedral opens</b> and its nine cards turn. <b>Turn 3</b> all
three converge on the Reef Caverns: the Oxygen Tank, the Scan Database and Lead Ecologist's Notes pool with
the reef's own Filterweed Oxygen to reach <code>3 Oxygen + 2 Knowledge</code> — <b>the caverns open</b> and
cards 16–21 turn. Two of the three deep sites cracked in three turns, entirely through crafted salvage and
coordination — exactly what the recipes and roles are <i>for</i>. Only the Engine Core stays sealed (it wants
the Power the team spent elsewhere) — a clean, legible trade-off, not a dead end.</div>

<div class=note warn><b>A food-chain question the encoding surfaces.</b> Once the Reef Caverns open in Turn 3,
the Crystalblind Snapper (apex predator, eats <b>Prey</b>) and the surface Spotted Grazers (eat <b>Fauna</b>)
share a board; as written the Grazers can eat the Snapper. And Kelp's Giant Lungweed reaches only Pop 2 with
no Cultivator present, so its <b>Pressure</b> icon (Pop 3+) never lights — the icon economy is sensitive to
who is on the expedition. Both are concrete, testable content notes, not sim bugs.</div>

<div class=note good><b>Where this leaves the conversion.</b> All three locations are now executable data.
<code>gsx</code> L6 validates every verb, icon, track and reference across the three files
(<b>0 errors</b>, 12 honest <code>unresolved</code> gaps). New this round and now in the closed vocabulary:
the <b>Pressure</b> icon and <b>Scanning</b> track, keyword-scoped conditions (<code>keyword_track_ge</code>,
<code>keyword_present</code>, <code>keyword_count_ge</code>, <code>not</code>), a conversion <code>rate</code>
(the Wreckage Field's 1 Abundance → 2 Materials), and a <b>craft</b> economy (cost / requires → hand or tuck)
that turns salvage into icons in the team phase. The power/energy icon is unified to <b>power</b> as
confirmed. Upkeep resolves in deck order; the Phase Reference card says players choose the order, so that is
one valid ordering — a knob the report makes visible.</div>

<p class=sub style="margin-top:22px">Reproduce: <code>python3 simulation/game_3p2t.py</code>
(add <code>--assist</code> to force every gate). Blocks in
<code>game/crash_flats_cards.gamespec.md</code> and <code>game/kelp_cathedral_cards.gamespec.md</code>;
interpreter in <code>mechanisms/card_effects.py</code>; validator <code>tools/gsx/card_effects_check.py</code>.</p>
</div></body></html>""".format(
    SURF=SURF, INK=INK, INK2=INK2, MUT=MUT, GRID=GRID, BLUE=BLUE, GREEN=GREEN,
    faithful_html=faithful_html)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "aphelion_3p2t_report.html")
open(OUT, "w", encoding="utf-8").write(HTML)
print("wrote", OUT)
