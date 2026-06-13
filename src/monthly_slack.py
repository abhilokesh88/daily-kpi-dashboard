"""
Send the monthly QuickBooks P&L summary to Slack.
"""

import requests

from src.config import SLACK_WEBHOOK_URL


def send_monthly(qb: dict) -> None:
    if not SLACK_WEBHOOK_URL:
        print("  [Slack] Skipped — webhook URL not configured.")
        return

    month_label = qb.get("month_label", "N/A")
    revenue = qb.get("revenue", 0)
    expenses = qb.get("expenses", 0)
    net_income = qb.get("net_income", 0)

    margin = (net_income / revenue * 100) if revenue else 0

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Monthly P&L — {month_label}"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*:ledger: QuickBooks P&L Summary*\n\n"
                    f">  *Revenue:*  ${revenue:,.2f}\n"
                    f">  *Expenses:*  ${expenses:,.2f}\n"
                    f">  *Net Income:*  ${net_income:,.2f}\n"
                    f">  *Margin:*  {margin:.1f}%"
                ),
            },
        },
    ]

    payload = {"blocks": blocks}
    resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
    resp.raise_for_status()
    print("  [Slack] Monthly report sent.")
