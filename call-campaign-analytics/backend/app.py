"""
app.py  –  Call Campaign Analytics Simulator  –  Backend API
Flask REST API that reads the CSV datasets and exposes
clean JSON endpoints consumed by the frontend dashboard.

Endpoints:
  GET /api/kpis            – Top-level KPI summary cards
  GET /api/campaigns       – Campaign list with metrics
  GET /api/agents          – Agent roster with today's stats
  GET /api/daily-trend     – Daily call volume + contact rate (30d)
  GET /api/dispositions    – Disposition breakdown
  GET /api/hourly          – Calls by hour of day
  GET /api/campaign/<id>   – Single campaign detail + trend
"""

from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

# ── helpers ──────────────────────────────────────────────────────────────────
def load():
    calls     = pd.read_csv(f"{DATA_DIR}/call_logs.csv", parse_dates=["timestamp","date"])
    agents    = pd.read_csv(f"{DATA_DIR}/agents.csv")
    campaigns = pd.read_csv(f"{DATA_DIR}/campaigns.csv")
    daily     = pd.read_csv(f"{DATA_DIR}/daily_summary.csv")
    return calls, agents, campaigns, daily

def safe(val):
    if isinstance(val, (np.integer,)):  return int(val)
    if isinstance(val, (np.floating,)): return round(float(val), 2)
    if pd.isna(val):                    return None
    return val

def row_to_dict(row):
    return {k: safe(v) for k, v in row.items()}

# ── routes ───────────────────────────────────────────────────────────────────

@app.route("/api/kpis")
def kpis():
    calls, agents, campaigns, daily = load()
    today      = calls["date"].max()
    today_df   = calls[calls["date"] == today]
    week_start = today - pd.Timedelta(days=6)
    week_df    = calls[calls["date"] >= week_start]
    prev_week  = calls[(calls["date"] >= week_start - pd.Timedelta(days=7)) &
                       (calls["date"] <  week_start)]

    def pct_change(curr, prev):
        if prev == 0: return 0
        return round((curr - prev) / prev * 100, 1)

    total_today     = len(today_df)
    connected_today = int(today_df["is_connected"].sum())
    contact_rate    = round(connected_today / total_today * 100, 1) if total_today else 0
    dur_series      = today_df[today_df["duration_sec"] > 0]["duration_sec"]
    avg_dur         = round(dur_series.mean(), 0) if len(dur_series) else 0
    active_agents   = int((agents["status"].isin(["Active","In Call"])).sum())
    week_calls      = len(week_df)
    prev_calls      = len(prev_week)
    week_connected  = int(week_df["is_connected"].sum())
    week_contact    = round(week_connected / week_calls * 100, 1) if week_calls else 0
    prev_conn       = int(prev_week["is_connected"].sum())
    prev_contact    = round(prev_conn / len(prev_week) * 100, 1) if len(prev_week) else 0

    return jsonify({
        "today_calls"       : int(total_today),
        "today_connected"   : connected_today,
        "contact_rate"      : contact_rate,
        "avg_handle_time"   : int(avg_dur),
        "active_agents"     : active_agents,
        "active_campaigns"  : int((campaigns["status"] == "Active").sum()),
        "week_calls"        : int(week_calls),
        "week_contact_rate" : week_contact,
        "calls_wow_pct"     : pct_change(week_calls, prev_calls),
        "contact_wow_pct"   : pct_change(week_contact, prev_contact),
        "as_of"             : str(today.date()),
    })


@app.route("/api/campaigns")
def campaigns_endpoint():
    calls, _, campaigns, _ = load()
    result = []
    for _, c in campaigns.iterrows():
        cdf   = calls[calls["campaign_id"] == c["campaign_id"]]
        total = len(cdf)
        conn  = int(cdf["is_connected"].sum())
        rate  = round(conn / total * 100, 1) if total else 0
        dur_s = cdf[cdf["duration_sec"] > 0]["duration_sec"]
        avg_d = round(dur_s.mean(), 0) if len(dur_s) else 0
        result.append({
            "campaign_id"    : c["campaign_id"],
            "name"           : c["name"],
            "type"           : c["type"],
            "status"         : c["status"],
            "dialer"         : c["dialer"],
            "start_date"     : c["start_date"],
            "end_date"       : c["end_date"],
            "target_contacts": int(c["target_contacts"]),
            "total_calls"    : total,
            "connected"      : conn,
            "contact_rate"   : rate,
            "avg_duration"   : int(avg_d),
        })
    return jsonify(result)


@app.route("/api/agents")
def agents_endpoint():
    calls, agents, _, _ = load()
    today = calls["date"].max()
    td    = calls[calls["date"] == today]
    result = []
    for _, a in agents.iterrows():
        adf   = td[td["agent_id"] == a["agent_id"]]
        total = len(adf)
        conn  = int(adf["is_connected"].sum())
        rate  = round(conn / total * 100, 1) if total else 0
        dur_s = adf[adf["duration_sec"] > 0]["duration_sec"]
        avg_d = round(dur_s.mean(), 0) if len(dur_s) else 0
        tgt   = int(a["target_calls"])
        result.append({
            "agent_id"     : a["agent_id"],
            "name"         : a["name"],
            "skill"        : a["skill"],
            "status"       : a["status"],
            "tenure_months": int(a["tenure_months"]),
            "target_calls" : tgt,
            "calls_today"  : total,
            "connected"    : conn,
            "contact_rate" : rate,
            "avg_duration" : int(avg_d),
            "attainment"   : round(total / tgt * 100, 1) if tgt else 0,
        })
    result.sort(key=lambda x: x["calls_today"], reverse=True)
    return jsonify(result)


@app.route("/api/daily-trend")
def daily_trend():
    _, _, _, daily = load()
    trend = (
        daily.groupby("date")
        .agg(total_calls=("total_calls", "sum"),
             connected=("connected", "sum"))
        .reset_index()
        .sort_values("date")
    )
    trend["contact_rate"] = (trend["connected"] / trend["total_calls"] * 100).round(1)
    return jsonify([row_to_dict(r) for _, r in trend.iterrows()])


@app.route("/api/dispositions")
def dispositions():
    calls, _, _, _ = load()
    cid = request.args.get("campaign_id")
    df  = calls if not cid else calls[calls["campaign_id"] == cid]
    counts = df["disposition"].value_counts().reset_index()
    counts.columns = ["disposition", "count"]
    counts["pct"] = (counts["count"] / counts["count"].sum() * 100).round(1)
    return jsonify([row_to_dict(r) for _, r in counts.iterrows()])


@app.route("/api/hourly")
def hourly():
    calls, _, _, _ = load()
    calls = calls.copy()
    calls["hour"] = pd.to_datetime(calls["timestamp"]).dt.hour
    h = calls.groupby("hour").agg(
        total_calls=("call_id", "count"),
        connected=("is_connected", "sum")
    ).reset_index()
    h["contact_rate"] = (h["connected"] / h["total_calls"] * 100).round(1)
    return jsonify([row_to_dict(r) for _, r in h.iterrows()])


@app.route("/api/campaign/<campaign_id>")
def campaign_detail(campaign_id):
    calls, _, campaigns, daily = load()
    c = campaigns[campaigns["campaign_id"] == campaign_id]
    if c.empty:
        return jsonify({"error": "Not found"}), 404
    c = c.iloc[0]
    trend = (
        daily[daily["campaign_id"] == campaign_id]
        .sort_values("date")[["date", "total_calls", "connected", "contact_rate"]]
    )
    return jsonify({
        "info" : row_to_dict(c),
        "trend": [row_to_dict(r) for _, r in trend.iterrows()],
    })


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
