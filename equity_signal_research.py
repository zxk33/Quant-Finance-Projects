"""Walk-forward cross-sectional equity signal research.

Input is a CSV/DataFrame of real or simulated observations with:
date, asset, forward_return, and one or more numeric signal columns.

The engine ranks signals cross-sectionally using only information available at
each date, forms market-neutral long/short portfolios, applies turnover costs,
and reports out-of-sample performance. No market-data API is hard-coded so the
research can be reproduced from an archived dataset.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SignalResult:
    daily_returns: pd.Series
    turnover: pd.Series
    weights: pd.DataFrame


@dataclass(frozen=True)
class SignalPerformance:
    total_return: float
    annualised_sharpe: float
    maximum_drawdown: float
    average_turnover: float


def load_panel(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "asset", "forward_return"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if df.duplicated(["date", "asset"]).any():
        raise ValueError("date/asset rows must be unique")
    if not np.isfinite(df["forward_return"]).all():
        raise ValueError("forward_return must be finite")
    return df.sort_values(["date", "asset"]).reset_index(drop=True)


def _zscore_cross_section(values: pd.Series) -> pd.Series:
    x = values.astype(float)
    std = float(x.std(ddof=0))
    if not np.isfinite(std) or std <= 1e-12:
        return pd.Series(0.0, index=x.index)
    return (x - float(x.mean())) / std


def composite_score(
    df: pd.DataFrame,
    signals: Sequence[str],
    *,
    directions: Sequence[float] | None = None,
) -> pd.Series:
    if not signals:
        raise ValueError("at least one signal is required")
    if directions is None:
        directions = [1.0] * len(signals)
    if len(directions) != len(signals):
        raise ValueError("directions must match signals")
    missing = set(signals).difference(df.columns)
    if missing:
        raise ValueError(f"missing signal columns: {sorted(missing)}")

    pieces = []
    for name, direction in zip(signals, directions):
        numeric = pd.to_numeric(df[name], errors="coerce")
        if numeric.isna().any():
            raise ValueError(f"signal {name} contains missing/non-numeric values")
        pieces.append(
            numeric.groupby(df["date"], group_keys=False).transform(_zscore_cross_section)
            * float(direction)
        )
    return pd.concat(pieces, axis=1).mean(axis=1)


def walk_forward_long_short(
    df: pd.DataFrame,
    signals: Sequence[str],
    *,
    directions: Sequence[float] | None = None,
    quantile: float = 0.2,
    cost_bps: float = 5.0,
) -> SignalResult:
    if not 0.0 < quantile <= 0.5:
        raise ValueError("quantile must be in (0, 0.5]")
    if cost_bps < 0:
        raise ValueError("cost_bps cannot be negative")

    panel = df.copy()
    panel["score"] = composite_score(panel, signals, directions=directions)
    all_weights = []
    daily = []
    turnover = []
    prev: dict[str, float] = {}

    for date, g in panel.groupby("date", sort=True):
        n = len(g)
        k = max(1, int(np.floor(n * quantile)))
        ranked = g.sort_values("score")
        short_assets = ranked.head(k)["asset"].tolist()
        long_assets = ranked.tail(k)["asset"].tolist()

        weights = {a: 0.5 / k for a in long_assets}
        weights.update({a: -0.5 / k for a in short_assets})
        traded = sum(abs(weights.get(a, 0.0) - prev.get(a, 0.0))
                     for a in set(weights) | set(prev))
        gross_ret = sum(
            weights.get(row.asset, 0.0) * float(row.forward_return)
            for row in g.itertuples()
        )
        net_ret = gross_ret - traded * cost_bps * 1e-4
        daily.append((date, net_ret))
        turnover.append((date, traded))
        all_weights.extend((date, a, w) for a, w in weights.items())
        prev = weights

    daily_s = pd.Series(dict(daily), name="return").sort_index()
    turnover_s = pd.Series(dict(turnover), name="turnover").sort_index()
    weights_df = pd.DataFrame(all_weights, columns=["date", "asset", "weight"])
    return SignalResult(daily_s, turnover_s, weights_df)


def performance(result: SignalResult, periods_per_year: int = 252) -> SignalPerformance:
    r = result.daily_returns.astype(float)
    if r.empty:
        raise ValueError("result has no returns")
    vol = float(r.std(ddof=1)) if len(r) > 1 else 0.0
    sharpe = 0.0 if vol <= 1e-12 else sqrt(periods_per_year) * float(r.mean()) / vol
    equity = (1.0 + r).cumprod()
    drawdown = equity / equity.cummax() - 1.0
    return SignalPerformance(
        total_return=float(equity.iloc[-1] - 1.0),
        annualised_sharpe=sharpe,
        maximum_drawdown=float(drawdown.min()),
        average_turnover=float(result.turnover.mean()),
    )


if __name__ == "__main__":
    raise SystemExit(
        "Import this module and pass an archived equity panel; see "
        "EQUITY_SIGNAL_RESEARCH.md for the schema and research controls."
    )
