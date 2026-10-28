import pandas as pd
from app import metrics


def test_summarize_known_values():
    df = pd.DataFrame({"actual_mw": [100.0, 100.0, 100.0, 100.0],
                       "forecast_mw": [110.0, 90.0, 120.0, 80.0]})  # errors +10 -10 +20 -20
    s = metrics.summarize(df)
    assert s["n"] == 4 and s["mae_mw"] == 15.0 and s["bias_mw"] == 0.0
    assert s["rmse_mw"] == round((250) ** 0.5, 1)
    assert s["nmae_pct"] == 15.0


def test_summarize_empty_and_nan_rows_ignored():
    assert metrics.summarize(pd.DataFrame({"actual_mw": [None], "forecast_mw": [1.0]})) == {"n": 0}
