"""Load court_data.csv (spreadsheet layout) into a clean list of court groups."""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TIMES = ["4 PM", "7 PM", "10 PM"]

# Column positions in court_data.csv for each time: (discoloration, friction, coef)
TIME_COLUMNS = {"4 PM": (3, 4, 5), "7 PM": (6, 7, 8), "10 PM": (9, 10, 11)}
MEASURED_TIMES = {"4 PM"}


def _number(text):
    return float(str(text).replace("lb", "").strip())


def dust_level(dustiness):
    """Turn a dustiness percentage into plain words."""
    if dustiness < 10:
        return "Clean"
    if dustiness < 30:
        return "Slightly dusty"
    if dustiness < 50:
        return "Dusty"
    return "Very dusty"


def load_courts(path=DATA_DIR / "court_data.csv"):
    rows = list(csv.reader(open(path, newline="")))
    clean_friction, shoe_weight = 3.25, 3.0
    for row in rows:
        if row and row[0].strip() == "Friction Clean":
            clean_friction = _number(row[1])
            shoe_weight = _number(row[4])

    groups = []
    basketball_count = 0
    for row in rows[1:]:
        court_id = row[0].strip() if row else ""
        if not court_id or court_id == "Friction Clean":
            if groups and not court_id:
                break
            continue

        court_type = row[1].strip()
        if court_type:  # first row of a new group holds the data
            if court_type == "Basketball":
                basketball_count += 1
                court_type = "Basketball " + "AB"[basketball_count - 1]
            group = {"name": court_type, "courts": [], "samples": 0, "times": {}}
            for t, (d, f, c) in TIME_COLUMNS.items():
                friction = _number(row[f])
                dustiness = max(0.0, min(100.0, (clean_friction - friction) / clean_friction * 100))
                group["times"][t] = {
                    "discoloration": _number(row[d]),
                    "friction": friction,
                    "coef": _number(row[c]),
                    "dustiness": round(dustiness),
                    "level": dust_level(dustiness),
                    "measured": t in MEASURED_TIMES,
                }
            groups.append(group)

        group = groups[-1]
        group["courts"].append(court_id)
        group["samples"] += int(row[2] or 0)

    for g in groups:
        first, last = g["courts"][0], g["courts"][-1]
        g["court_label"] = f"Court {first}" if first == last else f"Courts {first}–{last}"
        g["avg_dustiness"] = round(sum(t["dustiness"] for t in g["times"].values()) / len(TIMES))
        g["avg_level"] = dust_level(g["avg_dustiness"])
        g["best_time"] = min(TIMES, key=lambda t: g["times"][t]["dustiness"])
        g["worst_time"] = max(TIMES, key=lambda t: g["times"][t]["dustiness"])

    return {"courts": groups, "clean_friction": clean_friction, "shoe_weight": shoe_weight}
