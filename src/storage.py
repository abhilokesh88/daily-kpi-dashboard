"""
Simple CSV-based storage for daily KPIs.

Each day's data is appended to data/history.csv so we accumulate
a trend over time. The dashboard reads this file to draw charts.
"""

import csv
import os
from datetime import date

from src.config import DATA_DIR

HISTORY_FILE = os.path.join(DATA_DIR, "history.csv")

FIELDS = [
    "date",
    # GA4
    "ga4_sessions",
    "ga4_conversion_rate",
    "ga4_revenue",
    # Shopify
    "shopify_orders",
    "shopify_revenue",
    "shopify_aov",
    # Meta
    "meta_spend",
    "meta_roas",
    "meta_cpa",
]


def save(ga4: dict, shopify: dict, meta: dict) -> None:
    """Append one row to the history CSV."""
    file_exists = os.path.isfile(HISTORY_FILE)

    row = {
        "date": ga4.get("date") or shopify.get("date") or meta.get("date") or str(date.today()),
        "ga4_sessions": ga4.get("sessions", 0),
        "ga4_conversion_rate": ga4.get("conversion_rate", 0),
        "ga4_revenue": ga4.get("revenue", 0),
        "shopify_orders": shopify.get("orders", 0),
        "shopify_revenue": shopify.get("revenue", 0),
        "shopify_aov": shopify.get("aov", 0),
        "meta_spend": meta.get("spend", 0),
        "meta_roas": meta.get("roas", 0),
        "meta_cpa": meta.get("cpa", 0),
    }

    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"  [Storage] Saved row for {row['date']}.")


def load_history() -> list[dict]:
    """Read all historical rows. Returns list of dicts, oldest first."""
    if not os.path.isfile(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Convert numeric fields
    for row in rows:
        for key in row:
            if key == "date":
                continue
            try:
                row[key] = float(row[key])
            except (ValueError, TypeError):
                row[key] = 0.0

    return rows
