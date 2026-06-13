"""
Pull yesterday's KPIs from Google Analytics 4.

Metrics:
  - Sessions
  - Conversion rate (ecommerce)
  - Revenue
"""

import json
import os
import tempfile
from datetime import date, timedelta

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Metric,
    RunReportRequest,
)

from src.config import GA4_CREDENTIALS_JSON, GA4_PROPERTY_ID


def fetch(target_date: date | None = None) -> dict:
    """Return a dict with sessions, conversion_rate, revenue for *target_date*."""

    if not GA4_PROPERTY_ID or not GA4_CREDENTIALS_JSON:
        print("  [GA4] Skipped — credentials not configured.")
        return _empty()

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    # Write the service-account JSON to a temp file so the client can read it.
    creds_path = _write_temp_credentials()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=date_str, end_date=date_str)],
        metrics=[
            Metric(name="sessions"),
            Metric(name="ecommercePurchases"),
            Metric(name="purchaseRevenue"),
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
    conversion_rate = (purchases / sessions * 100) if sessions > 0 else 0.0

    return {
        "date": date_str,
        "sessions": sessions,
        "conversion_rate": round(conversion_rate, 2),
        "revenue": round(revenue, 2),
    }


# --- helpers ---------------------------------------------------------------

def _write_temp_credentials() -> str:
    """Write GA4_CREDENTIALS_JSON env var to a temp file; return its path."""
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
    }
