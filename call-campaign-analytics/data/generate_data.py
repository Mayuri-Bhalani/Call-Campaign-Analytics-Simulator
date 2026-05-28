"""
generate_data.py
Generates realistic synthetic call center datasets for the
Call Campaign Analytics Simulator.

Outputs:
  - agents.csv         : Agent roster with skills and status
  - campaigns.csv      : Campaign definitions
  - call_logs.csv      : Granular call records (last 30 days)
  - daily_summary.csv  : Aggregated daily KPIs per campaign
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUT = os.path.dirname(__file__)

# ── 1. AGENTS ──────────────────────────────────────────────────────────────
FIRST = ["James","Maria","Kevin","Priya","Daniel","Sarah","Omar","Linda",
         "Carlos","Aisha","Tyler","Nina","Raj","Emma","Chris","Fatima",
         "Michael","Julia","Andre","Mei"]
LAST  = ["Smith","Garcia","Chen","Patel","Johnson","Williams","Kim","Brown",
         "Davis","Martinez","Wilson","Anderson","Taylor","Thomas","Lee",
         "Harris","Clark","Lewis","Robinson","Walker"]

SKILLS   = ["Inbound","Outbound","Collections","Sales","Support"]
STATUSES = ["Active","On Break","Offline","In Call"]

agents = []
for i in range(1, 21):
    agents.append({
        "agent_id"     : f"AGT{i:03d}",
        "name"         : f"{random.choice(FIRST)} {random.choice(LAST)}",
        "skill"        : random.choice(SKILLS),
        "status"       : random.choices(STATUSES, weights=[50,10,20,20])[0],
        "tenure_months": random.randint(1, 60),
        "target_calls" : random.choice([60, 70, 80]),
    })

agents_df = pd.DataFrame(agents)
agents_df.to_csv(f"{OUT}/agents.csv", index=False)
print(f"✓ agents.csv ({len(agents_df)} rows)")

# ── 2. CAMPAIGNS ───────────────────────────────────────────────────────────
campaigns = [
    {"campaign_id":"CMP001","name":"Q2 Collections Drive","type":"Outbound","status":"Active",
     "start_date":"2026-04-01","end_date":"2026-06-30","target_contacts":5000,"dialer":"Five9"},
    {"campaign_id":"CMP002","name":"Product Renewal Outreach","type":"Outbound","status":"Active",
     "start_date":"2026-05-01","end_date":"2026-05-31","target_contacts":3000,"dialer":"Twilio"},
    {"campaign_id":"CMP003","name":"Customer Support Inbound","type":"Inbound","status":"Active",
     "start_date":"2026-01-01","end_date":"2026-12-31","target_contacts":10000,"dialer":"Acqueon"},
    {"campaign_id":"CMP004","name":"Win-Back Campaign","type":"Outbound","status":"Paused",
     "start_date":"2026-03-15","end_date":"2026-06-15","target_contacts":2000,"dialer":"RingCentral"},
    {"campaign_id":"CMP005","name":"New Leads May Blast","type":"Outbound","status":"Active",
     "start_date":"2026-05-15","end_date":"2026-05-31","target_contacts":1500,"dialer":"Five9"},
]
campaigns_df = pd.DataFrame(campaigns)
campaigns_df.to_csv(f"{OUT}/campaigns.csv", index=False)
print(f"✓ campaigns.csv ({len(campaigns_df)} rows)")

# ── 3. CALL LOGS (last 30 days) ─────────────────────────────────────────────
DISPOSITIONS = ["Connected","Voicemail","No Answer","Busy","Wrong Number","Do Not Call","Callback Scheduled"]
DISP_WEIGHTS  = [35, 20, 25, 8, 5, 4, 3]

call_logs = []
base_date = datetime(2026, 4, 28)
call_id   = 1

for day_offset in range(30):
    date = base_date + timedelta(days=day_offset)
    if date.weekday() >= 5:          # lighter on weekends
        daily_calls = random.randint(60, 120)
    else:
        daily_calls = random.randint(180, 320)

    for _ in range(daily_calls):
        agent    = random.choice(agents)
        campaign = random.choices(campaigns, weights=[30,20,25,10,15])[0]
        disp     = random.choices(DISPOSITIONS, weights=DISP_WEIGHTS)[0]
        duration = 0
        if disp == "Connected":
            duration = random.randint(45, 720)
        elif disp in ("Voicemail","Callback Scheduled"):
            duration = random.randint(10, 60)

        hour   = random.randint(8, 17)
        minute = random.randint(0, 59)
        ts     = date.replace(hour=hour, minute=minute, second=random.randint(0,59))

        call_logs.append({
            "call_id"      : f"CALL{call_id:06d}",
            "timestamp"    : ts.strftime("%Y-%m-%d %H:%M:%S"),
            "date"         : ts.strftime("%Y-%m-%d"),
            "agent_id"     : agent["agent_id"],
            "agent_name"   : agent["name"],
            "campaign_id"  : campaign["campaign_id"],
            "campaign_name": campaign["name"],
            "dialer"       : campaign["dialer"],
            "disposition"  : disp,
            "duration_sec" : duration,
            "is_connected" : 1 if disp == "Connected" else 0,
        })
        call_id += 1

calls_df = pd.DataFrame(call_logs)
calls_df.to_csv(f"{OUT}/call_logs.csv", index=False)
print(f"✓ call_logs.csv ({len(calls_df)} rows)")

# ── 4. DAILY SUMMARY ────────────────────────────────────────────────────────
summary = (
    calls_df
    .groupby(["date","campaign_id","campaign_name","dialer"])
    .agg(
        total_calls    = ("call_id",       "count"),
        connected      = ("is_connected",  "sum"),
        avg_duration   = ("duration_sec",  "mean"),
        total_duration = ("duration_sec",  "sum"),
    )
    .reset_index()
)
summary["contact_rate"]   = (summary["connected"] / summary["total_calls"] * 100).round(1)
summary["avg_duration"]   = summary["avg_duration"].round(0).astype(int)
summary["total_duration"] = (summary["total_duration"] / 3600).round(2)   # hours

summary.to_csv(f"{OUT}/daily_summary.csv", index=False)
print(f"✓ daily_summary.csv ({len(summary)} rows)")

print("\nAll datasets generated successfully.")
