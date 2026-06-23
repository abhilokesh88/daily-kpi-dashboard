"""
Generate trend charts from historical KPI data.

Outputs PNG images into docs/assets/ so the HTML dashboard can display them.
"""

import os

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

from src.config import OUTPUT_DIR


ASSETS_DIR = os.path.join(OUTPUT_DIR, "assets")


def generate_all(history: list[dict]) -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)

    if len(history) < 2:
        print("  [Charts] Not enough data for trend charts yet (need 2+ days).")
        return

    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in history]

    chart_configs = [
        {
            "filename": "sessions.png",
            "title": "Sessions (GA4)",
            "values": [r["ga4_sessions"] for r in history],
            "color": "#4285F4",
        },
        {
            "filename": "orders.png",
            "title": "Orders (Shopify)",
            "values": [r["shopify_orders"] for r in history],
            "color": "#96BF48",
        },
        {
            "filename": "revenue.png",
            "title": "Revenue (Shopify)",
            "values": [r["shopify_revenue"] for r in history],
            "color": "#5E8E3E",
        },
        {
            "filename": "ad_spend.png",
            "title": "Ad Spend (Meta)",
            "values": [r["meta_spend"] for r in history],
            "color": "#1877F2",
        },
        {
            "filename": "cvr.png",
            "title": "CVR — Orders / Sessions (%)",
            "values": [
                round(r["shopify_orders"] / r["ga4_sessions"] * 100, 2)
                if r["ga4_sessions"] else 0
                for r in history
            ],
            "color": "#2CA01C",
        },
    ]

    for cfg in chart_configs:
        _render_chart(dates, cfg)

    print(f"  [Charts] Generated {len(chart_configs)} trend charts.")


def _render_chart(dates: list, cfg: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 3))

    ax.plot(dates, cfg["values"], color=cfg["color"], linewidth=2, marker="o", markersize=4)
    ax.fill_between(dates, cfg["values"], alpha=0.1, color=cfg["color"])

    ax.set_title(cfg["title"], fontsize=14, fontweight="bold", pad=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()

    path = os.path.join(ASSETS_DIR, cfg["filename"])
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
