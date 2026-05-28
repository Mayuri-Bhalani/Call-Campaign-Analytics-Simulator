# 📞 CallPulse — Call Campaign Analytics Simulator

> A full-stack analytics dashboard for monitoring call center campaign performance, agent productivity, and KPIs — built with Python (Flask) + Vanilla JS + Chart.js.

---

## 🖥️ Dashboard Preview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  CallPulse  │  Operations Overview                     As of 2026-05-27      │
│  Analytics  ├──────────────────────────────────────────────────────────────  │
│  ─────────  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  ◈ Overview │  │  308     │ │  104     │ │  33.8%   │ │  4m 10s  │          │
│  ⊞ Campaigns│  │ Calls    │ │Connected │ │Cont.Rate │ │ Avg AHT  │          │
│  ◎ Agents   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ─────────  │                                                                 │
│  ↗ Perform. │  ┌────────────────────────────┐ ┌──────────────────────────┐   │
│  ◑ Disposit.│  │  Daily Call Volume (30d)   │ │  Contact Rate Trend      │   │
│             │  │  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ │ │  ～～～～～～～～～  │   │
│  ● Live     │  │  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ │ │                          │   │
│  5 campaigns│  └────────────────────────────┘ └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Purpose — What Problem Does This Solve?

In a real call center or collections environment, operations managers and analysts face three daily challenges:

**1. Fragmented visibility** — Call data lives in the dialer platform (Five9, Twilio, Acqueon), agent data lives in a workforce tool, and KPIs live in spreadsheets. There is no single view.

**2. Slow reporting loops** — Daily performance reports are manually compiled in Excel and emailed each morning. By the time a manager sees yesterday's contact rate drop, the problem has been running for 24+ hours.

**3. No campaign-level drill-down** — Aggregate numbers hide which specific campaigns are underperforming, which agents are lagging, and which hours of the day drive the best contact rates.

**CallPulse solves all three.** It simulates the data pipeline from dialer systems → Python analytics backend → live dashboard, providing:

- Real-time KPI cards (calls, contact rate, handle time, active agents)
- 30-day trend charts for call volume and contact rate
- Per-campaign monitoring with clickable drill-down
- Agent-level performance table with target attainment tracking
- Hourly heatmap to identify peak call windows
- Disposition breakdown analysis (Connected, Voicemail, No Answer, etc.)
- Week-over-week performance comparison

---

## 🏗️ Architecture

```
call-campaign-analytics/
│
├── data/
│   ├── generate_data.py      ← Synthetic data generator (6,187 call records)
│   ├── agents.csv            ← 20 agents with skills, status, targets
│   ├── campaigns.csv         ← 5 campaigns (Five9, Twilio, Acqueon, RingCentral)
│   ├── call_logs.csv         ← 30 days of granular call records
│   └── daily_summary.csv     ← Pre-aggregated daily KPIs per campaign
│
├── backend/
│   └── app.py                ← Flask REST API (8 endpoints)
│
├── frontend/
│   └── index.html            ← Single-file dashboard (HTML + CSS + JS)
│
├── requirements.txt
├── .gitignore
└── README.md
```

### Data Flow

```
generate_data.py
      │
      ▼
CSV datasets (agents, campaigns, call_logs, daily_summary)
      │
      ▼
Flask API (app.py) — reads CSVs with Pandas, computes KPIs, serves JSON
      │
      ▼
Frontend Dashboard (index.html) — Chart.js visualizations, 5 pages
```

> **Note:** The frontend also works in standalone mode — it has all data pre-embedded as JavaScript objects. This means you can open `frontend/index.html` directly in a browser without running the backend. The API backend is provided for integration into live systems.

---

## 📊 Dashboard Pages

### 1. Operations Overview
The main landing page. Shows:
- **6 KPI cards**: Today's calls, connected calls, contact rate, average handle time, active agents, active campaigns — with WoW delta indicators
- **Daily call volume bar chart**: 30-day stacked bar (total calls + connected)
- **Contact rate line chart**: 30-day trend with fill
- **Calls by hour**: Bar chart showing optimal calling windows (green = high contact rate hours)
- **Disposition doughnut**: Visual breakdown of call outcomes

### 2. Campaign Monitor
- **5 campaign cards**: Each shows dialer platform, type (Inbound/Outbound), status, total calls, contact rate, avg duration, and a progress bar toward target
- **Interactive drill-down**: Click any campaign → dual-axis chart loads showing daily call volume (bars) + contact rate trend (line) for that specific campaign

### 3. Agent Performance
- Full roster of 20 agents with today's metrics
- Columns: Name, Skill, Status (Active / In Call / On Break / Offline), Calls, Connected, Contact Rate, Avg Duration, Target Attainment
- Color-coded contact rates and attainment progress bars

### 4. Performance Analytics
- **Week-over-week bar chart**: This week vs prior week, daily breakdown
- **Campaign contact rate comparison**: Horizontal bar chart across all 5 campaigns
- **Full campaign summary table**: All metrics in one view with progress bars

### 5. Disposition Analysis
- **Doughnut chart**: Share of each call outcome
- **Horizontal bar chart**: Absolute volume per disposition
- **Detail table**: Count, percentage, and visual bar for every disposition type

---

## ⚙️ How It Works — Technical Detail

### Data Generation (`data/generate_data.py`)

Generates 4 realistic CSV files using NumPy/random with a fixed seed (reproducible):

| File | Rows | Description |
|------|------|-------------|
| `agents.csv` | 20 | Agent roster — name, skill, status, tenure, target calls/day |
| `campaigns.csv` | 5 | Campaign config — dialer platform, type, dates, target contacts |
| `call_logs.csv` | ~6,187 | Granular calls — timestamp, agent, campaign, disposition, duration |
| `daily_summary.csv` | 150 | Pre-aggregated daily KPIs per campaign (30 days × 5 campaigns) |

Realistic modeling includes:
- Weekend volume reduction (~60–120 calls vs 180–320 weekdays)
- Disposition weights matching real call center distributions (35% connect rate)
- Variable call durations by disposition type (Connected: 45–720s, Voicemail: 10–60s)

### Backend API (`backend/app.py`)

Flask app with 8 REST endpoints:

| Endpoint | Returns |
|----------|---------|
| `GET /api/health` | System health check |
| `GET /api/kpis` | Top-level KPI summary + WoW deltas |
| `GET /api/campaigns` | All campaigns with aggregated metrics |
| `GET /api/agents` | Agent roster + today's performance stats |
| `GET /api/daily-trend` | 30-day daily aggregation (calls + contact rate) |
| `GET /api/dispositions` | Disposition counts and percentages |
| `GET /api/hourly` | Calls and contact rate bucketed by hour |
| `GET /api/campaign/<id>` | Single campaign info + daily trend |

KPI logic highlights:
- **Contact rate**: `connected / total_calls × 100`
- **WoW delta**: Current 7-day window vs prior 7-day window
- **AHT** (Average Handle Time): Mean duration of connected calls only
- **Target attainment**: `calls_today / target_calls × 100`

### Frontend (`frontend/index.html`)

Single-file dashboard built with:
- **Chart.js 4.4** (loaded from CDN) — bar, line, doughnut chart types
- **Google Fonts** (Syne, DM Mono, Inter) for distinctive typography
- **Vanilla JS** — no React, no build step required
- **Dark theme** with CSS variables — `#0a0e1a` background, `#00d4ff` accent

All data is pre-embedded as JS objects so the file works offline. The backend provides the same data via API for live/production integration.

---

## 🚀 Quick Start

### Option A — Open directly in browser (no backend needed)
```bash
# Just open the file in any browser
open frontend/index.html
# or on Windows:
start frontend/index.html
```

### Option B — Run with live backend
```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/call-campaign-analytics.git
cd call-campaign-analytics

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Generate the datasets
python data/generate_data.py

# 4. Start the Flask API
python backend/app.py
# API runs at http://localhost:5000

# 5. Open the dashboard
open frontend/index.html
```

### API Quick Test
```bash
# Health check
curl http://localhost:5000/api/health

# KPIs
curl http://localhost:5000/api/kpis

# Specific campaign
curl http://localhost:5000/api/campaign/CMP001
```

---

## 📡 API Reference

### `GET /api/kpis`
```json
{
  "today_calls": 308,
  "today_connected": 104,
  "contact_rate": 33.8,
  "avg_handle_time": 250,
  "active_agents": 11,
  "active_campaigns": 4,
  "week_calls": 1442,
  "week_contact_rate": 33.4,
  "calls_wow_pct": -0.1,
  "contact_wow_pct": -6.7,
  "as_of": "2026-05-27"
}
```

### `GET /api/campaigns`
```json
[
  {
    "campaign_id": "CMP001",
    "name": "Q2 Collections Drive",
    "type": "Outbound",
    "status": "Active",
    "dialer": "Five9",
    "total_calls": 1906,
    "connected": 674,
    "contact_rate": 35.4,
    "avg_duration": 249,
    "target_contacts": 5000
  }
]
```

### `GET /api/agents`
```json
[
  {
    "agent_id": "AGT007",
    "name": "Mei Davis",
    "skill": "Inbound",
    "status": "Offline",
    "calls_today": 22,
    "connected": 8,
    "contact_rate": 36.4,
    "avg_duration": 251,
    "target_calls": 60,
    "attainment": 36.7
  }
]
```

---

## 🗂️ Dataset Schema

### `call_logs.csv`
| Column | Type | Description |
|--------|------|-------------|
| call_id | string | Unique call identifier (CALL000001) |
| timestamp | datetime | Call start time |
| date | date | Call date |
| agent_id | string | Agent identifier (AGT001–AGT020) |
| agent_name | string | Full agent name |
| campaign_id | string | Campaign identifier (CMP001–CMP005) |
| campaign_name | string | Campaign display name |
| dialer | string | Platform (Five9, Twilio, Acqueon, RingCentral) |
| disposition | string | Call outcome (Connected, Voicemail, No Answer, etc.) |
| duration_sec | int | Call duration in seconds |
| is_connected | int | Binary flag (1 = Connected) |

### Disposition Types
| Disposition | Typical % |
|-------------|-----------|
| Connected | ~34% |
| No Answer | ~25% |
| Voicemail | ~21% |
| Busy | ~8% |
| Wrong Number | ~5% |
| Do Not Call | ~4% |
| Callback Scheduled | ~3% |

---

## 🧠 Key Analytical Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **KPI Tracking** | Contact rate, AHT, attainment — computed fresh per API call |
| **Trend Analysis** | 30-day rolling window, WoW comparison |
| **Campaign Monitoring** | Per-campaign drill-down with dual-axis chart |
| **Agent Productivity** | Individual attainment vs daily target |
| **Peak Hour Analysis** | Hourly call volume with contact rate overlay |
| **Disposition Analysis** | Full breakdown with visual distribution |
| **ETL Pipeline** | `generate_data.py` → CSV → Pandas aggregation → JSON API |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Generation | Python, NumPy, Pandas |
| Backend API | Flask (Python) |
| Data Processing | Pandas, NumPy |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Chart.js 4.4 |
| Typography | Google Fonts (Syne, DM Mono, Inter) |
| Deployment | Static file (GitHub Pages compatible) |

---

## 📁 File Structure

```
call-campaign-analytics/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── generate_data.py
│   ├── agents.csv
│   ├── campaigns.csv
│   ├── call_logs.csv
│   └── daily_summary.csv
│
├── backend/
│   └── app.py
│
└── frontend/
    └── index.html
```

---

## 🔮 Potential Extensions

- **Live dialer integration** — Replace CSV data with real-time Twilio/Five9 webhooks
- **Authentication** — Add Flask-Login for role-based access (admin vs agent view)
- **Alert system** — Email/Slack notification when contact rate drops below threshold
- **Export** — Add CSV/PDF export for daily reports
- **Forecasting** — Use historical trend data to predict tomorrow's call volume
- **IVR flow mapping** — Visual tree of IVR paths with drop-off rates

---

## 👩‍💻 Author

**Mayuri Bhalani**
Data & Dialer Analyst | Vancouver, BC
[LinkedIn](https://www.linkedin.com/in/mayuri-bhalani-5472771a6/) · [GitHub](https://github.com/mayuri232003)

---

## 📄 License

MIT — free to use, adapt, and extend.
