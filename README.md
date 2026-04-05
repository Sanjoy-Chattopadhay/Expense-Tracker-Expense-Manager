# 💸 ExpenseTracker — MCP Server + Full-Stack Web App

A production-ready personal finance system that works in **two ways at once**:

| Mode | What it is | URL |
|---|---|---|
| **MCP Server** | AI-native tools for Claude, ChatMCP, and any MCP client | `https://academic-gold-weasel.fastmcp.app/mcp` |
| **Web App** | Full-stack dashboard with auth, forms, and reports | `https://academic-gold-weasel.fastmcp.app` |

Both modes share the same SQLite database, category taxonomy, budget rules, and recurring-expense engine — so anything you enter through the web UI is immediately visible to AI tools, and vice versa.

---

## Table of Contents

1. [Live Links](#live-links)
2. [Feature Overview](#feature-overview)
3. [MCP Server — Complete Reference](#mcp-server--complete-reference)
   - [How to Connect](#how-to-connect)
   - [All Tools](#all-tools)
   - [All Resources](#all-resources)
   - [Example Prompts](#example-prompts)
4. [Web Application — Complete Reference](#web-application--complete-reference)
   - [Authentication](#authentication)
   - [Dashboard](#dashboard)
   - [Expense Management](#expense-management-web)
   - [Budgets](#budgets-web)
   - [Recurring Expenses](#recurring-expenses-web)
   - [Profile & Settings](#profile--settings)
5. [Data Model](#data-model)
6. [Categories](#categories)
7. [Local Development](#local-development)
8. [Environment Variables](#environment-variables)
9. [Deployment](#deployment)
10. [Architecture](#architecture)
11. [Tech Stack](#tech-stack)

---

## Live Links

| Resource | URL |
|---|---|
| 🌐 Web App | https://academic-gold-weasel.fastmcp.app |
| 🤖 MCP Endpoint | https://academic-gold-weasel.fastmcp.app/mcp |
| ❤️ Health Check | https://academic-gold-weasel.fastmcp.app/api/health |
| 📂 Categories API | https://academic-gold-weasel.fastmcp.app/api/categories |

---

## Feature Overview

### MCP Side (AI / Claude)
- ✅ 21 tools covering full expense lifecycle
- ✅ 6 live resources (categories, today's spend, this month, budgets, recurring, all-time stats)
- ✅ Stateless HTTP transport — works with any MCP-compatible client
- ✅ Async SQLite backend (`aiosqlite`) with WAL mode

### Web App Side
- ✅ Google OAuth sign-in
- ✅ Phone OTP sign-in (Twilio Verify)
- ✅ Per-user data isolation
- ✅ Monthly dashboard with totals, category breakdown, trends
- ✅ Full CRUD for expenses, budgets, and recurring items
- ✅ Dark / light theme with system preference detection
- ✅ "Copy MCP URL" button — get your server endpoint directly from the UI
- ✅ Responsive design (mobile + desktop)

---

## MCP Server — Complete Reference

### How to Connect

**MCP Endpoint:**
```
https://academic-gold-weasel.fastmcp.app/mcp
```

**Transport:** Stateless HTTP (`POST /mcp`)

#### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "ExpenseTracker": {
      "url": "https://academic-gold-weasel.fastmcp.app/mcp"
    }
  }
}
```

#### ChatMCP / Inspector
Paste the endpoint URL directly into the server field:
```
https://academic-gold-weasel.fastmcp.app/mcp
```

#### Cursor / Windsurf / VS Code (MCP extension)
```json
{
  "mcp": {
    "servers": {
      "ExpenseTracker": {
        "url": "https://academic-gold-weasel.fastmcp.app/mcp",
        "transport": "http"
      }
    }
  }
}
```

---

### All Tools

#### 🧾 Expense CRUD

| Tool | Parameters | Description |
|---|---|---|
| `add_expense` | `date`, `amount`, `category`, `subcategory?`, `note?`, `tags?`, `payment_mode?`, `currency?` | Add a single expense entry |
| `update_expense` | `expense_id`, any field to change | Edit one or more fields of an existing expense |
| `delete_expense` | `expense_id` | Permanently remove an expense |
| `bulk_add_expenses` | `expenses` (list of objects) | Insert many expenses in one call |
| `get_expense` | `expense_id` | Fetch a single expense by its ID |

**`add_expense` — full parameter reference:**

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `date` | string | ✅ | Format: `YYYY-MM-DD` |
| `amount` | float | ✅ | Positive number |
| `category` | string | ✅ | Must match a category name (see [Categories](#categories)) |
| `subcategory` | string | — | Optional subcategory |
| `note` | string | — | Free-text description |
| `tags` | string | — | Comma-separated, e.g. `"work,reimbursable"` |
| `payment_mode` | string | — | `cash` / `upi` / `card` / `netbanking` / `emi` / `other` |
| `currency` | string | — | 3-letter code, default `INR` |

---

#### 🔍 Querying & Listing

| Tool | Parameters | Description |
|---|---|---|
| `list_expenses` | `start_date`, `end_date`, `category?`, `payment_mode?`, `min_amount?`, `max_amount?`, `tags?`, `limit?` | List expenses with rich filters |
| `search_expenses` | `keyword`, `start_date?`, `end_date?`, `limit?` | Full-text search across note, subcategory, tags, category |
| `top_expenses` | `start_date`, `end_date`, `n?`, `category?` | Return the N largest expenses in a range |

---

#### 📊 Reports & Analytics

| Tool | Parameters | Returns |
|---|---|---|
| `summarize` | `start_date`, `end_date`, `category?`, `group_by_subcategory?` | Category (or subcategory) totals with transaction counts |
| `monthly_report` | `year`, `month` | Total, category breakdown, daily totals, top 5 expenses, budget status |
| `yearly_report` | `year` | Annual total, month-by-month breakdown, category breakdown |
| `compare_months` | `month1`, `month2` (YYYY-MM) | Side-by-side totals and per-category change with % diff |
| `spending_trends` | `months?` (default 6), `category?` | Month-over-month trend for last N months |
| `daily_breakdown` | `start_date`, `end_date`, `category?` | Day-by-day spending totals |
| `expense_stats` | `start_date`, `end_date` | Total, count, mean, median, min, max, std dev, avg/day |
| `payment_mode_summary` | `start_date`, `end_date` | Spending grouped by payment method |
| `export_csv` | `start_date`, `end_date`, `category?` | Returns a CSV string ready to save or display |

---

#### 💰 Budget Management

| Tool | Parameters | Description |
|---|---|---|
| `set_budget` | `month` (YYYY-MM), `category`, `amount` | Set or update a monthly spending cap for a category |
| `get_budgets` | `month` | All budgets for a month with actual vs budget and % used |
| `delete_budget` | `month`, `category` | Remove a budget entry |

---

#### 🔁 Recurring Expenses

| Tool | Parameters | Description |
|---|---|---|
| `add_recurring` | `description`, `amount`, `category`, `subcategory?`, `payment_mode?`, `frequency`, `next_due?` | Register a recurring template (rent, EMI, subscriptions) |
| `list_recurring` | `active_only?` | List all active recurring templates |
| `log_recurring` | `recurring_id`, `date_override?` | Post an actual expense from the template and advance `next_due` |
| `delete_recurring` | `recurring_id` | Soft-delete (deactivate) a recurring template |

**`frequency` values:** `monthly` · `weekly` · `yearly`

---

### All Resources

Resources are read-only snapshots exposed as JSON. Any MCP client can read them directly.

| URI | Description |
|---|---|
| `expense:///categories` | Full category + subcategory taxonomy from `categories.json` |
| `expense:///summary/today` | Today's total and per-category breakdown |
| `expense:///summary/this_month` | Current month totals, budget progress per category, days elapsed |
| `expense:///recurring/due_soon` | All recurring items with `next_due` within the next 7 days |
| `expense:///budgets/status` | This month's budget vs actual for every configured category |
| `expense:///stats/all_time` | All-time transaction count, totals, averages, top 5 categories |

---

### Example Prompts

Paste these directly into Claude or any MCP-connected AI:

```
Add an expense: ₹450 for lunch today, category food, subcategory dining_out, paid by UPI.
```
```
Show all my expenses from April 1 to April 5, 2026.
```
```
Give me a full monthly report for March 2026.
```
```
Compare my spending in February and March 2026.
```
```
Set a budget of ₹8000 for food in April 2026.
```
```
Show my budget status for this month.
```
```
What are my top 10 largest expenses this year?
```
```
Add a recurring expense: Netflix ₹649/month, category subscriptions/streaming, next due 2026-05-01.
```
```
Log this month's Netflix payment.
```
```
Show spending trends for the last 6 months.
```
```
Export my April 2026 expenses as CSV.
```
```
Search for all expenses with the note "office".
```
```
Show stats for Q1 2026 (Jan 1 to Mar 31).
```

---

## Web Application — Complete Reference

**Live URL:** https://academic-gold-weasel.fastmcp.app

### Authentication

The web app supports two sign-in methods:

#### Google Sign-In
- One-click OAuth using your Google account
- No password needed
- Profile picture, name, and email pulled automatically

#### Phone OTP
- Enter your phone number with country code (e.g. `+91XXXXXXXXXX`)
- Receive a one-time code via SMS (powered by Twilio Verify)
- Enter the code to sign in

Sessions persist for **30 days**. You stay signed in across browser restarts.

---

### Dashboard

The dashboard is the home screen after sign-in. It shows:

| Section | What it displays |
|---|---|
| **Monthly Total** | Total spent so far this calendar month |
| **Category Breakdown** | Per-category totals with budget progress bars (if budgets are set) |
| **Recent Expenses** | Last few transactions at a glance |
| **Recurring Due Soon** | Upcoming recurring payments within 7 days |
| **MCP Connect Panel** | Your live MCP endpoint URL with a one-click copy button |

---

### Expense Management (Web)

Available under the **Expenses** tab:

- **Add expense** — date, amount, category (dropdown), subcategory, note, tags, payment mode, currency
- **View expenses** — paginated list filterable by date range
- **Edit expense** — click any entry to update any field
- **Delete expense** — remove with confirmation
- All changes sync immediately to the shared database (visible in AI tools too)

---

### Budgets (Web)

Available under the **Budgets** tab:

- **Set a budget** — pick a month, pick a category, set an amount
- **Budget tracker** — visual progress bars showing spent vs limit
- **Over-budget alerts** — highlighted rows when a category exceeds its cap
- **Delete budget** — remove any budget entry

---

### Recurring Expenses (Web)

Available under the **Recurring** tab:

- **Add recurring** — description, amount, category, frequency (monthly / weekly / yearly), next due date
- **View active recurring** — sorted by next due date
- **Log a payment** — marks one occurrence as paid and advances the next due date automatically
- **Deactivate** — soft-delete without losing history

---

### Profile & Settings

Available under the **Profile** tab:

| Field | Description |
|---|---|
| Full name | Display name shown on the dashboard |
| City | Optional location |
| Monthly income | Used for savings percentage calculations |
| Savings goal | Target monthly savings amount |
| Default currency | Currency shown across the UI |

---

## Data Model

### Expense Fields

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Auto-incremented primary key |
| `date` | text | `YYYY-MM-DD` |
| `amount` | real | Positive number |
| `category` | text | Main category |
| `subcategory` | text | Optional sub-category |
| `note` | text | Free-form description |
| `tags` | text | Comma-separated labels |
| `payment_mode` | text | `cash`, `upi`, `card`, `netbanking`, `emi`, `other` |
| `currency` | text | Default `INR` |
| `created_at` | text | UTC timestamp set on insert |

### Other Tables

| Table | Purpose |
|---|---|
| `budgets` | Monthly caps per category (`month`, `category`, `amount`) |
| `recurring` | Recurring templates with frequency and `next_due` |
| `app_users` | Web-app user profiles (Google + phone auth) |
| `app_sessions` | Session tokens with expiry |
| `app_otp_codes` | One-time passwords with TTL |
| `app_expenses` | Per-user expense records (web app) |
| `app_budgets` | Per-user budgets (web app) |
| `app_recurring` | Per-user recurring templates (web app) |

---

## Categories

20 top-level categories, each with subcategories defined in `categories.json`:

| Category | Example Subcategories |
|---|---|
| `food` | groceries, fruits_vegetables, dining_out, coffee_tea, delivery_fees |
| `transport` | fuel, public_transport, cab_ride_hailing, parking, vehicle_service |
| `housing` | rent, maintenance_hoa, property_tax, repairs_service, furnishing |
| `utilities` | electricity, water, internet_broadband, mobile_phone, tv_dth |
| `health` | medicines, doctor_consultation, diagnostics_labs, fitness_gym |
| `education` | books, courses, online_subscriptions, exam_fees, workshops |
| `family_kids` | school_fees, daycare, toys_games, clothes, events_birthdays |
| `entertainment` | movies_events, streaming_subscriptions, games_apps, outing |
| `shopping` | clothing, footwear, electronics_gadgets, appliances, home_decor |
| `subscriptions` | saas_tools, cloud_ai, music_video, storage_backup |
| `personal_care` | salon_spa, grooming, cosmetics, hygiene |
| `gifts_donations` | gifts_personal, charity_donation, festivals |
| `finance_fees` | bank_charges, late_fees, interest, brokerage |
| `business` | software_tools, hosting_domains, marketing_ads, contractor_payments |
| `travel` | flights, hotels, train_bus, visa_passport, local_transport |
| `home` | household_supplies, cleaning_supplies, kitchenware, pest_control |
| `pet` | food, vet, grooming, supplies |
| `taxes` | income_tax, gst, professional_tax, filing_fees |
| `investments` | mutual_funds, stocks, fd_rd, gold, crypto |
| `misc` | uncategorized, rounding, other |

---

## Local Development

### Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repo
git clone https://github.com/Sanjoy-Chattopadhay/Expense-Tracker-Expense-Manager.git
cd Expense-Tracker-Expense-Manager

# Install dependencies
uv sync

# Copy env template and fill in values
cp .env.example .env
```

### Run

```bash
# Start the server (web app + MCP endpoint)
uv run python main.py
```

| Endpoint | URL |
|---|---|
| Web App | http://localhost:8000 |
| MCP Endpoint | http://localhost:8000/mcp |
| Health Check | http://localhost:8000/api/health |

### Run with Uvicorn directly

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Connect local MCP to Claude Desktop

```json
{
  "mcpServers": {
    "ExpenseTracker-local": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `PORT` | — | `8000` | Server port |
| `DB_PATH` | — | auto-detected | Explicit SQLite file path. Auto-resolves to `./data/expenses.db` then `/tmp/expenses.db` |
| `SECURE_COOKIES` | — | `true` | Set `false` for local HTTP development only |
| `SESSION_TTL_DAYS` | — | `30` | How long web sessions last |
| `OTP_TTL_MINUTES` | — | `10` | How long phone OTP codes are valid |
| `GOOGLE_CLIENT_ID` | ✅ for Google auth | — | OAuth Web Client ID from Google Cloud Console |
| `MCP_URL` | ✅ for UI copy button | — | Your public MCP endpoint URL |
| `TWILIO_ACCOUNT_SID` | — | — | Twilio Account SID (OTP falls back to demo mode if unset) |
| `TWILIO_AUTH_TOKEN` | — | — | Twilio Auth Token |
| `TWILIO_VERIFY_SERVICE_SID` | — | — | Twilio Verify Service SID |

> **Note:** Without Twilio credentials the app still works — OTP codes are logged to the server console instead of being sent via SMS, which is useful for development.

---

## Deployment

### FastMCP Horizon (current)

This server is deployed on [FastMCP Horizon](https://horizon.prefect.io). Push to `main` to trigger a redeploy.

MCP endpoint: `https://academic-gold-weasel.fastmcp.app/mcp`

### Render (alternative)

A `render.yaml` is included for one-click Render deployment with a persistent disk mounted at `/app/data`:

1. Connect your GitHub repo in the Render dashboard
2. Render will detect `render.yaml` automatically
3. Set secret env vars in the Render dashboard:
   - `GOOGLE_CLIENT_ID`
   - `MCP_URL`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_VERIFY_SERVICE_SID`
4. Deploy

### Docker

```bash
# Build
docker build -t expense-tracker .

# Run
docker run -p 8000:8000 \
  -e GOOGLE_CLIENT_ID=your_id \
  -e MCP_URL=http://localhost:8000/mcp \
  -v $(pwd)/data:/app/data \
  expense-tracker
```

### Database Persistence Note

The app uses SQLite. For hosted deployments:

- **Persistent disk / volume mount** at `/app/data` → data survives restarts and redeploys ✅
- **Ephemeral filesystem** (e.g. Vercel, AWS Lambda) → data is wiped on redeploy ❌

Render, Railway, Fly.io, and self-hosted Docker all support volume mounts.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        main.py                          │
│                                                         │
│  FastMCP("ExpenseTracker")                              │
│  ├── 21 MCP Tools  (async, aiosqlite)                   │
│  ├── 6  MCP Resources (sync, sqlite3)                   │
│  └── register_web_routes(mcp, DB_PATH, ...)             │
│       └── webapp.py                                     │
│            ├── /api/auth/*    (Google + OTP)            │
│            ├── /api/expenses  (CRUD)                    │
│            ├── /api/budgets   (CRUD)                    │
│            ├── /api/recurring (CRUD + log)              │
│            ├── /api/dashboard                           │
│            ├── /api/public-config  → MCP_URL            │
│            └── /  → serves web/index.html              │
│                                                         │
│  SQLite DB (data/expenses.db)                           │
│  ├── expenses        budgets         recurring          │
│  ├── app_users       app_sessions    app_otp_codes      │
│  ├── app_expenses    app_budgets     app_recurring       │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ▲                              ▲
   MCP Clients                    Web Browser
   (Claude, ChatMCP,           (web/index.html +
    Cursor, Inspector)          app.js + styles.css)
```

**Key design decisions:**
- A single FastMCP instance serves both the MCP protocol and custom HTTP routes via `@mcp.custom_route`
- MCP tools use `aiosqlite` (async); MCP resources use `sqlite3` (sync — required by FastMCP's resource model)
- The web app has its own user/session tables (`app_*`) for multi-user isolation; MCP tools operate on the shared `expenses` table
- DB path is resolved at startup with a write-probe fallback chain so the server starts on any platform

---

## Tech Stack

| Layer | Technology |
|---|---|
| MCP Framework | [FastMCP](https://github.com/jlowin/fastmcp) 3.2+ |
| Web Framework | Starlette (via FastMCP custom routes) |
| ASGI Server | Uvicorn |
| Database | SQLite via `aiosqlite` (async) + `sqlite3` (sync) |
| Auth | Google OAuth 2.0 (`google-auth`) + Twilio Verify OTP |
| Frontend | Vanilla HTML + CSS + JS (zero framework dependencies) |
| Package Manager | [`uv`](https://docs.astral.sh/uv/) |
| Runtime | Python 3.13+ |
| Deployment | FastMCP Horizon / Docker / Render |

---

## Project Structure

```
.
├── main.py              # MCP server — all tools, resources, and app entry point
├── webapp.py            # Web app routes — auth, CRUD API, static file serving
├── app.py               # Minimal ASGI entry point for uvicorn
├── categories.json      # Expense category + subcategory taxonomy
├── web/
│   ├── index.html       # Single-page web application
│   ├── app.js           # Frontend logic (state, API calls, UI handlers)
│   └── styles.css       # Theme system, layout, responsive design
├── data/
│   └── expenses.db      # SQLite database (git-ignored)
├── Dockerfile           # Container image definition
├── render.yaml          # Render.com deployment config with persistent disk
├── pyproject.toml       # Python project metadata and dependencies
├── uv.lock              # Locked dependency tree
└── .env.example         # Template for all required environment variables
```

---

## License

MIT — use freely, attribution appreciated.
