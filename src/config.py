"""
Configuration — all secrets come from environment variables.
In GitHub Actions these are set via repository secrets.
"""

import os


# --- GA4 ---
GA4_PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "")
# Path to the service-account JSON (written to a temp file in CI)
GA4_CREDENTIALS_JSON = os.environ.get("GA4_CREDENTIALS_JSON", "")

# --- Shopify ---
SHOPIFY_STORE_URL = os.environ.get("SHOPIFY_STORE_URL", "")  # e.g. "my-store.myshopify.com"
SHOPIFY_ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")

# --- Meta Ads ---
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "")  # e.g. "act_123456789"

# --- QuickBooks ---
QB_CLIENT_ID = os.environ.get("QB_CLIENT_ID", "")
QB_CLIENT_SECRET = os.environ.get("QB_CLIENT_SECRET", "")
QB_REFRESH_TOKEN = os.environ.get("QB_REFRESH_TOKEN", "")
QB_REALM_ID = os.environ.get("QB_REALM_ID", "")  # aka Company ID
QB_ENVIRONMENT = os.environ.get("QB_ENVIRONMENT", "production")  # "sandbox" or "production"

# --- Slack ---
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")  # GitHub Pages serves from /docs
