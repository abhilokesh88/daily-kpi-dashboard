# Daily KPI Dashboard — Setup Guide

Everything is built. You just need to connect your accounts.
Follow these steps one at a time — each takes a few minutes.

---

## Step 1: Create the GitHub Repo

1. Go to https://github.com/new
2. Name it `daily-kpi-dashboard`
3. Set it to **Private** (your data stays private)
4. Click **Create repository**
5. Follow the instructions to push this folder to GitHub (I can help with this)

## Step 2: Enable GitHub Pages

1. In your repo, go to **Settings → Pages**
2. Under "Source", select **Deploy from a branch**
3. Set the branch to `main` and folder to `/docs`
4. Click **Save**
5. Your dashboard will be live at: `https://YOUR-USERNAME.github.io/daily-kpi-dashboard/`

---

## Step 3: Get Your API Credentials

### 3A. Google Analytics 4

1. Go to https://console.cloud.google.com/
2. Create a project (or use an existing one)
3. Enable the **Google Analytics Data API**
4. Go to **IAM & Admin → Service Accounts** → Create a service account
5. Download the JSON key file
6. In GA4 (analytics.google.com), go to **Admin → Property → Property Access Management**
7. Add the service account email as a Viewer
8. Find your GA4 Property ID in **Admin → Property Settings** (it's a number like `123456789`)

**You'll need:** the Property ID number + the entire contents of the JSON key file

### 3B. Shopify

1. In your Shopify admin, go to **Settings → Apps and sales channels → Develop apps**
2. Click **Create an app** → name it "KPI Dashboard"
3. Under **Configuration**, add these scopes: `read_orders`
4. Click **Install app**
5. Copy the **Admin API access token** (starts with `shpat_`)
6. Your store URL is: `your-store-name.myshopify.com`

**You'll need:** the store URL + the access token

### 3C. Meta (Facebook) Ads

1. Go to https://developers.facebook.com/
2. Create an app (type: Business)
3. In the app dashboard, go to **Marketing API → Tools**
4. Generate a **System User Access Token** with `ads_read` permission
5. Find your Ad Account ID in **Meta Business Suite → Settings → Ad Accounts** (format: `act_123456789`)

**You'll need:** the access token + the ad account ID

### 3D. Slack Webhook

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**
2. Name it "KPI Dashboard", pick your workspace
3. Go to **Incoming Webhooks** → toggle ON
4. Click **Add New Webhook to Workspace** → pick the channel you want reports in
5. Copy the webhook URL (starts with `https://hooks.slack.com/...`)

**You'll need:** the webhook URL

---

## Step 4: Add Secrets to GitHub

1. In your repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** for each of these:

| Secret Name            | Value                                      |
|------------------------|--------------------------------------------|
| `GA4_PROPERTY_ID`      | Your GA4 property ID number                |
| `GA4_CREDENTIALS_JSON` | The entire contents of the JSON key file   |
| `SHOPIFY_STORE_URL`    | `your-store.myshopify.com`                 |
| `SHOPIFY_ACCESS_TOKEN` | `shpat_xxxxxxxxxxxx`                       |
| `META_ACCESS_TOKEN`    | Your Meta access token                     |
| `META_AD_ACCOUNT_ID`   | `act_123456789`                            |
| `SLACK_WEBHOOK_URL`    | `https://hooks.slack.com/services/...`     |

---

## Step 5: Test It

1. Go to the **Actions** tab in your repo
2. Click **Daily KPI Report** in the sidebar
3. Click **Run workflow** → **Run workflow**
4. Wait ~1 minute for it to finish
5. Check your Slack channel and your dashboard URL!

---

## Adjusting the Schedule

The report runs daily at 8:00 AM UTC by default.
To change it, edit `.github/workflows/daily-kpis.yml` and update the cron line.

Examples:
- `0 12 * * *` = noon UTC (7 AM EST)
- `0 14 * * *` = 2 PM UTC (9 AM EST)
- `0 6 * * 1-5` = 6 AM UTC, weekdays only

---

## Adding New KPIs Later

Just ask me! I'll add the metric to the right fetch script,
update the Slack message, and update the dashboard template.
