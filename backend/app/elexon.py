"""Thin client for the Elexon BMRS Insights API (FUELHH + WINDFOR streams)."""
import time
from datetime import date, timedelta

import pandas as pd
import requests

BASE = "https://data.elexon.co.uk/bmrs/api/v1"


def _get(path: str, params: dict, retries: int = 3) -> list:
    for attempt in range(retries):
        try:
            r = requests.get(f"{BASE}{path}", params=params,
                             headers={"Accept": "application/json"}, timeout=90)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def _chunks(start: date, end: date, days: int):
    d = start
    while d <= end:
        e = min(d + timedelta(days=days - 1), end)
        yield d, e
        d = e + timedelta(days=1)


def fetch_actuals(start: date, end: date) -> pd.DataFrame:
    rows = []
    for a, b in _chunks(start, end, 7):
        rows += _get("/datasets/FUELHH/stream", {
            "settlementDateFrom": a.isoformat(),
            "settlementDateTo": b.isoformat(),
            "fuelType": ["WIND"],
        })
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("FUELHH returned no rows")
    df = df[df["fuelType"] == "WIND"]
    out = pd.DataFrame({
        "start_time": pd.to_datetime(df["startTime"], utc=True),
        "actual_mw": df["generation"].astype(float),
    })
    return out.drop_duplicates("start_time").sort_values("start_time").reset_index(drop=True)


def fetch_forecasts(publish_from: date, publish_to: date) -> pd.DataFrame:
    rows = []
    for a, b in _chunks(publish_from, publish_to, 1):
        rows += _get("/datasets/WINDFOR/stream", {
            "publishDateTimeFrom": f"{a.isoformat()}T00:00:00Z",
            "publishDateTimeTo": f"{(b + timedelta(days=1)).isoformat()}T00:00:00Z",
        })
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("WINDFOR returned no rows")
    out = pd.DataFrame({
        "start_time": pd.to_datetime(df["startTime"], utc=True),
        "publish_time": pd.to_datetime(df["publishTime"], utc=True),
        "forecast_mw": df["generation"].astype(float),
    })
    return (out.drop_duplicates(["start_time", "publish_time"])
               .sort_values(["start_time", "publish_time"]).reset_index(drop=True))
