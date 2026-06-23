"""
Build the Meta Ads Daily Performance page at docs/meta-ads.html.

Calculates derived KPIs from raw GA4, Shopify, and Meta data:
  MER, CPP, CTR, Frequency, CPC, CPM, Hook Rate, Hold Rate
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from src.config import OUTPUT_DIR, TEMPLATE_DIR
from src import performance_storage


def build_meta_ads(ga4: dict, shopify: dict, meta: dict) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    sessions = ga4.get("sessions", 0)
    orders = shopify.get("orders", 0)
    revenue = shopify.get("revenue", 0)
    atc = ga4.get("add_to_carts", 0)

    spend = meta.get("spend", 0)
    purchases = meta.get("purchases", 0)
    impressions = meta.get("impressions", 0)
    reach = meta.get("reach", 0)
    link_clicks = meta.get("link_clicks", 0)
    video_3s = meta.get("video_plays_3s", 0)
    video_25 = meta.get("video_plays_25", 0)

    kpis = {
        "mer": round(revenue / spend, 2) if spend else 0,
        "cpp": round(spend / orders, 2) if orders else 0,
        "ctr": round(link_clicks / impressions * 100, 2) if impressions else 0,
        "cvr": round(orders / sessions * 100, 2) if sessions else 0,
        "atc_rate": round(atc / sessions * 100, 2) if sessions else 0,
        "frequency": round(impressions / reach, 1) if reach else 0,
        "cpm": round(spend / impressions * 1000, 2) if impressions else 0,
        "cpc": round(spend / link_clicks, 2) if link_clicks else 0,
        "hook_rate": round(video_3s / impressions * 100, 1) if impressions else 0,
        "hold_rate": round(video_25 / video_3s * 100, 1) if video_3s else 0,
    }

    raw = {
        "sessions": sessions,
        "orders": orders,
        "revenue": revenue,
        "atc": atc,
        "spend": spend,
        "purchases": purchases,
        "impressions": impressions,
        "reach": reach,
        "link_clicks": link_clicks,
        "video_3s": video_3s,
        "video_25": video_25,
    }

    report_date = ga4.get("date") or shopify.get("date") or meta.get("date") or "N/A"

    performance_storage.save(report_date, raw, kpis)
    history = performance_storage.load_history()

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("meta-ads.html")

    html = template.render(
        report_date=report_date,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        kpis=kpis,
        raw=raw,
        history=history,
    )

    out_path = os.path.join(OUTPUT_DIR, "meta-ads.html")
    with open(out_path, "w") as f:
        f.write(html)

    print(f"  [Meta Ads] Written to {out_path}")
