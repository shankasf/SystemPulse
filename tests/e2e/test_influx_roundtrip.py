# tests/e2e/test_influx_roundtrip.py

import time
import pytest
import httpx
from testcontainers.influxdb import InfluxDbContainer
from influxdb_client import InfluxDBClient, Point, WriteOptions

def test_write_and_query_against_real_influx():
    # Boot InfluxDB v2.6 with the one‑time setup env vars
    container = (
        InfluxDbContainer("influxdb:2.6")
        .with_env("DOCKER_INFLUXDB_INIT_MODE", "setup")
        .with_env("DOCKER_INFLUXDB_INIT_USERNAME", "admin")
        .with_env("DOCKER_INFLUXDB_INIT_PASSWORD", "admin123")
        .with_env("DOCKER_INFLUXDB_INIT_ORG", "testorg")
        .with_env("DOCKER_INFLUXDB_INIT_BUCKET", "testbucket")
        .with_env("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", "admintoken123")
    )

    with container as influx:
        url = influx.get_url()  # e.g. http://127.0.0.1:XXXXX

        # 1) Wait for /health to return pass
        client = httpx.Client()
        for _ in range(15):
            try:
                r = client.get(f"{url}/health", timeout=1.0)
                if r.status_code == 200 and r.json().get("status") == "pass":
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            pytest.skip("InfluxDB did not become healthy in time")

        # 2) Connect via the Python SDK
        influx_client = InfluxDBClient(url=url, token="admintoken123", org="testorg")
        write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))
        query_api = influx_client.query_api()

        # 3) Write a single point
        write_api.write(bucket="testbucket", record=Point("cpu_usage").field("test_field", 42))

        # give the write a moment to land
        time.sleep(1)

        # 4) Query it back
        flux = (
            'from(bucket:"testbucket") '
            '|> range(start: -1m) '
            ' |> filter(fn: (r) => r["_measurement"] == "cpu_usage")'
        )
        tables = query_api.query(org="testorg", query=flux)

        # 5) Assert at least one record is present
        assert tables and any(tbl.records for tbl in tables)
