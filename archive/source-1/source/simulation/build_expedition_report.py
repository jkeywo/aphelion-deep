"""Build the HTML report for the Aphelion Deep 3-player / 3-turn expedition sim."""
import os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import expedition_sim as sim

R = sim.run_expedition(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
prof, turns, final = R["profiles"], R["turns"], R["final"]

SURF, INK, INK2, MUT, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8a86", "#e7e6e2"
BLUE, GREEN, ORANGE, VIOLET = "#2a78d6", "#008300", "#eb6834", "#4a3aa7"
GOOD, WARN, CRIT = "#0ca30c", "#fab219", "#d03b3b"
STANCE_COLOR = {"exploit": ORANGE, "restore": GREEN}
DEPT_COLOR = {"Engineering": ORANGE, "Ecology": GREEN}


def esc(s): return html.escape(str(s))


def tile(big, label, color=INK):
    return ('<div class="tile"><div class="big" style="color:%s">%s</div>'
            '<div class="tlabel">%s</div></div>' % (color, big, label))


def bar(label, value, vmax, color, width=200, suffix=""):
    w = max(2, int(round(value / vmax * width))) if vmax else 2
    return ('<div class="row"><span class="rl">%s</span>'
            '<span class="track"><span class="bar" style="width:%dpx;background:%s"></span></span>'
            '<span class="rv">%s%s</span></div>' % (esc(label), w, color, value, suffix))


def clock(phase, mx=6):
    pips = ""
    for i in range(mx):
        if i < phase:
            col = CRIT if phase >= mx else (WARN if phase >= mx - 2 else GOOD)
        else:
            col = "rgba(0,0,0,.08)"
        pips += '<span class="pip" style="background:%s"></span>' % col
    tag = ' <b style="color:%s">CRITICAL</b>' % CRIT if phase >= mx else ""
    return '<span class="clock">%s</span> phase %d/%d%s' % (pips, phase, mx, tag)


# location profiles table
prof_rows = ""
for loc in sim.LOCATIONS:
    p = prof[loc]
    prof_rows += ("<tr><td><b>%s</b></td><td>%d</td><td>%d</td><td>%d</td>"
                  "<td class=muted>materials %d · oxygen %d · biomass %d · reactor %d · pressure %d</td></tr>"
                  % (esc(loc), p["prod"], p["life"], p["risk"], p["raw"].get("materials", 0),
                     p["raw"].get("oxygen", 0), p["raw"].get("biomass", 0),
                     p["raw"].get("reactor", 0), p["raw"].get("pressure", 0)))

# players table
players_rows = ""
for pl in sim.PLAYERS:
    aff = " · ".join("%s %d" % (k.split()[0], v) for k, v in pl["affinity"].items())
    players_rows += ("<tr><td><b>%s</b></td><td><span class=chip style='background:%s1a;color:%s'>%s</span></td>"
                     "<td><span class=chip style='background:%s1a;color:%s'>%s</span></td><td class=muted>%s</td></tr>"
                     % (esc(pl["name"]), DEPT_COLOR[pl["dept"]], DEPT_COLOR[pl["dept"]], esc(pl["dept"]),
                        STANCE_COLOR[pl["stance"]], STANCE_COLOR[pl["stance"]], esc(pl["stance"]), esc(aff)))

# per-turn sections
turn_html = ""
for t in turns:
    rows = ""
    for e in t["expeditions"]:
        rows += ("<tr><td><b>%s</b><div class=muted style='font-size:11.5px'>%s</div></td>"
                 "<td>%s</td><td><span class=chip style='background:%s1a;color:%s'>%s</span></td>"
                 "<td>+%d prod<br>+%d life</td><td class=muted>%s</td><td class=muted>%s</td></tr>"
                 % (esc(e["player"]), esc(e["dept"]), esc(e["loc"]),
                    STANCE_COLOR[e["stance"]], STANCE_COLOR[e["stance"]], esc(e["stance"]),
                    e["prod"], e["life"], esc(e["find"]), esc(e["why"])))
    s = t["state"]
    outcome_color = CRIT if "defeat" in s["outcome"] else (GOOD if s["outcome"] == "victory" else INK2)
    turn_html += """
    <h3>Turn %d</h3>
    <table class=exp>
      <tr><th>Player</th><th>Expedition</th><th>Stance</th><th>Yield</th><th>Discovery</th><th>Why here</th></tr>
      %s
    </table>
    <div class=turnstate>
      <span>Colony <b>%d</b> production · <b>%d</b> life-support</span>
      <span>Reactor %s</span>
      <span>Megafauna aggression <b>%d</b></span>
      <span style="color:%s;font-weight:600">%s</span>
    </div>""" % (t["turn"], rows, s["production"], s["life_support"],
                 clock(s["reactor_phase"]), s["megafauna"], outcome_color,
                 s["outcome"].replace("_", " "))

# trajectory bars
maxres = max(max(t["state"]["production"], t["state"]["life_support"]) for t in turns)
traj = ""
for t in turns:
    traj += bar("T%d production" % t["turn"], t["state"]["production"], maxres, BLUE)
    traj += bar("T%d life-support" % t["turn"], t["state"]["life_support"], maxres, GREEN)

outcome = final["outcome"]
if "defeat" in outcome:
    verdict = ("The colony is <b>thriving on resources</b> — production and life-support both climb every "
               "turn — yet it reaches <b style='color:%s'>%s</b> by turn 3. The Fabrication Lead's extraction "
               "at Crash Flats, right beside the sunken Engine Core, stokes the reactor an extra phase each "
               "turn, and with both ecologists committed to the reef and the deep, <b>no one is ever assigned "
               "to contain the reactor</b>. Two restorers to one exploiter keeps the megafauna calm (aggression "
               "stays at 0), so the danger isn't the sea — it's the clock the extraction feeds."
               % (CRIT, outcome.replace("_", " ")))
    lever = ("The assignment policy optimises for colony supply and never trades an expedition slot for "
             "<code>attempt_stabilise_reactor</code>. Add a reactor-need term (e.g. when phase ≥ 3, pull the "
             "engineer off Crash Flats to contain) and re-run — the harness will show whether three players is "
             "simply too few to both supply the colony and hold the clock.")
else:
    verdict = "The colony ends turn 3 <b>%s</b> with production %d and life-support %d." % (
        outcome.replace("_", " "), final["production"], final["life_support"])
    lever = "Adjust the assignment policy or location yields and re-run to test alternatives."

HTML = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>The Aphelion Deep — 3-player expedition sim</title><style>
 body{{margin:0;background:{SURF};color:{INK};font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
 .wrap{{max-width:860px;margin:0 auto;padding:40px 28px 64px}}
 h1{{font-size:26px;margin:0 0 4px;letter-spacing:-.01em}}
 h2{{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:{INK2};margin:34px 0 12px;border-bottom:1px solid {GRID};padding-bottom:6px}}
 h3{{font-size:16px;margin:22px 0 8px}}
 .sub{{color:{MUT};margin:0 0 26px}} p{{color:{INK2}}}
 .tiles{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:8px 0}}
 .tile{{background:rgba(0,0,0,.02);border:1px solid {GRID};border-radius:10px;padding:14px 16px}}
 .big{{font-size:26px;font-weight:650;letter-spacing:-.02em}} .tlabel{{color:{MUT};font-size:12.5px;margin-top:2px}}
 table{{border-collapse:collapse;width:100%;font-size:13.5px;margin-top:4px}}
 th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid {GRID};vertical-align:top}}
 th{{color:{MUT};font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em}}
 .muted{{color:{MUT}}} .chip{{padding:1px 8px;border-radius:20px;font-size:12px;font-weight:600}}
 .row{{display:flex;align-items:center;gap:12px;margin:4px 0}}
 .rl{{width:120px;color:{INK2};font-size:12.5px;text-align:right;flex:none}}
 .track{{flex:1;background:rgba(0,0,0,.04);border-radius:5px;height:15px}} .bar{{height:15px;border-radius:5px;display:block}}
 .rv{{width:44px;font-size:12.5px;font-variant-numeric:tabular-nums;flex:none}}
 .clock{{display:inline-flex;gap:3px;vertical-align:middle;margin-right:6px}}
 .pip{{width:13px;height:13px;border-radius:3px;display:inline-block}}
 .turnstate{{display:flex;flex-wrap:wrap;gap:18px;margin:8px 0 2px;padding:10px 12px;background:rgba(0,0,0,.02);border:1px solid {GRID};border-radius:9px;font-size:13px;color:{INK2}}}
 .note{{background:rgba(208,59,59,.05);border:1px solid rgba(208,59,59,.25);border-radius:10px;padding:14px 16px;color:{INK2};font-size:14px}}
 .callout{{background:rgba(42,120,214,.06);border:1px solid rgba(42,120,214,.25);border-radius:10px;padding:12px 16px;color:{INK2};font-size:13.5px;margin:6px 0 0}}
 code{{background:rgba(0,0,0,.05);padding:1px 5px;border-radius:4px;font-size:12.5px}}
 table.exp td:nth-child(4){{white-space:nowrap;font-variant-numeric:tabular-nums}}
</style></head><body><div class=wrap>
<h1>The Aphelion Deep — first three turns, three players</h1>
<p class=sub>Three role cards (two Ecology, one Engineering) across three expedition sites. Assignment
by role affinity + colony need + crowding; every yield and consequence resolved by the real
colony / reactor / megafauna mechanisms. Location profiles derived from the card text.</p>

<div class=tiles>{tiles}</div>

<div class=callout><b>Content check.</b> Verified in <code>components.xlsx</code>: <b>3 locations</b>
(Reef Gardens 21 cards, Crash Flats 14, Kelp Cathedral 9) and <b>3 role cards</b> — but two are
Ecology (Lead + Systems Ecologist, native to the reef) and one is Engineering (Fabrication Lead,
native to the wreckage). <b>Kelp Cathedral has no role of its own</b>, so the deep site is only ever
reached when crowding pushes an ecologist off the reef.</div>

<h2>The three sites (yields derived from card text)</h2>
<table><tr><th>Location</th><th>Production</th><th>Life</th><th>Reactor heat</th><th>Source icons counted</th></tr>
{prof_rows}</table>

<h2>The three players</h2>
<table><tr><th>Role</th><th>Department</th><th>Philosophy</th><th>Expedition affinity</th></tr>
{players_rows}</table>

<h2>The playthrough</h2>
{turn_html}

<h2>Colony trajectory</h2>
{traj}

<h2>What the sim reveals</h2>
<div class=note>{verdict}</div>
<p class=callout style="background:rgba(0,131,0,.06);border-color:rgba(0,131,0,.25)"><b>Lever to test.</b> {lever}</p>

<p class=sub style="margin-top:26px">Reproduce: <code>python3 simulation/expedition_sim.py</code> ·
report: <code>python3 simulation/build_expedition_report.py</code>. Seeded &amp; deterministic.</p>
</div></body></html>""".format(
    SURF=SURF, INK=INK, INK2=INK2, MUT=MUT, GRID=GRID,
    tiles=(tile("3", "players / roles") + tile("3", "expedition sites")
           + tile(str(final["reactor_phase"]) + "/6", "reactor at turn 3",
                  CRIT if "defeat" in outcome else INK)
           + tile(outcome.replace("_", " "), "turn-3 outcome",
                  CRIT if "defeat" in outcome else GOOD)),
    prof_rows=prof_rows, players_rows=players_rows, turn_html=turn_html, traj=traj,
    verdict=verdict, lever=lever)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "aphelion_expedition_report.html")
open(OUT, "w", encoding="utf-8").write(HTML)
print("wrote", OUT, "| outcome:", outcome, "| reactor", final["reactor_phase"])
