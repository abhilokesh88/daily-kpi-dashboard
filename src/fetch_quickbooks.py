"""
Pull monthly P&L from QuickBooks Online API.

Fetches the full Profit & Loss report for a given month.
Used by the monthly financial report (run_monthly.py), not the daily dashboard.
"""

import base64
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


def fetch_month(year: int, month: int) -> dict:
    """Return P&L data for an entire month: revenue, expenses, net_income."""

    if not QB_CLIENT_ID or not QB_REFRESH_TOKEN or not QB_REALM_ID:
        print("  [QuickBooks] Skipped — credentials not configured.")
        return _empty(year, month)

    start = date(year, month, 1)
    if month == 12:
        end = date(year, 12, 31)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)

    access_token = _refresh_access_token()
    if not access_token:
        print("  [QuickBooks] Failed to refresh access token.")
        return _empty(year, month)

    base = BASE_URL.get(QB_ENVIRONMENT, BASE_URL["production"])
    url = f"{base}/v3/company/{QB_REALM_ID}/reports/ProfitAndLoss"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    params = {
        "start_date": start.strftime("%Y-%m-%d"),
        "end_date": end.strftime("%Y-%m-%d"),
        "minorversion": "65",
    }

    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    report = resp.json()

    revenue, expenses, net_income = _parse_pnl(report)

    month_label = start.strftime("%B %Y")
    print(f"  [QuickBooks] {month_label}: Revenue=${revenue:,.2f}  Expenses=${expenses:,.2f}  Net=${net_income:,.2f}")

    return {
        "month": start.strftime("%Y-%m"),
        "month_label": month_label,
        "revenue": round(revenue, 2),
        "expenses": round(expenses, 2),
        "net_income": round(net_income, 2),
    }


def _refresh_access_token() -> str | None:
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
    marker_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", ".new_qb_refresh_token"
    )
    os.makedirs(os.path.dirname(marker_path), exist_ok=True)
    with open(marker_path, "w") as f:
        f.write(new_token)
    print("  [QuickBooks] New refresh token saved for rotation.")


def _parse_pnl(report: dict) -> tuple[float, float, float]:
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


def _empty(year: int, month: int) -> dict:
    return {
        "month": f"{year:04d}-{month:02d}",
        "month_label": date(year, month, 1).strftime("%B %Y"),
        "revenue": 0.0,
        "expenses": 0.0,
        "net_income": 0.0,
    }
