"""
CSV storage for comprehensive GA4 daily summary metrics.
"""

import csv
import os

from src.config import DATA_DIR

GA4_FILE = os.path.join(DATA_DIR, "ga4_summary.csv")

FIELDS = [
    "date",
    "total_users", "new_users", "sessions", "pageviews",
    "pages_per_session", "bounce_rate", "avg_duration",
    "add_to_carts", "purchases", "revenue", "cvr",
]


def save(summary: dict) -> None:
    file_exists = os.path.isfile(GA4_FILE)
    os.makedirs(DATA_DIR, exist_ok=True)

    row = {f: summary.get(f, 0) for f in FIELDS}

    with open(GA4_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"  [GA4 Log] Saved summary for {row['date']}.")


def load_history() -> list[dict]:
    if not os.path.isfile(GA4_FILE):
        return []

    with open(GA4_FILE, newline="") as f:
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
