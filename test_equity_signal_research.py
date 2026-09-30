import numpy as np
import pandas as pd

from equity_signal_research import composite_score, performance, walk_forward_long_short


def sample_panel():
    dates = pd.date_range("2024-01-01", periods=6, freq="D")
    rows = []
    for i, d in enumerate(dates):
        for j, asset in enumerate(["A", "B", "C", "D", "E"]):
            rows.append({
                "date": d,
                "asset": asset,
                "forward_return": 0.001 * (j - 2),
                "value": float(j),
                "momentum": float(j) + 0.1 * i,
            })
    return pd.DataFrame(rows)


def test_scores_are_cross_sectionally_centred():
    df = sample_panel()
    score = composite_score(df, ["value", "momentum"])
    means = score.groupby(df["date"]).mean()
    assert np.allclose(means.to_numpy(), 0.0)


def test_long_short_weights_are_market_neutral():
    result = walk_forward_long_short(sample_panel(), ["value"], quantile=0.2, cost_bps=0)
    sums = result.weights.groupby("date")["weight"].sum()
    assert np.allclose(sums.to_numpy(), 0.0)


def test_performance_is_finite():
    result = walk_forward_long_short(sample_panel(), ["value"], quantile=0.2, cost_bps=1)
    stats = performance(result)
    assert np.isfinite(stats.total_return)
    assert np.isfinite(stats.maximum_drawdown)
