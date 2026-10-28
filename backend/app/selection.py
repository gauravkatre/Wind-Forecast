"""Core logic: which forecast was the latest one available at decision time?

Day-ahead purchase for delivery day D is made on D-1 at `cutoff_local` (UK time).
For each target half-hour we take the forecast with the latest publishTime
<= that cutoff.
"""
import pandas as pd

from . import config


def cutoff_for(start_times: pd.Series, cutoff_local: str = config.CUTOFF_LOCAL) -> pd.Series:
    hh, mm = (int(x) for x in cutoff_local.split(":"))
    local = start_times.dt.tz_convert(config.TZ)
    naive = pd.to_datetime(local.dt.date) - pd.Timedelta(days=1) + pd.Timedelta(hours=hh, minutes=mm)
    cut = naive.dt.tz_localize(config.TZ, ambiguous="NaT", nonexistent="shift_forward")
    return cut.dt.tz_convert("UTC")


def select_latest_available(forecasts: pd.DataFrame, cutoff_local: str = config.CUTOFF_LOCAL) -> pd.DataFrame:
    f = forecasts.copy()
    f["cutoff"] = cutoff_for(f["start_time"], cutoff_local)
    f = f[f["publish_time"] <= f["cutoff"]]
    f = f.sort_values("publish_time").groupby("start_time", as_index=False).last()
    return f[["start_time", "publish_time", "cutoff", "forecast_mw"]]


def join_actuals(latest: pd.DataFrame, actuals: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(actuals, latest, on="start_time", how="outer").sort_values("start_time")
    df["error_mw"] = df["forecast_mw"] - df["actual_mw"]  # + = over-forecast
    return df.reset_index(drop=True)
