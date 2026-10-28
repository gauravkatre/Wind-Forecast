"""Generate SYNTHETIC data (NOT real Elexon data) so the app runs without network access."""
import numpy as np
import pandas as pd
from pathlib import Path

out = Path(__file__).resolve().parents[1] / "data" / "sample"
out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(42)

idx = pd.date_range("2025-12-20", "2026-02-03", freq="30min", tz="UTC")
x = np.zeros(len(idx))
for i in range(1, len(idx)):
    x[i] = 0.995 * x[i - 1] + rng.normal(0, 0.08)
x = (x - x.min()) / (x.max() - x.min())
series = pd.Series(500 + x * 12000, index=idx)

start, end = pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-31 23:30", tz="UTC")
actual = series[start:end]
pd.DataFrame({"start_time": actual.index, "actual_mw": actual.values.round(0)}).to_csv(out / "actuals.csv", index=False)

pubs = pd.date_range("2025-12-25", "2026-01-31 23:00", freq="1h", tz="UTC")
parts = []
for h in range(1, 49):
    tgt = pubs + pd.Timedelta(hours=h)
    keep = (tgt >= start) & (tgt <= end)
    base = series.reindex(tgt[keep]).values
    f = np.clip(base * 1.02 + rng.normal(0, 150 + 90 * h, keep.sum()), 0, None)
    parts.append(pd.DataFrame({"start_time": tgt[keep], "publish_time": pubs[keep], "forecast_mw": f.round(0)}))
pd.concat(parts).sort_values(["start_time", "publish_time"]).to_csv(out / "forecasts.csv", index=False)
print("sample data written to", out)
