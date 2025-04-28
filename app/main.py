import asyncio
import logging
import time
import os
import psutil
from fastapi import FastAPI
from contextlib import asynccontextmanager
from influxdb_client import InfluxDBClient, Point, WriteOptions
import uvicorn

logging.basicConfig(level=logging.INFO)

# ─── InfluxDB Configuration ────────────────────────────────────────────────────
INFLUXDB_URL    = "http://localhost:8086"
INFLUXDB_TOKEN  = os.getenv("INFLUXDB_TOKEN", "KabRYpBt5CK_GNLjD5h1S1lw1qyJ9EGkD5IIfU_wtgw0Qit1bQ6WKEknz50x8zUF043KWD89MytjgNFjEXw2LQ==")
INFLUXDB_ORG    = "SystemPulseOrg"
INFLUXDB_BUCKET = "system_metrics_bucket"

# ─── InfluxDB Client Setup ─────────────────────────────────────────────────────
client    = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=WriteOptions(batch_size=1))
query_api = client.query_api()

# ─── State for delta calculations ──────────────────────────────────────────────
prev_disk = psutil.disk_io_counters()
prev_net  = psutil.net_io_counters()
prev_time = time.time()

async def collect_metrics():
    freq = psutil.cpu_freq()
    cpu_info = (
        Point("cpu_info")
        .tag("hostname","server1")
        .field("current_mhz",     freq.current)
        .field("min_mhz",         freq.min)
        .field("max_mhz",         freq.max)
        .field("physical_cores",  psutil.cpu_count(logical=False))
        .field("logical_threads", psutil.cpu_count(logical=True))
    )
    write_api.write(bucket=INFLUXDB_BUCKET, record=cpu_info)

    global prev_disk, prev_net, prev_time
    while True:
        try:
            now      = time.time()
            interval = now - prev_time

            cpu_pct = psutil.cpu_percent(interval=None)
            load1, load5, load15 = (
                psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0.0,0.0,0.0)
            )
            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("cpu_usage")
                .tag("hostname","server1")
                .field("usage_pct", cpu_pct)
                .field("load_1m",    load1)
                .field("load_5m",    load5)
                .field("load_15m",   load15)
            ))

            vm = psutil.virtual_memory()
            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("memory_usage")
                .tag("hostname","server1")
                .field("total_mb", vm.total/1e6)
                .field("used_mb",  vm.used/1e6)
                .field("free_mb",  vm.available/1e6)
                .field("swap_mb",  psutil.swap_memory().used/1e6)
            ))

            cur_disk = psutil.disk_io_counters()
            read_bytes  = cur_disk.read_bytes  - prev_disk.read_bytes
            write_bytes = cur_disk.write_bytes - prev_disk.write_bytes
            read_count  = cur_disk.read_count  - prev_disk.read_count
            write_count = cur_disk.write_count - prev_disk.write_count
            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("disk_io")
                .tag("hostname","server1")
                .field("read_mb_s",  read_bytes/1e6/interval)
                .field("write_mb_s", write_bytes/1e6/interval)
                .field("read_iops",  read_count/interval)
                .field("write_iops", write_count/interval)
            ))
            prev_disk = cur_disk

            cur_net = psutil.net_io_counters()
            sent_bytes = cur_net.bytes_sent - prev_net.bytes_sent
            recv_bytes = cur_net.bytes_recv - prev_net.bytes_recv
            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("network_activity")
                .tag("hostname","server1")
                .field("sent_mb_s",   sent_bytes/1e6/interval)
                .field("recv_mb_s",   recv_bytes/1e6/interval)
                .field("packets_sent",   cur_net.packets_sent - prev_net.packets_sent)
                .field("packets_recv",   cur_net.packets_recv - prev_net.packets_recv)
                .field("err_in",         cur_net.errin  - prev_net.errin)
                .field("err_out",        cur_net.errout - prev_net.errout)
                .field("drop_in",        cur_net.dropin - prev_net.dropin)
                .field("drop_out",       cur_net.dropout- prev_net.dropout)
            ))
            prev_net  = cur_net

            for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):
                info = p.info
                write_api.write(bucket=INFLUXDB_BUCKET, record=(
                    Point("process_info")
                    .tag("hostname","server1")
                    .tag("pid",  str(info["pid"]))
                    .tag("name", info["name"] or "unknown")
                    .field("cpu_pct", info["cpu_percent"])
                    .field("mem_pct", info["memory_percent"])
                ))

            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("system_load")
                .tag("hostname","server1")
                .field("load_1m",  load1)
                .field("load_5m",  load5)
                .field("load_15m", load15)
            ))

            uptime_sec = now - psutil.boot_time()
            write_api.write(bucket=INFLUXDB_BUCKET, record=(
                Point("system_uptime")
                .tag("hostname","server1")
                .field("uptime_s", uptime_sec)
            ))

            prev_time = now
            logging.info("Wrote full system metrics")
        except Exception as e:
            logging.error(f"Error collecting metrics: {e}")
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

app = FastAPI(lifespan=lifespan)

@app.get("/metrics")
async def get_metrics():
    query = f'''from(bucket:"{INFLUXDB_BUCKET}")
      |> range(start: -1m)'''
    tables = query_api.query(org=INFLUXDB_ORG, query=query)
    out = []
    for table in tables:
        for r in table.records:
            tag_dict = {k: v for k, v in r.values.items()
                        if k not in ("_time", "_value", "_field", "_measurement")}
            out.append({
                "time":        str(r.get_time()),
                "measurement": r.get_measurement(),
                "field":       r.get_field(),
                "value":       r.get_value(),
                "tags":        tag_dict,
            })
    return {"data": out}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
