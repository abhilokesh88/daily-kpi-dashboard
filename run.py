#!/usr/bin/env python3
"""
Main entry point — run this daily (locally or via GitHub Actions).

1. Fetch yesterday's KPIs from GA4, Shopify, Meta, QuickBooks
2. Save to CSV history
3. Generate trend charts
4. Build the HTML dashboard
5. Post summary to Slack
"""

from src import fetch_ga4, fetch_shopify, fetch_meta, fetch_quickbooks
from src import storage, charts, slack_notify, build_dashboard


def main():
    print("=== Daily KPI Dashboard ===\n")

    # 1. Fetch data
    print("[1/5] Fetching data...")
    ga4_data = fetch_ga4.fetch()
    shopify_data = fetch_shopify.fetch()
    meta_data = fetch_meta.fetch()
    qb_data = fetch_quickbooks.fetch()

    # 2. Save to history
    print("\n[2/5] Saving to history...")
    storage.save(ga4_data, shopify_data, meta_data, qb=qb_data)

    # 3. Load full history & generate charts
    print("\n[3/5] Generating charts...")
    history = storage.load_history()
    charts.generate_all(history)

    # 4. Build HTML dashboard
    print("\n[4/5] Building dashboard...")
    build_dashboard.build(ga4_data, shopify_data, meta_data, history, qb=qb_data)

    # 5. Post to Slack
    print("\n[5/5] Sending Slack notification...")
    slack_notify.send(ga4_data, shopify_data, meta_data, qb=qb_data)

    print("\nDone!")


if __name__ == "__main__":
    main()
