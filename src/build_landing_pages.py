"""
Build the landing page performance page at docs/landing-pages.html.

Embeds all historical data as JSON so the page can filter
by date range entirely client-side.
"""

import json
import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.config import OUTPUT_DIR, TEMPLATE_DIR
from src import landing_page_storage


def build_landing_pages(lp_rows: list[dict]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    landing_page_storage.save(lp_rows)
    all_data = landing_page_storage.load_all()

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("landing-pages.html")

    report_date = lp_rows[0]["date"] if lp_rows else "N/A"

    html = template.render(
        report_date=report_date,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        all_data_json=json.dumps(all_data),
    )

    out_path = os.path.join(OUTPUT_DIR, "landing-pages.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"  [Landing Pages] Written to {out_path}")
