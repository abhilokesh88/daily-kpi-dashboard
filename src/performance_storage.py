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
    "spend", "purchases", "impressions", "reach",
    "link_clicks", "video_3s", "video_25",
    # Calculated — Economics
    "mer", "cpp", "ctr", "cvr", "atc_rate",
    # Calculated — Funnel
    "frequency", "cpm", "cpc",
    # Calculated — Creative
    "hook_rate", "hold_rate",
]


def save(date_str: str, raw: dict, kpis: dict) -> None:
    file_exists = os.path.isfile(PERF_FILE)
    os.makedirs(DATA_DIR, exist_ok=True)

    row = {"date": date_str}
    row.update(raw)
    row.update(kpis)

    with open(PERF_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

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
