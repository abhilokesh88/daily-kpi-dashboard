"""
Generate the Daily Central Command Dashboard at docs/index.html.

Shows the core marketing KPIs, trend charts, and a daily performance log.
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.config import OUTPUT_DIR, TEMPLATE_DIR


def build(ga4: dict, shopify: dict, meta: dict, history: list[dict]) -> None:
    os.makedirs(os.path.join(OUTPUT_DIR, "assets"), exist_ok=True)

    sessions = ga4.get("sessions", 0)
    orders = shopify.get("orders", 0)
    atc = ga4.get("add_to_carts", 0)
    meta_spend = meta.get("spend", 0)
    meta_purchases = meta.get("purchases", 0)
    cvr = round(orders / sessions * 100, 2) if sessions else 0.0
    atc_to_purchase = round(orders / atc * 100, 2) if atc else 0.0
    cpp = round(meta_spend / meta_purchases, 2) if meta_purchases else 0.0

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("dashboard.html")

    html = template.render(
        report_date=ga4.get("date") or shopify.get("date") or meta.get("date") or "N/A",
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        sessions=sessions,
        orders=orders,
        revenue=shopify.get("revenue", 0),
        ad_spend=meta_spend,
        cpp=cpp,
        cvr=cvr,
        atc=atc,
        atc_to_purchase=atc_to_purchase,
        new_customers=shopify.get("new_customers", 0),
        returning_customers=shopify.get("returning_customers", 0),
        history=history,
        has_trends=len(history) >= 2,
    )

    out_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"  [Dashboard] Written to {out_path}")
