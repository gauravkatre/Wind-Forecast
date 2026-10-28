from datetime import date
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from . import config, metrics, selection
from .data import load_data

app = FastAPI(title="Wind Forecast Portal API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

Start = Query(date.fromisoformat(config.RANGE_START))
End = Query(date.fromisoformat(config.RANGE_END))
Cutoff = Query(config.CUTOFF_LOCAL, pattern=r"^\d{2}:\d{2}$",
               description="D-1 decision cutoff, UK local time HH:MM")


@lru_cache(maxsize=16)
def _evaluation(cutoff: str) -> pd.DataFrame:
    actuals, forecasts, _ = load_data()
    return selection.join_actuals(selection.select_latest_available(forecasts, cutoff), actuals)


def _slice(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    s = pd.Timestamp(start, tz="UTC")
    e = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
    return df[(df["start_time"] >= s) & (df["start_time"] < e)]


def _records(df: pd.DataFrame) -> list[dict]:
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[c]):
            out[c] = out[c].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out.astype(object).where(out.notna(), None).to_dict("records")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/config")
def get_config():
    _, _, is_sample = load_data()
    return {"cutoff_local": config.CUTOFF_LOCAL, "timezone": config.TZ,
            "range_start": config.RANGE_START, "range_end": config.RANGE_END,
            "using_sample_data": is_sample}


@app.get("/api/actuals")
def actuals(start: date = Start, end: date = End):
    a, _, _ = load_data()
    return _records(_slice(a, start, end))


@app.get("/api/forecast/latest")
def forecast_latest(start: date = Start, end: date = End, cutoff: str = Cutoff):
    """Actual vs the latest forecast that was available at the D-1 cutoff."""
    return _records(_slice(_evaluation(cutoff), start, end))


@app.get("/api/metrics")
def get_metrics(start: date = Start, end: date = End, cutoff: str = Cutoff):
    df = _slice(_evaluation(cutoff), start, end)
    return {"cutoff_local": cutoff, "overall": metrics.summarize(df),
            "by_hour": metrics.by_hour(df), "by_day": metrics.by_day(df)}


@app.get("/api/horizon-error")
def horizon_error(start: date = Start, end: date = End, bin_hours: int = Query(6, ge=1, le=48)):
    """Error vs forecast horizon, using every published forecast (all vintages)."""
    a, f, _ = load_data()
    df = pd.merge(f, a, on="start_time", how="inner")
    return metrics.by_horizon(_slice(df, start, end), bin_hours)
