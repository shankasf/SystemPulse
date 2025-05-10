# SystemPulse

**SystemPulse** is a real-time system monitoring tool built with **FastAPI**, **InfluxDB 2.x**, and a React-based dashboard. It captures CPU, memory, disk, network, and process stats every 5 seconds and visualizes them live. Supports Telegram alerts and metrics export. Ideal for system admins, developers, or hobbyists who want lightweight local observability.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)

   * [1. Clone & Install](#1-clone--install)
   * [2. Run InfluxDB](#2-run-influxdb)
   * [3. Start the Backend API](#3-start-the-backend-api)
   * [4. Start the Frontend](#4-start-the-frontend)
6. [Metrics Captured](#metrics-captured)
7. [Alerts & Notifications](#alerts--notifications)
8. [File-Based Metrics Dump](#file-based-metrics-dump)
9. [Testing](#testing)
10. [Future Enhancements](#future-enhancements)

---

## Features

✅ FastAPI-based backend service
✅ CPU, memory, disk, network, uptime & process info every 5s
✅ InfluxDB 2.x integration with Flux queries
✅ Real-time **React dashboard** at `http://localhost:3000`
✅ Alerts via **Telegram bot** for CPU/Memory overuse
✅ Auto-dumps last 5m metrics to `metrics/` every 5 minutes
✅ Sortable process table with usage normalization
✅ Responsive UI & notification toasts
✅ CLI + GUI compatible

---

## Architecture

```
+-------------+        +-------------+       +-------------+       +------------------+
|  FastAPI    |  -->   |  InfluxDB   | <-->  |  React UI   | <---> |  Your Browser    |
|  main.py    |        |  2.7 local  |       |  /frontend   |       | (localhost:3000) |
+-------------+        +-------------+       +-------------+       +------------------+
    ↑
    └───── background asyncio collector
           (psutil: CPU, RAM, DISK, NET, PROCS)
```

---

## Prerequisites

* Python 3.10+
* Node.js + npm (for frontend)
* Docker (for InfluxDB)
* (Optional) Telegram account & bot token

---

## Project Structure

```
SystemPulse/
├── app/
│   └── main.py                # FastAPI app + metric collector
├── frontend/                  # React dashboard
│   ├── src/                   # Charts, tables, UI logic
│   └── package.json
├── metrics/                   # Auto-dumped .txt files every 5 mins
├── tests/                     # pytest-based tests (optional)
├── .env                       # InfluxDB & Telegram secrets (optional)
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/yourorg/SystemPulse.git
cd SystemPulse
python -m venv .venv
. .venv/Scripts/activate   # Windows
# or
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 2. Run InfluxDB 2.x

```bash
docker run -d --name influxdb -p 8086:8086 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=admin123 \
  -e DOCKER_INFLUXDB_INIT_ORG=SystemPulseOrg \
  -e DOCKER_INFLUXDB_INIT_BUCKET=system_metrics_bucket \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=yourtoken \
  influxdb:2.7
```

Then visit [http://localhost:8086](http://localhost:8086) and complete setup if needed.

### 3. Start the Backend API (from project root)

```bash
python -m uvicorn app.main:app --reload
```

This will:

* Launch FastAPI on `localhost:8000`
* Start collecting metrics every 5s
* Dump metrics to `metrics/` folder every 5m
* Send Telegram alerts if enabled

### 4. Start the Frontend (React Dashboard)

```bash
cd frontend
npm install
npm run dev
```

Now visit [http://localhost:3000](http://localhost:3000)
You’ll see live charts and top processes.

---

## Metrics Captured

| Measurement        | Fields                                                   |
| ------------------ | -------------------------------------------------------- |
| `cpu_info`         | `current_mhz`, `min_mhz`, `max_mhz`, `cores`             |
| `cpu_usage`        | `usage_pct`, `load_1m`, `load_5m`, `load_15m`            |
| `memory_usage`     | `used_mb`, `free_mb`, `swap_mb`, `total_mb`              |
| `disk_io`          | `read_mb_s`, `write_mb_s`, `read_iops`, `write_iops`     |
| `network_activity` | `sent_mb_s`, `recv_mb_s`, `packets_sent`, `packets_recv` |
| `system_uptime`    | `uptime_s`                                               |
| `process_info`     | tags: `pid`, `name` → `cpu_pct`, `mem_pct`               |

---

## Alerts & Notifications

📲 SystemPulse supports **Telegram alerts** out-of-the-box.
To enable:

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Get your bot token
3. Start a chat with your bot and get your `chat_id` via [@userinfobot](https://t.me/userinfobot)

Then in your `.env` or OS environment:

```
TELEGRAM_BOT_TOKEN=your:bot_token
TELEGRAM_CHAT_ID=123456789
```

Alerts fire if:

* CPU usage > 72%
* Memory usage > 72%

---

## File-Based Metrics Dump

Every 5 minutes, a `.txt` file with the last 5 minutes of all metrics is saved to:

```bash
/metrics/metrics_YYYYMMDD_HHMMSS.txt
```

This helps you keep historical records, even without InfluxDB queries.

---

## Testing

Unit and integration tests coming soon.

For now, test your FastAPI endpoints manually:

```bash
curl http://localhost:8000/metrics
curl http://localhost:8000/processes
```

You should get live metric JSON.

---

---

> MIT Licensed · Built by Devs, for Devs · Contributions Welcome 🚀
