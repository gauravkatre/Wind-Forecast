"""Loads cached CSVs. Uses real data if present, otherwise the synthetic sample."""
from functools import lru_cache

import pandas as pd

from . import config


@lru_cache(maxsize=1)
def load_data():
    real = (config.DATA_DIR / "actuals.csv").exists() and (config.DATA_DIR / "forecasts.csv").exists()
    folder = config.DATA_DIR if real else config.SAMPLE_DIR
    actuals = pd.read_csv(folder / "actuals.csv", parse_dates=["start_time"])
    forecasts = pd.read_csv(folder / "forecasts.csv", parse_dates=["start_time", "publish_time"])
    for df in (actuals, forecasts):
        df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    forecasts["publish_time"] = pd.to_datetime(forecasts["publish_time"], utc=True)
    return actuals, forecasts, (not real)
