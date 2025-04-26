# SystemPulse

A lightweight FastAPI service that collects system performance metrics (CPU, memory, disk, network, processes) and writes them into InfluxDB, with a `/metrics` HTTP endpoint for querying the last minute of data. Includes full test coverage (unit, integration, end-to-end) and a CI pipeline.

---

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Project Structure](#project-structure)  
4. [Getting Started](#getting-started)  
   - [1. Clone & Install](#1-clone--install)  
   - [2. Run InfluxDB](#2-run-influxdb)  
   - [3. Start the API](#3-start-the-api)  
   - [4. Query Metrics](#4-query-metrics)  
5. [Metrics Collected](#metrics-collected)  
6. [Testing](#testing)  
7. [CI Pipeline](#ci-pipeline)  
8. [Future Enhancements](#future-enhancements)  

---

## Features

- **Background collection** every 5 seconds of:
  - **CPU** utilization & load averages  
  - **Memory** total & used  
  - **Disk** total & free space (root)  
  - **Network** bytes sent & received  
  - **Process** snapshot: PID, name, CPU %, memory %  
  - **Static CPU info**: frequency, physical cores, logical threads  
- **InfluxDB 2.x** integration (writes & Flux queries)  
- **FastAPI** `/metrics` endpoint returning JSON of the last 1 minute of data  
- **Visualization script** for quick local charts  
- **Tests**:
  - **Unit**: `collect_metrics()` logic  
  - **Integration**: `/metrics` HTTP behavior under mocked responses  
  - **E2E**: real InfluxDB container via Testcontainers  
- **Coverage** enforced at ≥ 85%  
- **CI** example (GitHub Actions) bringing up InfluxDB service and running tests  

---

## Prerequisites

- Python 3.10+  
- Docker (for local InfluxDB or CI)  
- (Optional) Minikube/Kubernetes if using the provided `influxdb.yaml`  

---

## Project Structure

```plaintext
SystemPulse/
├── app/
│   └── main.py                # core FastAPI app + collector
├── influxdb.yaml              # k8s Deployment & Service for InfluxDB
├── visualize_metrics/
│   └── plot_metrics.py        # standalone script to pull & plot data
├── tests/
│   ├── unit/
│   │   └── test_collect_metrics.py
│   ├── integration/
│   │   └── test_api_metrics.py
│   └── e2e/
│       └── test_influx_roundtrip.py
├── conftest.py                # shared pytest fixtures
├── requirements.txt           # runtime deps
├── requirements-dev.txt       # pytest, testcontainers, httpx, etc.
└── README.md                  # this file
```  

---

## Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/yourorg/SystemPulse.git
cd SystemPulse
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run InfluxDB

**Option A: Docker**

```bash
docker run -d \
  --name influxdb \
  -p 8086:8086 \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=admin \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=admin123 \
  -e DOCKER_INFLUXDB_INIT_ORG=SystemPulseOrg \
  -e DOCKER_INFLUXDB_INIT_BUCKET=system_metrics_bucket \
  -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=yourtoken \
  influxdb:2.6
```

**Option B: Kubernetes**

```bash
kubectl apply -f influxdb.yaml
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

You should see logs every 5 seconds:

```
INFO  app.main: Wrote CPU, memory, disk, network and 42 processes
```

### 4. Query Metrics

```bash
curl http://127.0.0.1:8000/metrics
```

Returns JSON:

```json
{
  "data": [
    {
      "time": "2025-04-21T12:00:05Z",
      "measurement": "cpu_usage",
      "field": "usage_percent",
      "value": 12.3
    },
    …
  ]
}
```

---

## Metrics Collected

| Measurement      | Fields                                           |
|------------------|--------------------------------------------------|
| `cpu_info`       | `current_mhz`, `min_mhz`, `max_mhz`, `physical_cores`, `logical_threads` |
| `cpu_usage`      | `usage_percent`, `load_avg_1m`, `load_avg_5m`, `load_avg_15m` |
| `memory_usage`   | `total_mb`, `used_mb`                            |
| `disk_usage`     | `total_gb`, `free_gb`                            |
| `network_usage`  | `sent_mb`, `recv_mb`                             |
| `process_info`   | tags: `pid`, `name`; fields: `cpu_pct`, `mem_pct` |

---

## Testing

Install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests with coverage:

```bash
pytest -vv --cov=app --cov-report=term-missing --cov-fail-under=85
```

This will show any untested lines and fail if coverage < 85%.

---

## Future Enhancements

- Persist per-process history (instead of snapshot)  
- Add authentication + metrics dashboard UI  
- Support custom collection intervals via config  
- Push metrics to other backends (Prometheus, Graphite)  

