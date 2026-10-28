"""Fetch real Elexon data for Jan 2026 and cache as CSV in backend/data/.
Usage (from backend/):  python -m scripts.fetch_data
"""
import argparse
from datetime import date

from app import config, elexon

p = argparse.ArgumentParser()
p.add_argument("--start", default=config.RANGE_START)
p.add_argument("--end", default=config.RANGE_END)
p.add_argument("--publish-from", default="2025-12-25",
               help="earliest forecast publish date to pull (forecasts for early Jan are published earlier)")
a = p.parse_args()
start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)

actuals = elexon.fetch_actuals(start, end)
forecasts = elexon.fetch_forecasts(date.fromisoformat(a.publish_from), end)
forecasts = forecasts[(forecasts["start_time"] >= f"{start}T00:00:00Z") &
                      (forecasts["start_time"] < f"{end}T23:59:59Z")]
config.DATA_DIR.mkdir(parents=True, exist_ok=True)
actuals.to_csv(config.DATA_DIR / "actuals.csv", index=False)
forecasts.to_csv(config.DATA_DIR / "forecasts.csv", index=False)
print(f"actuals: {len(actuals)} rows | forecasts: {len(forecasts)} rows")
