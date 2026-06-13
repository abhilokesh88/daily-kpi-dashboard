"""
Generate the static HTML dashboard from the latest data + history.

Outputs docs/index.html which GitHub Pages serves automatically.
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.config import OUTPUT_DIR, TEMPLATE_DIR


def build(ga4: dict, shopify: dict, meta: dict, history: list[dict], qb: dict | None = None) -> None:
    """Render the dashboard HTML from the Jinja2 template."""
    qb = qb or {}
    os.makedirs(os.path.join(OUTPUT_DIR, "assets"), exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("dashboard.html")

    html = template.render(
        report_date=ga4.get("date") or shopify.get("date") or meta.get("date") or "N/A",
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        ga4=ga4,
        shopify=shopify,
        meta=meta,
        qb=qb,
        history=history,
        has_trends=len(history) >= 2,
    )

    out_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"  [Dashboard] Written to {out_path}")
