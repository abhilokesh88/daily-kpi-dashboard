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
    """Create all trend charts from the history data."""
    os.makedirs(ASSETS_DIR, exist_ok=True)

    if len(history) < 2:
        print("  [Charts] Not enough data for trend charts yet (need 2+ days).")
        return

    dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in history]

    chart_configs = [
        {
            "filename": "ga4_sessions.png",
            "title": "GA4 — Sessions",
            "values": [r["ga4_sessions"] for r in history],
            "color": "#4285F4",
            "fmt": "{:,.0f}",
        },
        {
            "filename": "ga4_conversion_rate.png",
            "title": "GA4 — Conversion Rate (%)",
            "values": [r["ga4_conversion_rate"] for r in history],
            "color": "#34A853",
            "fmt": "{:.2f}%",
        },
        {
            "filename": "ga4_revenue.png",
            "title": "GA4 — Revenue ($)",
            "values": [r["ga4_revenue"] for r in history],
            "color": "#0F9D58",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "shopify_orders.png",
            "title": "Shopify — Orders",
            "values": [r["shopify_orders"] for r in history],
            "color": "#96BF48",
            "fmt": "{:,.0f}",
        },
        {
            "filename": "shopify_revenue.png",
            "title": "Shopify — Revenue ($)",
            "values": [r["shopify_revenue"] for r in history],
            "color": "#5E8E3E",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "shopify_aov.png",
            "title": "Shopify — AOV ($)",
            "values": [r["shopify_aov"] for r in history],
            "color": "#7AB648",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "meta_spend.png",
            "title": "Meta — Ad Spend ($)",
            "values": [r["meta_spend"] for r in history],
            "color": "#1877F2",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "meta_roas.png",
            "title": "Meta — ROAS",
            "values": [r["meta_roas"] for r in history],
            "color": "#42B72A",
            "fmt": "{:.2f}x",
        },
        {
            "filename": "meta_cpa.png",
            "title": "Meta — CPA ($)",
            "values": [r["meta_cpa"] for r in history],
            "color": "#F7B928",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "qb_revenue.png",
            "title": "QuickBooks — Revenue ($)",
            "values": [r.get("qb_revenue", 0) for r in history],
            "color": "#2CA01C",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "qb_expenses.png",
            "title": "QuickBooks — Expenses ($)",
            "values": [r.get("qb_expenses", 0) for r in history],
            "color": "#D94B38",
            "fmt": "${:,.2f}",
        },
        {
            "filename": "qb_net_income.png",
            "title": "QuickBooks — Net Income ($)",
            "values": [r.get("qb_net_income", 0) for r in history],
            "color": "#393B79",
            "fmt": "${:,.2f}",
        },
    ]

    for cfg in chart_configs:
        _render_chart(dates, cfg)

    print(f"  [Charts] Generated {len(chart_configs)} trend charts.")


def _render_chart(dates: list, cfg: dict) -> None:
    """Render a single trend line chart."""
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
