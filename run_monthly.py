#!/usr/bin/env python3
"""
Monthly financial report — runs on the 7th of each month.

Pulls the previous month's P&L from QuickBooks, sends a Slack summary,
and builds a monthly financials page on the dashboard site.
"""

from datetime import date

from src import fetch_quickbooks
from src.monthly_slack import send_monthly
from src.monthly_dashboard import build_monthly


def main():
    today = date.today()
    if today.month == 1:
        target_year, target_month = today.year - 1, 12
    else:
        target_year, target_month = today.year, today.month - 1

    print(f"=== Monthly Financial Report — {date(target_year, target_month, 1).strftime('%B %Y')} ===\n")

    print("[1/3] Fetching QuickBooks P&L...")
    qb_data = fetch_quickbooks.fetch_month(target_year, target_month)

    print("\n[2/3] Building monthly dashboard page...")
    build_monthly(qb_data)

    print("\n[3/3] Sending Slack notification...")
    send_monthly(qb_data)

    print("\nDone!")


if __name__ == "__main__":
    main()
