from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)


def test_health_and_config():
    assert c.get("/api/health").json() == {"status": "ok"}
    assert "cutoff_local" in c.get("/api/config").json()


def test_latest_forecast_respects_cutoff():
    rows = c.get("/api/forecast/latest?start=2026-01-10&end=2026-01-10").json()
    assert rows
    for r in rows:
        if r["publish_time"]:
            assert r["publish_time"] <= r["cutoff"]


def test_metrics_and_horizon():
    m = c.get("/api/metrics").json()
    assert m["overall"]["n"] > 0 and m["by_hour"] and m["by_day"]
    h = c.get("/api/horizon-error").json()
    assert h and h[-1]["mae_mw"] > h[0]["mae_mw"]  # error should grow with horizon
