"""
Pull yesterday's KPIs from Meta (Facebook) Marketing API.

Metrics:
  - Ad Spend
  - ROAS (Return on Ad Spend)
  - CPA  (Cost per Acquisition / Purchase)
"""

from datetime import date, timedelta

import requests

from src.config import META_ACCESS_TOKEN, META_AD_ACCOUNT_ID


API_VERSION = "v20.0"


def fetch(target_date: date | None = None) -> dict:
    """Return a dict with spend, roas, cpa for *target_date*."""

    if not META_ACCESS_TOKEN or not META_AD_ACCOUNT_ID:
        print("  [Meta] Skipped — credentials not configured.")
        return _empty()

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    url = (
        f"https://graph.facebook.com/{API_VERSION}/"
        f"{META_AD_ACCOUNT_ID}/insights"
    )
    params = {
        "access_token": META_ACCESS_TOKEN,
        "time_range": f'{{"since":"{date_str}","until":"{date_str}"}}',
        "fields": "spend,purchase_roas,actions,action_values,impressions,reach,inline_link_clicks,video_play_actions,video_p25_watched_actions",
        "level": "account",
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    if not data:
        print(f"  [Meta] No data for {date_str}.")
        return _empty(date_str)

    row = data[0]
    spend = float(row.get("spend", 0))
    impressions = int(row.get("impressions", 0))
    reach = int(row.get("reach", 0))
    link_clicks = int(row.get("inline_link_clicks", 0))

    roas_list = row.get("purchase_roas", [])
    roas = float(roas_list[0]["value"]) if roas_list else 0.0

    purchases = _extract_action_value(row.get("actions", []), "purchase")
    cpa = (spend / purchases) if purchases > 0 else 0.0

    video_plays_3s = _extract_action_value(row.get("video_play_actions", []), "video_view")
    video_plays_25 = _extract_action_value(row.get("video_p25_watched_actions", []), "video_view")

    purchase_value = _extract_action_float(row.get("action_values", []), "purchase")
    meta_revenue = round(purchase_value, 2) if purchase_value else round(spend * roas, 2)

    return {
        "date": date_str,
        "spend": round(spend, 2),
        "roas": round(roas, 2),
        "cpa": round(cpa, 2),
        "purchases": purchases,
        "revenue": meta_revenue,
        "impressions": impressions,
        "reach": reach,
        "link_clicks": link_clicks,
        "video_plays_3s": video_plays_3s,
        "video_plays_25": video_plays_25,
    }


# --- helpers ---------------------------------------------------------------

def _extract_action_value(actions: list[dict], action_type: str) -> int:
    for action in actions:
        if action.get("action_type") == action_type:
            return int(action.get("value", 0))
    return 0


def _extract_action_float(actions: list[dict], action_type: str) -> float:
    for action in actions:
        if action.get("action_type") == action_type:
            return float(action.get("value", 0))
    return 0.0


def _empty(date_str: str = "") -> dict:
    return {
        "date": date_str,
        "spend": 0.0,
        "roas": 0.0,
        "cpa": 0.0,
        "purchases": 0,
        "revenue": 0.0,
        "impressions": 0,
        "reach": 0,
        "link_clicks": 0,
        "video_plays_3s": 0,
        "video_plays_25": 0,
    }
