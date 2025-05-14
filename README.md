# SystemPulse

SystemPulse is a real-time system monitoring tool built with FastAPI, InfluxDB 2.x, and a responsive React dashboard. It continuously captures system metrics like CPU, memory, disk, network, and running processes every 5 seconds. The application also provides alerts, data dumps, and a metrics API for live dashboards or external integrations.

---

## Table of Contents

1. Features
2. Architecture & Design
3. Prerequisites
4. Project Structure
5. Setup & Execution
6. Collected Metrics
7. Notification & Monitoring
8. Data Logging & Persistence
9. Testing Overview
10. Code Quality & Repository Guidelines

---

## 1. Features

1. Real-time system resource monitoring (CPU, RAM, disk I/O, network, uptime, process stats)
2. Live metrics collected every 5 seconds using `psutil`
3. FastAPI backend with `/metrics` endpoint delivering JSON metrics from InfluxDB
4. InfluxDB 2.x integration with Flux query support
5. Telegram alerts for high CPU or memory usage (>72%)
6. Lightweight React dashboard (localhost:3000) with live charts & top process table
7. Automatic file-based metric dump to `/metrics/` every 5 minutes
8. Sortable process table, capped to 100% CPU normalized over total cores
9. Fully modular, with unit tests and integration coverage
10. Ready-to-use with `uvicorn`, Docker, and npm

---

## 2. Architecture & Design

The application follows a modular architecture with clean separation between data collection, API services, and UI rendering. System metrics are written into a time-series database (InfluxDB) and queried via RESTful APIs consumed by the React frontend.

```
+-------------+        +-------------+       +-------------+       +------------------+
|  FastAPI    |  -->   |  InfluxDB   | <-->  |  React UI   | <---> |  Your Browser    |
|  main.py    |        |  2.7 local  |       |  /frontend   |       | (localhost:3000) |
+-------------+        +-------------+       +-------------+       +------------------+
↑
└── async task: collect_metrics()
    (CPU, Memory, Disk, Net, Processes)
```

---

## 3. Prerequisites

* Python 3.10+
* Node.js + npm (for frontend)
* Docker (for local InfluxDB)
* Telegram Bot Token & Chat ID (optional for alerts)

---

## 4. Project Structure

```
SystemPulse/
├── app/
│   └── main.py                # FastAPI backend + async collector
├── frontend/                  # React.js dashboard
│   ├── src/components/        # Chart & table modules
│   └── App.jsx, index.jsx
├── metrics/                   # Auto-generated metric logs every 5 mins
├── tests/
│   ├── unit/                  # test_collect_metrics.py
│   └── integration/           # test_api_metrics.py
├── requirements.txt
├── requirements-dev.txt       # pytest, coverage, testcontainers
└── README.md
```

---

## 5. Setup & Execution

### 5.1 Clone & Install Backend

```bash
git clone https://github.com/yourorg/SystemPulse.git
cd SystemPulse
python -m venv .venv
. .venv/Scripts/activate     # or `source .venv/bin/activate`
pip install -r requirements.txt
```

### 5.2 Run InfluxDB Locally

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

Visit [http://localhost:8086](http://localhost:8086) to confirm.

### 5.3 Start the Backend API

Run from project root directory:

```bash
python -m uvicorn app.main:app --reload
```

Watch terminal for:

```
INFO:root: Wrote full system metrics
```

### 5.4 Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view live dashboard.

---

## 6. Collected Metrics

| Measurement        | Fields                                                   |
| ------------------ | -------------------------------------------------------- |
| `cpu_info`         | `current_mhz`, `min_mhz`, `max_mhz`, `cores`             |
| `cpu_usage`        | `usage_pct`, `load_1m`, `load_5m`, `load_15m`            |
| `memory_usage`     | `used_mb`, `free_mb`, `swap_mb`, `total_mb`              |
| `disk_io`          | `read_mb_s`, `write_mb_s`, `read_iops`, `write_iops`     |
| `network_activity` | `sent_mb_s`, `recv_mb_s`, `packets_sent`, `packets_recv` |
| `system_uptime`    | `uptime_s`                                               |
| `process_info`     | tags: `pid`, `name`; fields: `cpu_pct`, `mem_pct`        |

---

## 7. Notification & Monitoring

SystemPulse integrates Telegram bot alerts.
Enable by adding to `.env` or environment:

```
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=yyy
```

Triggers:

* CPU usage > 72%
* Memory usage > 72%

Frontend shows toast popups for recent anomalies.

---

## 8. Data Logging & Persistence

Every 5 minutes, a JSON `.txt` file is dumped to `metrics/`, containing the last 5 minutes of readings:

```bash
metrics/metrics_20250421_120000.txt
```

Each file includes timestamped entries of all metric types, ideal for audit logs or offline analysis.

---

## 9. Testing Overview

* Unit Tests – Found under `tests/unit/test_collect_metrics.py`

  * Tests metric values, psutil logic, Influx `Point` formatting

* Integration Tests – `tests/integration/test_api_metrics.py`

  * Covers `/metrics` route behavior and output structure

Run all tests:

```bash
pip install -r requirements-dev.txt
pytest -v --cov=app --cov-report=term-missing
```

* 85%+ coverage verified
* Bug tracking and test feedback loop handled via commit history and `main.py` improvements

---

## 10. Code Quality & Repository Guidelines

* Source code is PEP8-compliant, modular, and documented
* All logic is located in `main.py` for easy navigation
* Frontend is split into reusable chart/table components
* Repository includes proper `.gitignore`, lockfiles, and organized dependencies
* Commits follow incremental structure (e.g. UI fix, telemetry patch, dump logic)

---

