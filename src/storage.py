"""
Simple CSV-based storage for daily KPIs.

Each day's data is written to data/history.csv with deduplication
so we accumulate a trend over time. The dashboard reads this file to draw charts.
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
    "ga4_atc",
    # Shopify
    "shopify_orders",
    "shopify_revenue",
    "shopify_aov",
    "shopify_new_customers",
    "shopify_returning_customers",
    # Meta
    "meta_spend",
    "meta_purchases",
    "meta_roas",
    "meta_cpa",
]


def save(ga4: dict, shopify: dict, meta: dict) -> None:
    date_str = ga4.get("date") or shopify.get("date") or meta.get("date") or str(date.today())

    row = {
        "date": date_str,
        "ga4_sessions": ga4.get("sessions", 0),
        "ga4_conversion_rate": ga4.get("conversion_rate", 0),
        "ga4_revenue": ga4.get("revenue", 0),
        "ga4_atc": ga4.get("add_to_carts", 0),
        "shopify_orders": shopify.get("orders", 0),
        "shopify_revenue": shopify.get("revenue", 0),
        "shopify_aov": shopify.get("aov", 0),
        "shopify_new_customers": shopify.get("new_customers", 0),
        "shopify_returning_customers": shopify.get("returning_customers", 0),
        "meta_spend": meta.get("spend", 0),
        "meta_purchases": meta.get("purchases", 0),
        "meta_roas": meta.get("roas", 0),
        "meta_cpa": meta.get("cpa", 0),
    }

    os.makedirs(DATA_DIR, exist_ok=True)

    existing = load_history()
    existing = [r for r in existing if r.get("date") != date_str]
    existing.append(row)

    with open(HISTORY_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(existing)

    print(f"  [Storage] Saved row for {date_str}.")


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
