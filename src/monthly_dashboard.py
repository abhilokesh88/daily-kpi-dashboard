"""
Build the monthly financials page at docs/monthly.html.
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.config import OUTPUT_DIR, TEMPLATE_DIR


def build_monthly(qb: dict) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("monthly.html")

    revenue = qb.get("revenue", 0)
    expenses = qb.get("expenses", 0)
    net_income = qb.get("net_income", 0)
    margin = (net_income / revenue * 100) if revenue else 0

    html = template.render(
        month_label=qb.get("month_label", "N/A"),
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        revenue=revenue,
        expenses=expenses,
        net_income=net_income,
        margin=margin,
    )

    out_path = os.path.join(OUTPUT_DIR, "monthly.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"  [Monthly] Written to {out_path}")
