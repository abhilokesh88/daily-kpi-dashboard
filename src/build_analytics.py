"""
Build the GA4 analytics page at docs/analytics.html.

Sections:
  1. Paid Ad CVR — ad content × medium breakdown
  2. Comprehensive GA4 summary — site totals + channel mix
  3. GA4 trend table — daily history
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.config import OUTPUT_DIR, TEMPLATE_DIR
from src import ga4_storage


def build_analytics(ga4_summary: dict, ad_performance: list[dict]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ga4_storage.save(ga4_summary)
    history = ga4_storage.load_history()

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("analytics.html")

    html = template.render(
        report_date=ga4_summary.get("date", "N/A"),
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        summary=ga4_summary,
        ad_rows=ad_performance,
        channels=ga4_summary.get("channels", []),
        history=history,
    )

    out_path = os.path.join(OUTPUT_DIR, "analytics.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"  [Analytics] Written to {out_path}")
