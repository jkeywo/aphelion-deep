"""Parse the regular Pop-banded upkeep text out of the component workbook.

Card upkeep is written in a regular form on the card front:
    Upkeep
    Pop 0 - No effect
    Pop 1 - +1 Pop
    Pop 2-4 - +2 Population
    Pop 5 - No effect
This extracts the bands per card and lightly classifies each band's effect into the
closed op vocabulary; irregular effects keep their raw text and are flagged, so the
port is 'mostly mechanical, hand-finish the rest'.
"""
from __future__ import annotations
import os, re, json, sys

WB = os.environ.get("APHELION_WB",
    "/mnt/user-data/uploads/AIWriting/GameProjects/aphelion_deep/source/components/components.xlsx")

BAND = re.compile(r"^\s*Pop\s+(\d+)(?:\s*[-–]\s*(\d+))?\s*[-–:]\s*(.+?)\s*$", re.I)
ICON = re.compile(r"(?:Provides|Pop\s*\d\+?:?)\s*(\d+)?\s*\[?(Oxygen|Knowledge|Food|Energy|Biomass|Materials|Pressure|Reactor)", re.I)


def classify(effect: str):
    e = effect.strip().lower()
    if e in ("no effect", "-", "none"):
        return [{"op": "no_effect"}]
    # simple own-population change: "+1 Pop", "+2 Population", "-1 Pop"
    m = re.fullmatch(r"([+-]\d+)\s*(?:pop|population)\.?", e)
    if m:
        return [{"op": "change_population", "target": "self", "delta": int(m.group(1))}]
    # otherwise: irregular (else-branches, consume-from-fauna, choose-one, spends)
    return None


def extract_upkeep(front: str):
    if not front:
        return None
    lines = front.splitlines()
    # find the Upkeep section
    idx = next((i for i, l in enumerate(lines) if l.strip().lower().startswith("upkeep")), None)
    if idx is None:
        return None
    bands = []
    for l in lines[idx + 1:]:
        m = BAND.match(l)
        if m:
            lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
            raw = m.group(3).strip()
            ops = classify(raw)
            bands.append({"pop": (str(lo) if lo == hi else "%d-%d" % (lo, hi)),
                          "lo": lo, "hi": hi, "raw": raw, "ops": ops})
        elif l.strip() and bands and not l.strip().lower().startswith(("rations", "hydroponics", "icons", "triggers")):
            continue
    return bands or None


def band_coverage(bands, mx=5):
    covered = set()
    for b in bands:
        for p in range(b["lo"], b["hi"] + 1):
            covered.add(p)
    full = covered == set(range(0, mx + 1))
    return full, sorted(set(range(0, mx + 1)) - covered)


def main(wb_path=None):
    import openpyxl
    wb = openpyxl.load_workbook(wb_path or os.environ.get("APHELION_WB", WB), data_only=True)
    ws = wb["Cards"]; rows = list(ws.iter_rows(values_only=True))
    hdr = [str(c).strip() if c else "" for c in rows[0]]
    gi = lambda n: hdr.index(n) if n in hdr else None
    ID, NM, CT, LOC, FT = gi("ID"), gi("Name"), gi("Card Type"), gi("Location"), gi("Front Text")
    out = {}
    stats = {"cards": 0, "with_upkeep": 0, "bands_full": 0, "fully_parsed": 0, "partial": 0}
    for r in rows[1:]:
        if not r or r[ID] is None:
            continue
        stats["cards"] += 1
        bands = extract_upkeep(str(r[FT] or ""))
        if not bands:
            continue
        stats["with_upkeep"] += 1
        full, gaps = band_coverage(bands)
        allops = all(b["ops"] is not None for b in bands)
        if full: stats["bands_full"] += 1
        if full and allops: stats["fully_parsed"] += 1
        elif allops or full: stats["partial"] += 1
        out[str(r[ID])] = {"name": r[NM], "type": str(r[CT]), "location": str(r[LOC]),
                           "bands": bands, "bands_tile_0_5": full, "gaps": gaps,
                           "all_ops_parsed": allops}
    return out, stats


if __name__ == "__main__":
    data, stats = main()
    print("=== upkeep parse coverage ===")
    print("cards: %d | with Pop-banded upkeep: %d | bands tile 0-5: %d | fully parsed (bands+ops): %d | partial: %d"
          % (stats["cards"], stats["with_upkeep"], stats["bands_full"], stats["fully_parsed"], stats["partial"]))
    print("\nper-card:")
    for cid, d in data.items():
        flag = "FULL " if (d["bands_tile_0_5"] and d["all_ops_parsed"]) else ("bands✓ ops?" if d["bands_tile_0_5"] else "irregular")
        print("  %-40s %-8s %s  (%d bands)" % (cid, d["type"], flag, len(d["bands"])))
    if "--json" in sys.argv:
        open("/tmp/upkeep_bands.json", "w").write(json.dumps(data, indent=1, default=str))
        print("\nwrote /tmp/upkeep_bands.json")
