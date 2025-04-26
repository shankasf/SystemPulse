# tests/integration/test_api_metrics.py

def test_metrics_endpoint_ok(patch_query, test_client):
    """
    Using the patch_query fixture (which returns one cpu_usage record),
    GET /metrics should return that record.
    """
    resp = test_client.get("/metrics")
    assert resp.status_code == 200

    data = resp.json()["data"]
    assert isinstance(data, list) and data, "expected a non‑empty list"

    rec = data[0]
    assert rec["measurement"] == "cpu_usage"
    assert rec["field"] == "usage_percent"
    assert rec["value"] == 55.0


def test_metrics_endpoint_empty(monkeypatch, test_client):
    """
    If query_api.query() returns no tables, /metrics should return {"data":[]}.
    """
    import app.main as m

    class DummyQueryAPI:
        def query(self, *args, **kwargs):
            return []  # simulate no data

    monkeypatch.setattr(m, "query_api", DummyQueryAPI())

    resp = test_client.get("/metrics")
    assert resp.status_code == 200
    assert resp.json() == {"data": []}


def test_metrics_endpoint_includes_memory(monkeypatch, test_client):
    """
    Simulate a memory_usage record coming back so we exercise that branch.
    """
    import app.main as m

    class RecMem:
        def __init__(self):
            from datetime import datetime
            self._t = datetime.utcnow()
        def get_time(self):
            return self._t
        def get_measurement(self):
            return "memory_usage"
        def get_field(self):
            return "used_memory_mb"
        def get_value(self):
            return 123.45

    class Table:
        def __init__(self):
            self.records = [RecMem()]

    class DummyQueryAPI:
        def query(self, *args, **kwargs):
            return [Table()]

    monkeypatch.setattr(m, "query_api", DummyQueryAPI())

    resp = test_client.get("/metrics")
    assert resp.status_code == 200

    data = resp.json()["data"]
    assert any(r["measurement"] == "memory_usage" for r in data), "memory_usage record missing"


def test_metrics_endpoint_cpu(patch_query, test_client):
    """
    Re‑use the cpu stub from patch_query to verify the CPU branch.
    """
    resp = test_client.get("/metrics")
    assert resp.status_code == 200

    data = resp.json()["data"]
    assert any(
        (r["measurement"] == "cpu_usage"
         and r["field"] == "usage_percent"
         and r["value"] == 55.0)
        for r in data
    ), "cpu_usage record missing or incorrect"
