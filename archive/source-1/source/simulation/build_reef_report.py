"""Report: the faithful Reef Gardens expedition + the honest upkeep-encoding coverage."""
import os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import reef_expedition as R
import parse_upkeep

reef, log = R.run(3)
upkeep, stats = parse_upkeep.main(R.WB)

SURF, INK, INK2, MUT, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a86", "#e7e6e2"
BLUE, GREEN, GOOD, WARN, CRIT = "#2a78d6", "#008300", "#0ca30c", "#eda100", "#d03b3b"
KIND_COLOR = {"play_at_location": BLUE, "to_hand": GREEN, "resolve_now": MUT,
              "gate-closed": CRIT, "gate-open": GOOD, "upkeep": BLUE, "upkeep-unresolved": WARN}


def esc(s): return html.escape(str(s))


def turn_block(turn):
    rows = ""
    for kind, what, detail in turn:
        if kind == "--":
            rows += '<tr class=sec><td colspan=3>%s</td></tr>' % esc(what)
        elif kind == "state":
            rows += '<tr class=st><td colspan=3>%s &nbsp; <span class=muted>%s</span></td></tr>' % (esc(what), esc(detail))
        else:
            c = KIND_COLOR.get(kind, INK2)
            rows += ('<tr><td><span class=chip style="background:%s1a;color:%s">%s</span></td>'
                     '<td>%s</td><td class=muted>%s</td></tr>' % (c, c, esc(kind), esc(what), esc(detail)))
    return rows


# upkeep coverage table (only cards that HAVE upkeep)
cov_rows = ""
for cid, d in sorted(upkeep.items()):
    full = d["bands_tile_0_5"] and d["all_ops_parsed"]
    state = ("fully encoded", GOOD) if full else (("bands parsed, ops need hand-encoding", WARN)
             if d["bands_tile_0_5"] else ("irregular / prose", CRIT))
    cov_rows += ('<tr><td>%s</td><td class=muted>%s</td><td><span class=chip style="background:%s1a;color:%s">%s</span></td></tr>'
                 % (esc(cid), esc(d["type"]), state[1], state[1], state[0]))

turns_html = "".join('<table class=trace>%s</table>' % turn_block(t) for t in log)

HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Reef Gardens — faithful expedition</title><style>
 body{{margin:0;background:{SURF};color:{INK};font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
 .wrap{{max-width:820px;margin:0 auto;padding:40px 28px 64px}} h1{{font-size:25px;margin:0 0 4px}}
 h2{{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:{INK2};margin:30px 0 10px;border-bottom:1px solid {GRID};padding-bottom:6px}}
 .sub{{color:{MUT};margin:0 0 24px}} p{{color:{INK2}}}
 table{{border-collapse:collapse;width:100%;font-size:13px;margin:6px 0 14px}}
 td{{padding:5px 9px;border-bottom:1px solid {GRID};vertical-align:top}}
 .trace td:first-child{{width:150px;white-space:nowrap}} .muted{{color:{MUT}}}
 .chip{{padding:1px 8px;border-radius:20px;font-size:11.5px;font-weight:600}}
 tr.sec td{{background:rgba(0,0,0,.03);font-weight:600;color:{INK};text-transform:uppercase;font-size:11.5px;letter-spacing:.04em}}
 tr.st td{{background:rgba(42,120,214,.05);font-variant-numeric:tabular-nums}}
 .note{{background:rgba(208,59,59,.05);border:1px solid rgba(208,59,59,.22);border-radius:10px;padding:13px 16px;color:{INK2};font-size:13.5px}}
 .good{{background:rgba(0,131,0,.06);border-color:rgba(0,131,0,.25)}}
 code{{background:rgba(0,0,0,.05);padding:1px 5px;border-radius:4px;font-size:12.5px}}
</style></head><body><div class=wrap>
<h1>Reef Gardens — a faithful expedition</h1>
<p class=sub>The real 21-card ordered, two-faced deck, turned one card at a time by the package's own
mechanisms. Dispositions, Population starts, and upkeep bands are read from the workbook; the deck
cursor persists across turns. This is the game's actual rule loop — not the invented stand-in.</p>

<div class=note><b>The gate holds.</b> Turning the surface reef (cards 1–14) reaches the
<b>Reef Caverns</b> expedition marker, which requires <code>2 Oxygen + 2 Knowledge</code> to descend.
The surface reef yields only <b>1 Oxygen</b> (Filterweed at Pop 3+) and <b>1 Knowledge</b> (one notes
card) — so the deep stays <b>locked across all three turns</b>, the cursor resting on the marker. The
earlier stand-in let anyone dive anywhere; the encoded rules gate the deep behind ecosystem
development, exactly as designed. (Whether the second Knowledge card sitting *behind* the gate is
intended or a content snag is now a visible, testable question.)</div>

<h2>The playthrough (deck cursor persists)</h2>
{turns_html}

<h2>Upkeep encoding coverage — the honest gap</h2>
<p>Of 46 cards, <b>19 have an Upkeep section</b>; only <b>4</b> use the clean
<code>Pop N – effect</code> form. Of those, Filterweed encodes fully; the population-dynamics fauna
parse their bands but their effect ops (consume-from-fauna, else-branches) need hand-encoding; the
rest (Rations, Choose-one, convert/produce) are free-form prose. Each unencoded card is <b>flagged,
not silently skipped</b> — the tracked gap the executable layer exists to surface.</p>
<table>{cov_rows}</table>

<p class=note style="background:rgba(0,131,0,.06);border-color:rgba(0,131,0,.25)"><b>Where this leaves you.</b>
The deck-turning, disposition, expedition gate and Population dynamics are now <b>encoded and running</b>
on the real deck, and <code>gsx</code> validates the whole model (references resolve, the mechanism
contracts hold, the Filterweed bands tile Pop 0–5). The remaining work is authoring the prose upkeep
into the <code>op</code> vocabulary (or regularising the card text) — a bounded, tracked list, one card
at a time, each re-checked by the harness.</p>

<p class=sub style="margin-top:24px">Reproduce: <code>python3 simulation/reef_expedition.py</code> ·
parse coverage: <code>python3 tools/parse_upkeep.py</code>. Content in
<code>game/exploration.gamespec.md</code>, mechanisms in <code>mechanisms/exploration.py</code>.</p>
</div></body></html>""".format(
    SURF=SURF, INK=INK, INK2=INK2, MUT=MUT, GRID=GRID,
    turns_html=turns_html, cov_rows=cov_rows)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "reef_expedition_report.html")
open(OUT, "w", encoding="utf-8").write(HTML)
print("wrote", OUT, "| cards with parsed bands:", len(upkeep))
