import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
SAMPLE_DIR = DATA_DIR / "sample"
TZ = "Europe/London"
# Day-ahead decision cutoff, UK local time on D-1. ASSUMPTION: configurable.
CUTOFF_LOCAL = os.getenv("DECISION_CUTOFF", "09:00")
RANGE_START = "2026-01-01"
RANGE_END = "2026-01-31"
