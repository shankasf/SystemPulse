# conftest.py
import asyncio
import pytest
from fastapi.testclient import TestClient
import app.main as m

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture()
def test_client():
    return TestClient(m.app)

@pytest.fixture()
def patch_query(monkeypatch):
    """Stub m.query_api to return a single cpu_usage record."""
    class Rec:
        def __init__(self):
            from datetime import datetime
            self._t = datetime.utcnow()
        def get_time(self):        return self._t
        def get_measurement(self): return "cpu_usage"
        def get_field(self):       return "usage_percent"
        def get_value(self):       return 55.0

    class Table:
        def __init__(self):
            self.records = [Rec()]

    class DummyQueryAPI:
        def query(self, *args, **kwargs):
            return [Table()]

    monkeypatch.setattr(m, "query_api", DummyQueryAPI())
    yield
