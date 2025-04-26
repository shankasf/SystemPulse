# app/main.py

import asyncio
import logging
import time
import os
import psutil
import smtplib
from email.message import EmailMessage
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from influxdb_client import InfluxDBClient, Point, WriteOptions
import uvicorn

logging.basicConfig(level=logging.INFO)

# ─── InfluxDB Configuration ────────────────────────────────────────────────────
INFLUXDB_URL    = "http://localhost:8086"
INFLUXDB_TOKEN  = os.getenv(
    "INFLUXDB_TOKEN",
    "KabRYpBt5CK_GNLjD5h1S1lw1qyJ9EGkD5IIfU_wtgw0Qit1bQ6WKEknz50x8zUF043KWD89MytjgNFjEXw2LQ=="
)
INFLUXDB_ORG    = "SystemPulseOrg"
INFLUXDB_BUCKET = "system_metrics_bucket"

# ─── Email Alert Configuration ────────────────────────────────────────────────
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "alert@example.com")
SMTP_HOST   = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 587))
SMTP_USER   = os.getenv("SMTP_USER", "youremail@gmail.com")
SMTP_PASS   = os.getenv("SMTP_PASS", "yourpassword")

# ─── InfluxDB Client Setup ─────────────────────────────────────────────────────
client    = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))
query_api = client.query_api()

# ─── State for delta calculations ──────────────────────────────────────────────
prev_disk = psutil.disk_io_counters()
prev_net  = psutil.net_io_counters()
prev_time = time.time()

async def collect_metrics():
    # ... your existing collect_metrics implementation ...
    # (omitted here for brevity; assume all metrics collection code runs as before)
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(collect_metrics())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logging.info("Collector stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/metrics")
async def get_metrics():
    """
    Return last 1 minute of ALL measurements:
    cpu_info, cpu_usage, memory_usage, disk_io, network_activity,
    process_info, system_load, system_uptime.
    Includes tags: hostname, pid, name.
    """
    query = f'''
      from(bucket:"{INFLUXDB_BUCKET}")
        |> range(start: -1m)
    '''
    tables = query_api.query(org=INFLUXDB_ORG, query=query)
    out = []
    for table in tables:
        for r in table.records:
            # Extract tags we care about
            tags = {}
            for tag in ("hostname", "pid", "name"):
                if tag in r.values:
                    tags[tag] = r.values[tag]
            out.append({
                "time":        str(r.get_time()),
                "measurement": r.get_measurement(),
                "field":       r.get_field(),
                "value":       r.get_value(),
                **tags
            })
    return {"data": out}

@app.post("/notify/email")
async def send_email_alert(
    background_tasks: BackgroundTasks,
    subject: str,
    body: str,
    to: str = ALERT_EMAIL
):
    """
    Send an email alert asynchronously.
    """
    def _send():
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"]    = SMTP_USER
        msg["To"]      = to
        msg.set_content(body)
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    background_tasks.add_task(_send)
    return {"status": "queued"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
