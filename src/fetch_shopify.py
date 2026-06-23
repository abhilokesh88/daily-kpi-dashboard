"""
Pull yesterday's KPIs from Shopify Admin API (REST).

Metrics:
  - Orders, Revenue, AOV
  - New vs Returning customers
"""

from datetime import date, datetime, timedelta, timezone

import requests

from src.config import SHOPIFY_ACCESS_TOKEN, SHOPIFY_STORE_URL


def fetch(target_date: date | None = None) -> dict:
    if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
        print("  [Shopify] Skipped — credentials not configured.")
        return _empty()

    target = target_date or date.today() - timedelta(days=1)
    start = datetime.combine(target, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-10/orders.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
    params = {
        "status": "any",
        "created_at_min": start.isoformat(),
        "created_at_max": end.isoformat(),
        "limit": 250,
        "fields": "id,total_price,customer",
    }

    all_orders: list[dict] = []
    while url:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        all_orders.extend(data.get("orders", []))
        url = _next_page_url(resp)
        params = {}

    order_count = len(all_orders)
    revenue = sum(float(o.get("total_price", 0)) for o in all_orders)
    aov = (revenue / order_count) if order_count > 0 else 0.0

    new_customers = 0
    returning_customers = 0
    for o in all_orders:
        customer = o.get("customer", {})
        if customer:
            orders_count = customer.get("orders_count", 1)
            if orders_count <= 1:
                new_customers += 1
            else:
                returning_customers += 1
        else:
            new_customers += 1

    return {
        "date": target.strftime("%Y-%m-%d"),
        "orders": order_count,
        "revenue": round(revenue, 2),
        "aov": round(aov, 2),
        "new_customers": new_customers,
        "returning_customers": returning_customers,
    }


def _next_page_url(resp: requests.Response) -> str | None:
    link = resp.headers.get("Link", "")
    for part in link.split(","):
        if 'rel="next"' in part:
            return part.split(";")[0].strip().strip("<>")
    return None


def _empty(date_str: str = "") -> dict:
    return {
        "date": date_str,
        "orders": 0,
        "revenue": 0.0,
        "aov": 0.0,
        "new_customers": 0,
        "returning_customers": 0,
    }
