"""
Pull yesterday's KPIs from Google Analytics 4.

Three fetch modes:
  fetch()              — core daily KPIs (sessions, CVR, revenue, ATC)
  fetch_ad_performance() — paid ad CVR by ad content × medium
  fetch_summary()      — comprehensive site-wide + channel breakdown
"""

import json
import os
import tempfile
from datetime import date, timedelta

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy,
)

from src.config import GA4_CREDENTIALS_JSON, GA4_PROPERTY_ID


def _get_client():
    if not GA4_PROPERTY_ID or not GA4_CREDENTIALS_JSON:
        return None
    creds_path = _write_temp_credentials()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    return BetaAnalyticsDataClient()


def fetch(target_date: date | None = None) -> dict:
    """Core daily KPIs: sessions, conversion_rate, revenue, add_to_carts."""

    client = _get_client()
    if not client:
        print("  [GA4] Skipped — credentials not configured.")
        return _empty()

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        metrics=[
            Metric(name="sessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
            Metric(name="addToCarts"),
        ],
    )

    response = client.run_report(request)

    if not response.rows:
        print(f"  [GA4] No data for {date_str}.")
        return _empty(date_str)

    row = response.rows[0]
    sessions = int(row.metric_values[0].value)
    purchases = int(row.metric_values[1].value)
    revenue = float(row.metric_values[2].value)
    add_to_carts = int(row.metric_values[3].value)
    conversion_rate = (purchases / sessions * 100) if sessions > 0 else 0.0

    return {
        "date": date_str,
        "sessions": sessions,
        "conversion_rate": round(conversion_rate, 2),
        "revenue": round(revenue, 2),
        "add_to_carts": add_to_carts,
    }


def fetch_ad_performance(target_date: date | None = None) -> list[dict]:
    """Paid Ad CVR: sessions, purchases, LP CVR by ad content × medium."""

    client = _get_client()
    if not client:
        return []

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[
            Dimension(name="sessionManualAdContent"),
            Dimension(name="firstUserMedium"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="ecommercePurchases"),
        ],
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True),
        ],
        limit=25,
    )

    response = client.run_report(request)
    rows = []
    for row in response.rows:
        sessions = int(row.metric_values[0].value)
        purchases = int(row.metric_values[1].value)
        cvr = round(purchases / sessions * 100, 2) if sessions > 0 else 0.0
        rows.append({
            "ad_content": row.dimension_values[0].value,
            "medium": row.dimension_values[1].value,
            "sessions": sessions,
            "purchases": purchases,
            "lp_cvr": cvr,
        })

    print(f"  [GA4] Ad performance: {len(rows)} rows for {date_str}.")
    return rows


def fetch_summary(target_date: date | None = None) -> dict:
    """Comprehensive GA4 summary: site totals + channel breakdown."""

    client = _get_client()
    if not client:
        return _empty_summary()

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    summary_metrics = [
        Metric(name="totalUsers"),
        Metric(name="newUsers"),
        Metric(name="sessions"),
        Metric(name="screenPageViews"),
        Metric(name="bounceRate"),
        Metric(name="averageSessionDuration"),
        Metric(name="addToCarts"),
        Metric(name="ecommercePurchases"),
        Metric(name="purchaseRevenue"),
    ]

    totals_req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        metrics=summary_metrics,
    )

    totals_resp = client.run_report(totals_req)

    if not totals_resp.rows:
        print(f"  [GA4] No summary data for {date_str}.")
        return _empty_summary(date_str)

    r = totals_resp.rows[0]
    total_users = int(r.metric_values[0].value)
    new_users = int(r.metric_values[1].value)
    sessions = int(r.metric_values[2].value)
    pageviews = int(r.metric_values[3].value)
    bounce_rate = float(r.metric_values[4].value)
    avg_duration = float(r.metric_values[5].value)
    add_to_carts = int(r.metric_values[6].value)
    purchases = int(r.metric_values[7].value)
    revenue = float(r.metric_values[8].value)

    channel_req = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
            Metric(name="bounceRate"),
        ],
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True),
        ],
        limit=15,
    )

    channel_resp = client.run_report(channel_req)
    channels = []
    for row in channel_resp.rows:
        ch_sessions = int(row.metric_values[0].value)
        ch_users = int(row.metric_values[1].value)
        ch_purchases = int(row.metric_values[2].value)
        ch_revenue = float(row.metric_values[3].value)
        ch_bounce = float(row.metric_values[4].value)
        ch_cvr = round(ch_purchases / ch_sessions * 100, 2) if ch_sessions > 0 else 0.0
        channels.append({
            "channel": row.dimension_values[0].value,
            "sessions": ch_sessions,
            "users": ch_users,
            "purchases": ch_purchases,
            "revenue": round(ch_revenue, 2),
            "bounce_rate": round(ch_bounce * 100, 1),
            "cvr": ch_cvr,
        })

    cvr = round(purchases / sessions * 100, 2) if sessions > 0 else 0.0
    pages_per_session = round(pageviews / sessions, 1) if sessions > 0 else 0.0

    return {
        "date": date_str,
        "total_users": total_users,
        "new_users": new_users,
        "sessions": sessions,
        "pageviews": pageviews,
        "pages_per_session": pages_per_session,
        "bounce_rate": round(bounce_rate * 100, 1),
        "avg_duration": round(avg_duration, 1),
        "add_to_carts": add_to_carts,
        "purchases": purchases,
        "revenue": round(revenue, 2),
        "cvr": cvr,
        "channels": channels,
    }


# --- helpers ---------------------------------------------------------------

def fetch_landing_pages(target_date: date | None = None) -> list[dict]:
    """Landing page performance: sessions, users, purchases, revenue, CVR."""

    client = _get_client()
    if not client:
        return []

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        dimensions=[Dimension(name="landingPage")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="newUsers"),
            Metric(name="averageSessionDuration"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
        ],
        order_bys=[
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True),
        ],
        limit=50,
    )

    response = client.run_report(request)
    rows = []
    for row in response.rows:
        sessions = int(row.metric_values[0].value)
        active_users = int(row.metric_values[1].value)
        new_users = int(row.metric_values[2].value)
        avg_duration = float(row.metric_values[3].value)
        purchases = int(row.metric_values[4].value)
        revenue = float(row.metric_values[5].value)
        cvr = round(purchases / sessions * 100, 2) if sessions > 0 else 0.0

        rows.append({
            "date": date_str,
            "page": row.dimension_values[0].value,
            "sessions": sessions,
            "active_users": active_users,
            "new_users": new_users,
            "avg_duration": round(avg_duration, 1),
            "purchases": purchases,
            "revenue": round(revenue, 2),
            "cvr": cvr,
        })

    print(f"  [GA4] Landing pages: {len(rows)} rows for {date_str}.")
    return rows


def _write_temp_credentials() -> str:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="ga4_creds_"
    )
    tmp.write(GA4_CREDENTIALS_JSON)
    tmp.close()
    return tmp.name


def _empty(date_str: str = "") -> dict:
    return {
        "date": date_str,
        "sessions": 0,
        "conversion_rate": 0.0,
        "revenue": 0.0,
        "add_to_carts": 0,
    }


def _empty_summary(date_str: str = "") -> dict:
    return {
        "date": date_str,
        "total_users": 0,
        "new_users": 0,
        "sessions": 0,
        "pageviews": 0,
        "pages_per_session": 0.0,
        "bounce_rate": 0.0,
        "avg_duration": 0.0,
        "add_to_carts": 0,
        "purchases": 0,
        "revenue": 0.0,
        "cvr": 0.0,
        "channels": [],
    }
