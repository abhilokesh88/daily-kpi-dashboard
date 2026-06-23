"""
Send a daily KPI summary to Slack via an Incoming Webhook.
"""

import json

import requests

from src.config import SLACK_WEBHOOK_URL


def send(ga4: dict, shopify: dict, meta: dict) -> None:
    if not SLACK_WEBHOOK_URL:
        print("  [Slack] Skipped — webhook URL not configured.")
        return

    report_date = ga4.get("date") or shopify.get("date") or meta.get("date") or "N/A"

    sessions = ga4.get("sessions", 0)
    orders = shopify.get("orders", 0)
    cvr = round(orders / sessions * 100, 2) if sessions else 0.0
    new_cust = shopify.get("new_customers", 0)
    ret_cust = shopify.get("returning_customers", 0)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Daily KPI Report — {report_date}"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*:dart: Central Command*\n"
                    f">  Sessions: *{sessions:,}* (GA4)\n"
                    f">  Orders: *{orders:,}* (Shopify)\n"
                    f">  Revenue: *${shopify.get('revenue', 0):,.2f}* (Shopify)\n"
                    f">  Ad Spend: *${meta.get('spend', 0):,.2f}* (Meta)\n"
                    f">  CVR: *{cvr:.2f}%* (Orders/Sessions)"
                ),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*:busts_in_silhouette: Customers*\n"
                    f">  New: *{new_cust}*  |  Returning: *{ret_cust}*"
                ),
            },
        },
    ]

    payload = {"blocks": blocks}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
    resp.raise_for_status()
    print("  [Slack] Message sent.")
