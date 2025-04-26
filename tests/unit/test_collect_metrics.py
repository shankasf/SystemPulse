import asyncio
import pytest
import app.main as m

class DummyWriteAPI:
    def __init__(self):
        self.records = []
    def write(self, bucket, record):
        self.records.append((bucket, record))

@pytest.mark.asyncio
async def test_collect_metrics_writes_points(monkeypatch):
    dummy = DummyWriteAPI()
    monkeypatch.setattr(m, "write_api", dummy)

    task = asyncio.create_task(m.collect_metrics())
    await asyncio.sleep(0.2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    measurements = {pt._name for _, pt in dummy.records}
    assert {"cpu_usage", "memory_usage"} <= measurements
