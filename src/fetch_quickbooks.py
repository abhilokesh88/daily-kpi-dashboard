"""
Pull financial KPIs from QuickBooks Online API.

Metrics:
  - Revenue (Income)
  - Expenses
  - Net Income (Profit)
"""

import base64
import json
import os
from datetime import date, timedelta

import requests

from src.config import (
    QB_CLIENT_ID,
    QB_CLIENT_SECRET,
    QB_REFRESH_TOKEN,
    QB_REALM_ID,
    QB_ENVIRONMENT,
)


BASE_URL = {
    "sandbox": "https://sandbox-quickbooks.api.intuit.com",
    "production": "https://quickbooks.api.intuit.com",
}


def fetch(target_date: date | None = None) -> dict:
    """Return a dict with revenue, expenses, net_income for *target_date*."""

    if not QB_CLIENT_ID or not QB_REFRESH_TOKEN or not QB_REALM_ID:
        print("  [QuickBooks] Skipped — credentials not configured.")
        return _empty()

    target = target_date or date.today() - timedelta(days=1)
    date_str = target.strftime("%Y-%m-%d")

    access_token = _refresh_access_token()
    if not access_token:
        print("  [QuickBooks] Failed to refresh access token.")
        return _empty(date_str)

    base = BASE_URL.get(QB_ENVIRONMENT, BASE_URL["production"])
    url = f"{base}/v3/company/{QB_REALM_ID}/reports/ProfitAndLoss"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    params = {
        "start_date": date_str,
        "end_date": date_str,
        "minorversion": "65",
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    report = resp.json()

    revenue, expenses, net_income = _parse_pnl(report)

    return {
        "date": date_str,
        "revenue": round(revenue, 2),
        "expenses": round(expenses, 2),
        "net_income": round(net_income, 2),
    }


# --- helpers ---------------------------------------------------------------

def _refresh_access_token() -> str | None:
    """Exchange the refresh token for a new access token."""
    url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

    auth_str = f"{QB_CLIENT_ID}:{QB_CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": QB_REFRESH_TOKEN,
    }

    resp = requests.post(url, headers=headers, data=data, timeout=15)

    if resp.status_code != 200:
        print(f"  [QuickBooks] Token refresh failed: {resp.status_code} {resp.text}")
        return None

    tokens = resp.json()

    new_refresh = tokens.get("refresh_token")
    if new_refresh and new_refresh != QB_REFRESH_TOKEN:
        _save_new_refresh_token(new_refresh)

    return tokens.get("access_token")


def _save_new_refresh_token(new_token: str) -> None:
    """Update the GitHub secret with the new refresh token via env marker file."""
    marker_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", ".new_qb_refresh_token"
    )
    os.makedirs(os.path.dirname(marker_path), exist_ok=True)
    with open(marker_path, "w") as f:
        f.write(new_token)
    print("  [QuickBooks] New refresh token saved for rotation.")


def _parse_pnl(report: dict) -> tuple[float, float, float]:
    """Extract revenue, expenses, net income from QBO P&L report JSON."""
    revenue = 0.0
    expenses = 0.0
    net_income = 0.0

    rows = report.get("Rows", {}).get("Row", [])
    for row in rows:
        group = row.get("group", "")
        summary = row.get("Summary", {})
        col_data = summary.get("ColData", [])

        if not col_data or len(col_data) < 2:
            continue

        try:
            value = float(col_data[1].get("value", "0"))
        except (ValueError, TypeError):
            value = 0.0

        if group == "Income":
            revenue = value
        elif group == "Expenses":
            expenses = value
        elif group == "NetIncome":
            net_income = value

    return revenue, expenses, net_income


def _empty(date_str: str = "") -> dict:
    return {
        "date": date_str,
        "revenue": 0.0,
        "expenses": 0.0,
        "net_income": 0.0,
    }
