"""
Send a daily KPI summary to Slack via an Incoming Webhook.
"""

import json

import requests

from src.config import SLACK_WEBHOOK_URL


def send(ga4: dict, shopify: dict, meta: dict, qb: dict | None = None) -> None:
    """Post a formatted KPI summary to Slack."""
    qb = qb or {}

    if not SLACK_WEBHOOK_URL:
        print("  [Slack] Skipped — webhook URL not configured.")
        return

    report_date = ga4.get("date") or shopify.get("date") or meta.get("date") or "N/A"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Daily KPI Report — {report_date}"},
        },
        {"type": "divider"},
        # --- GA4 ---
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*:bar_chart: Google Analytics*\n"
                    f">  Sessions: *{ga4.get('sessions', 0):,}*\n"
                    f">  Conversion Rate: *{ga4.get('conversion_rate', 0):.2f}%*\n"
                    f">  Revenue: *${ga4.get('revenue', 0):,.2f}*"
                ),
            },
        },
        {"type": "divider"},
        # --- Shopify ---
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*:shopping_bags: Shopify*\n"
                    f">  Orders: *{shopify.get('orders', 0):,}*\n"
                    f">  Revenue: *${shopify.get('revenue', 0):,.2f}*\n"
                    f">  AOV: *${shopify.get('aov', 0):,.2f}*"
                ),
            },
        },
        {"type": "divider"},
        # --- Meta ---
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*:mega: Meta Ads*\n"
                    f">  Spend: *${meta.get('spend', 0):,.2f}*\n"
                    f">  ROAS: *{meta.get('roas', 0):.2f}x*\n"
                    f">  CPA: *${meta.get('cpa', 0):,.2f}*"
                ),
            },
        },
        {"type": "divider"},
        # --- QuickBooks ---
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*:ledger: QuickBooks*\n"
                    f">  Revenue: *${qb.get('revenue', 0):,.2f}*\n"
                    f">  Expenses: *${qb.get('expenses', 0):,.2f}*\n"
                    f">  Net Income: *${qb.get('net_income', 0):,.2f}*"
                ),
            },
        },
    ]

    payload = {"blocks": blocks}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
    resp.raise_for_status()
    print("  [Slack] Message sent.")
