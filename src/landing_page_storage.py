"""
JSON storage for daily landing page performance data.

Uses JSON instead of CSV so the data can be embedded directly
in the HTML page for client-side date range filtering.
"""

import json
import os

from src.config import DATA_DIR

LP_FILE = os.path.join(DATA_DIR, "landing_pages.json")


def save(rows: list[dict]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    existing = load_all()

    if rows:
        new_date = rows[0].get("date", "")
        existing = [r for r in existing if r.get("date") != new_date]
        existing.extend(rows)

    with open(LP_FILE, "w") as f:
        json.dump(existing, f)

    print(f"  [LP Store] Saved {len(rows)} landing page rows.")


def load_all() -> list[dict]:
    if not os.path.isfile(LP_FILE):
        return []

    with open(LP_FILE) as f:
        return json.load(f)
