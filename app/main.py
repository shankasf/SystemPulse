import os
import time
import asyncio
import logging
import psutil
import requests
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from influxdb_client import InfluxDBClient, Point, WriteOptions
import uvicorn

# ─── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# ─── InfluxDB Configuration ────────────────────────────────────────────────────
INFLUXDB_URL    = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN  = os.getenv("INFLUXDB_TOKEN", "KabRYpBt5CK_GNLjD5h1S1lw1qyJ9EGkD5IIfU_wtgw0Qit1bQ6WKEknz50x8zUF043KWD89MytjgNFjEXw2LQ==")
INFLUXDB_ORG    = os.getenv("INFLUXDB_ORG", "SystemPulseOrg")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "system_metrics_bucket")

# ─── Telegram Bot Configuration ────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7541875255:AAFsaW2dOmRA-VZxE-umbfvxcqRZMC-XUbQ")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "2117478694")  # your numeric chat ID

# ─── Alert Thresholds ──────────────────────────────────────────────────────────
CPU_ALERT_THRESHOLD = float(os.getenv("CPU_ALERT_THRESHOLD", 72.0))  # %
MEM_ALERT_THRESHOLD = float(os.getenv("MEM_ALERT_THRESHOLD", 72.0))  # %

# ─── Periodic Dump Configuration ──────────────────────────────────────────────
DUMP_INTERVAL_SECONDS = 300  # every 5 minutes
DUMP_FOLDER           = os.getenv("METRICS_DUMP_FOLDER", "metrics")

# ─── InfluxDB Client Setup ─────────────────────────────────────────────────────
influx_client = InfluxDBClient(
    url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))
query_api = influx_client.query_api()

# ─── Helper: Send Telegram Notification ─────────────────────────────────────────
def send_telegram_notification(message: str) -> None:
    if not TELEGRAM_CHAT_ID:
        logging.warning("Telegram chat ID not set; skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        logging.info(f"Telegram alert sent: {message}")
    except requests.RequestException as e:
        logging.error(f"Failed to send Telegram alert: {e}")

# ─── State for Delta Calculations and Dump Timing ──────────────────────────────
prev_disk = psutil.disk_io_counters()
prev_net  = psutil.net_io_counters()
prev_time = time.time()
last_dump = time.time()

async def collect_metrics():
    """
    Background task: collect system metrics, write to InfluxDB,
    send alerts when thresholds exceeded, and dump metrics to txt files.
    """
    # Write static CPU info once
    freq = psutil.cpu_freq() or (0.0, 0.0, 0.0)
    cpu_info = (
        Point("cpu_info")
        .tag("hostname", "server1")
        .field("current_mhz",     freq.current)
        .field("min_mhz",         freq.min)
        .field("max_mhz",         freq.max)
        .field("physical_cores",  psutil.cpu_count(logical=False))
        .field("logical_threads", psutil.cpu_count(logical=True))
    )
    write_api.write(bucket=INFLUXDB_BUCKET, record=cpu_info)

    global prev_disk, prev_net, prev_time, last_dump
    while True:
        now = time.time()
        interval = max(now - prev_time, 1)

        # ─── CPU Usage & Alert ────────────────────────────────────────────────
        cpu_pct = psutil.cpu_percent(interval=None)
        load1, load5, load15 = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0.0, 0.0, 0.0)
        write_api.write(bucket=INFLUXDB_BUCKET, record=(
            Point("cpu_usage")
            .tag("hostname", "server1")
            .field("usage_pct", cpu_pct)
            .field("load_1m",    load1)
            .field("load_5m",    load5)
            .field("load_15m",   load15)
        ))
        if cpu_pct > CPU_ALERT_THRESHOLD:
            send_telegram_notification(f"🚨 High CPU Alert: {cpu_pct:.1f}% (threshold {CPU_ALERT_THRESHOLD}%)")

        # ─── Memory Usage & Alert ─────────────────────────────────────────────
        vm = psutil.virtual_memory()
        mem_used_pct = vm.percent
        write_api.write(bucket=INFLUXDB_BUCKET, record=(
            Point("memory_usage")
            .tag("hostname", "server1")
            .field("total_mb", vm.total / 1e6)
            .field("used_mb",  vm.used / 1e6)
            .field("free_mb",  vm.available / 1e6)
            .field("swap_mb",  psutil.swap_memory().used / 1e6)
        ))
        if mem_used_pct > MEM_ALERT_THRESHOLD:
            send_telegram_notification(f"🚨 High Memory Alert: {mem_used_pct:.1f}% (threshold {MEM_ALERT_THRESHOLD}%)")

        # ─── Disk I/O Metrics ────────────────────────────────────────────────
        cur_disk = psutil.disk_io_counters()
        read_bytes  = cur_disk.read_bytes  - prev_disk.read_bytes
        write_bytes = cur_disk.write_bytes - prev_disk.write_bytes
        write_api.write(bucket=INFLUXDB_BUCKET, record=(
            Point("disk_io")
            .tag("hostname", "server1")
            .field("read_mb_s",  read_bytes  / 1e6 / interval)
            .field("write_mb_s", write_bytes / 1e6 / interval)
        ))
        prev_disk = cur_disk

        # ─── Network Activity Metrics ───────────────────────────────────────
        cur_net = psutil.net_io_counters()
        sent_bytes = cur_net.bytes_sent - prev_net.bytes_sent
        recv_bytes = cur_net.bytes_recv - prev_net.bytes_recv
        write_api.write(bucket=INFLUXDB_BUCKET, record=(
            Point("network_activity")
            .tag("hostname", "server1")
            .field("sent_mb_s", sent_bytes / 1e6 / interval)
            .field("recv_mb_s", recv_bytes / 1e6 / interval)
        ))
        prev_net = cur_net

        # ─── Per-Process Metrics ──────────────────────────────────────────────
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            info = p.info
            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("process_info")
                .tag("hostname", "server1")
                .tag("pid",   str(info["pid"]))
                .tag("name",  info["name"] or "unknown")
                .field("cpu_pct", info["cpu_percent"])
                .field("mem_pct", info["memory_percent"])
            ))

        # ─── System Load & Uptime ──────────────────────────────────────────────
        write_api.write(bucket=INFLUXDB_BUCKET, record=(
            Point("system_load")
            .tag("hostname", "server1")
            .field("load_1m",  load1)
            .field("load_5m",  load5)
            .field("load_15m", load15)
        ))
        uptime_sec = now - psutil.boot_time()
        write_api.write(bucket=INFLUXDB_BUCKET, record=(
            Point("system_uptime")
            .tag("hostname", "server1")
            .field("uptime_s", uptime_sec)
        ))

        prev_time = now
        logging.info("Wrote full system metrics to InfluxDB")

        # ─── Periodic Dump to File ────────────────────────────────────────────
        if now - last_dump >= DUMP_INTERVAL_SECONDS:
            try:
                flux = f'''from(bucket:"{INFLUXDB_BUCKET}")
                  |> range(start: -5m)'''
                tables = query_api.query(org=INFLUXDB_ORG, query=flux)
                records = []
                for table in tables:
                    for r in table.records:
                        record = {
                            "time":        str(r.get_time()),
                            "measurement": r.get_measurement(),
                            "field":       r.get_field(),
                            "value":       r.get_value()
                        }
                        # include tags
                        for k, v in r.values.items():
                            if k not in ("_time", "_value", "_field", "_measurement"):
                                record[k] = v
                        records.append(record)

                os.makedirs(DUMP_FOLDER, exist_ok=True)
                filename = os.path.join(
                    DUMP_FOLDER,
                    datetime.now().strftime("metrics_%Y%m%d_%H%M%S.txt")
                )
                with open(filename, "w") as f:
                    json.dump(records, f, indent=2)
                logging.info(f"Metrics dumped to {filename}")
            except Exception as e:
                logging.error(f"Failed to dump metrics: {e}")
            last_dump = now

        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(collect_metrics())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logging.info("Collector stopped")

# ─── FastAPI App & CORS ────────────────────────────────────────────────────────
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics")
async def get_metrics():
    """
    Return the last 1 minute of all metrics.
    """
    flux = f'''from(bucket:"{INFLUXDB_BUCKET}")
      |> range(start: -1m)'''
    tables = query_api.query(org=INFLUXDB_ORG, query=flux)
    out = []
    for table in tables:
        for r in table.records:
            data = {
                "time":        str(r.get_time()),
                "measurement": r.get_measurement(),
                "field":       r.get_field(),
                "value":       r.get_value()
            }
            for k, v in r.values.items():
                if k not in ("_time", "_value", "_field", "_measurement"):
                    data[k] = v
            out.append(data)
    return {"data": out}

@app.get("/processes")
async def list_processes():
    """
    Return the last 1 minute of per-process metrics,
    grouping cpu_pct & mem_pct together per PID.
    """
    flux = f'''
    from(bucket:"{INFLUXDB_BUCKET}")
      |> range(start: -1m)
      |> filter(fn: (r) => r["_measurement"] == "process_info")
    '''
    tables = query_api.query(org=INFLUXDB_ORG, query=flux)

    proc_map: dict[str, dict] = {}
    for table in tables:
        for r in table.records:
            pid = r.values.get("pid")
            name = r.values.get("name")
            field = r.get_field()       # either "cpu_pct" or "mem_pct"
            val   = r.get_value()       # the numeric value

            if pid is None:
                continue

            if pid not in proc_map:
                proc_map[pid] = {
                    "pid": pid,
                    "name": name,
                    "cpu_pct": 0.0,
                    "mem_pct": 0.0,
                }
            proc_map[pid][field] = val

    # Return the grouped list
    return {"processes": list(proc_map.values())}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
