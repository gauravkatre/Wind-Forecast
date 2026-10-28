import pandas as pd
from app import selection


def _f(rows):
    return pd.DataFrame(rows, columns=["start_time", "publish_time", "forecast_mw"]).astype(
        {"start_time": "datetime64[ns, UTC]", "publish_time": "datetime64[ns, UTC]"})


def T(s):
    return pd.Timestamp(s, tz="UTC")


def test_cutoff_is_previous_day_0900_london():
    s = pd.Series([T("2026-01-10 12:00")])
    assert selection.cutoff_for(s, "09:00").iloc[0] == T("2026-01-09 09:00")


def test_picks_latest_publish_at_or_before_cutoff():
    tgt = T("2026-01-10 12:00")
    f = _f([[tgt, T("2026-01-09 08:00"), 100.0],
            [tgt, T("2026-01-09 09:00"), 200.0],   # exactly at cutoff -> allowed
            [tgt, T("2026-01-09 10:00"), 300.0]])  # after cutoff -> must be ignored
    r = selection.select_latest_available(f, "09:00")
    assert len(r) == 1 and r.iloc[0]["forecast_mw"] == 200.0


def test_no_forecast_before_cutoff_gives_no_row():
    tgt = T("2026-01-10 12:00")
    f = _f([[tgt, T("2026-01-09 09:30"), 1.0]])
    assert selection.select_latest_available(f, "09:00").empty


def test_join_error_sign_over_forecast_positive():
    latest = pd.DataFrame({"start_time": [T("2026-01-10 12:00")], "publish_time": [T("2026-01-09 09:00")],
                           "cutoff": [T("2026-01-09 09:00")], "forecast_mw": [1200.0]})
    actuals = pd.DataFrame({"start_time": [T("2026-01-10 12:00")], "actual_mw": [1000.0]})
    assert selection.join_actuals(latest, actuals).iloc[0]["error_mw"] == 200.0
