"""Accuracy metrics. error = forecast - actual (positive = over-forecast)."""
import numpy as np
import pandas as pd

from . import config


def _r(x, nd=1):
    return None if x is None or pd.isna(x) else round(float(x), nd)


def summarize(df: pd.DataFrame) -> dict:
    d = df.dropna(subset=["actual_mw", "forecast_mw"])
    if d.empty:
        return {"n": 0}
    e = d["forecast_mw"] - d["actual_mw"]
    ae = e.abs()
    mean_actual = d["actual_mw"].mean()
    return {
        "n": int(len(d)),
        "mean_actual_mw": _r(mean_actual),
        "mae_mw": _r(ae.mean()),
        "rmse_mw": _r(np.sqrt((e ** 2).mean())),
        "bias_mw": _r(e.mean()),
        "nmae_pct": _r(ae.mean() / mean_actual * 100, 2) if mean_actual else None,
        "abs_error_p50_mw": _r(ae.quantile(0.5)),
        "abs_error_p90_mw": _r(ae.quantile(0.9)),
        "abs_error_p95_mw": _r(ae.quantile(0.95)),
        "abs_error_max_mw": _r(ae.max()),
        "over_forecast_p95_mw": _r(max(0, e.quantile(0.95))),
        "under_forecast_p95_mw": _r(max(0, -e.quantile(0.05))),
    }


def by_hour(df: pd.DataFrame) -> list[dict]:
    d = df.dropna(subset=["actual_mw", "forecast_mw"]).copy()
    d["hour"] = d["start_time"].dt.tz_convert(config.TZ).dt.hour
    return [{"hour": int(h), **summarize(g)} for h, g in d.groupby("hour")]


def by_day(df: pd.DataFrame) -> list[dict]:
    d = df.dropna(subset=["actual_mw", "forecast_mw"]).copy()
    d["day"] = d["start_time"].dt.tz_convert(config.TZ).dt.date.astype(str)
    return [{"day": k, **summarize(g)} for k, g in d.groupby("day")]


def by_horizon(df: pd.DataFrame, bin_hours: int = 6) -> list[dict]:
    """df must have start_time, publish_time, actual_mw, forecast_mw (all vintages)."""
    d = df.dropna(subset=["actual_mw", "forecast_mw"]).copy()
    d["horizon_h"] = (d["start_time"] - d["publish_time"]).dt.total_seconds() / 3600
    d = d[d["horizon_h"] >= 0]
    d["bin"] = (d["horizon_h"] // bin_hours * bin_hours).astype(int)
    return [{"horizon_from_h": int(b), "horizon_to_h": int(b + bin_hours), **summarize(g)}
            for b, g in d.groupby("bin")]
