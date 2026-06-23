"""
CSV storage for the daily performance log.

Separate from the main history.csv — stores raw inputs and calculated KPIs
so the performance page can render a running table.
"""

import csv
import os

from src.config import DATA_DIR

PERF_FILE = os.path.join(DATA_DIR, "performance_log.csv")

FIELDS = [
    "date",
    # Shopify
    "revenue", "orders",
    # GA4
    "sessions", "atc",
    # Meta
    "spend", "purchases", "meta_revenue", "impressions", "reach",
    "link_clicks", "video_3s", "video_25",
    # Calculated — Economics
    "mer", "cpp", "ctr", "cvr", "atc_rate",
    # Calculated — Funnel
    "frequency", "cpm", "cpc",
    # Calculated — Creative
    "hook_rate", "hold_rate",
]


def save(date_str: str, raw: dict, kpis: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    existing = load_history()
    existing = [r for r in existing if r.get("date") != date_str]

    new_row = {"date": date_str}
    new_row.update(raw)
    new_row.update(kpis)
    existing.append(new_row)

    with open(PERF_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(existing)

    print(f"  [PerfLog] Saved row for {date_str}.")


def load_history() -> list[dict]:
    if not os.path.isfile(PERF_FILE):
        return []

    with open(PERF_FILE, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        for key in row:
            if key == "date":
                continue
            try:
                row[key] = float(row[key])
            except (ValueError, TypeError):
                row[key] = 0.0

    return rows
