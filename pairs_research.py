"""Walk-forward pairs research with explicit leakage and cost controls.

The module is intentionally data-source agnostic: pass two positive price arrays
from a CSV/API, or use ``generate_cointegrated_prices`` for a reproducible demo.
Signals at time t are estimated only from observations strictly before t and are
applied to returns from t to t+1.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass(frozen=True)
class BacktestResult:
    pnl: np.ndarray
    positions: np.ndarray
    hedge_ratios: np.ndarray
    z_scores: np.ndarray
    turnover: np.ndarray
    start_index: int


@dataclass(frozen=True)
class Performance:
    total_return: float
    annualised_sharpe: float
    maximum_drawdown: float
    average_turnover: float


def generate_cointegrated_prices(
    observations: int = 1_000,
    *,
    seed: int = 7,
    hedge_ratio: float = 1.15,
    spread_persistence: float = 0.85,
    common_volatility: float = 0.012,
    spread_volatility: float = 0.008,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate two positive prices with a stationary log-price spread."""
    if observations < 3:
        raise ValueError("observations must be at least 3")
    if not 0.0 <= spread_persistence < 1.0:
        raise ValueError("spread_persistence must be in [0, 1)")
    if min(common_volatility, spread_volatility) <= 0.0:
        raise ValueError("volatilities must be positive")

    rng = np.random.default_rng(seed)
    log_x = np.empty(observations)
    spread = np.empty(observations)
    log_x[0] = np.log(100.0)
    spread[0] = 0.0
    common_shocks = rng.normal(0.0, common_volatility, observations - 1)
    spread_shocks = rng.normal(0.0, spread_volatility, observations - 1)
    for t in range(1, observations):
        log_x[t] = log_x[t - 1] + common_shocks[t - 1]
        spread[t] = spread_persistence * spread[t - 1] + spread_shocks[t - 1]
    log_y = 0.25 + hedge_ratio * log_x + spread
    return np.exp(log_x), np.exp(log_y)


def _validate_prices(prices_x: np.ndarray, prices_y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(prices_x, dtype=float)
    y = np.asarray(prices_y, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size:
        raise ValueError("price inputs must be one-dimensional and equally sized")
    if x.size < 4 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("prices must contain at least four finite observations")
    if np.any(x <= 0.0) or np.any(y <= 0.0):
        raise ValueError("prices must be strictly positive")
    return x, y


def _ols(y: np.ndarray, x: np.ndarray) -> tuple[float, float]:
    x_mean = float(x.mean())
    y_mean = float(y.mean())
    denominator = float(np.sum((x - x_mean) ** 2))
    if denominator <= 1e-14:
        raise ValueError("training window has insufficient variation")
    beta = float(np.sum((x - x_mean) * (y - y_mean)) / denominator)
    return y_mean - beta * x_mean, beta


def walk_forward_backtest(
    prices_x: np.ndarray,
    prices_y: np.ndarray,
    *,
    lookback: int = 60,
    entry_z: float = 1.5,
    exit_z: float = 0.35,
    cost_bps: float = 1.0,
) -> BacktestResult:
    """Backtest a rolling log-spread strategy without look-ahead bias.

    At each t, OLS parameters and spread moments use [t-lookback, t), the
    current observation forms the signal, and the resulting weights earn the
    t-to-t+1 return. Costs are charged on absolute portfolio-weight changes.
    """
    x, y = _validate_prices(prices_x, prices_y)
    if not 10 <= lookback <= x.size - 2:
        raise ValueError("lookback must be between 10 and len(prices)-2")
    if not entry_z > exit_z >= 0.0:
        raise ValueError("require entry_z > exit_z >= 0")
    if cost_bps < 0.0:
        raise ValueError("cost_bps cannot be negative")

    log_x, log_y = np.log(x), np.log(y)
    periods = x.size - lookback - 1
    pnl = np.zeros(periods)
    positions = np.zeros((periods, 2))
    betas = np.zeros(periods)
    z_scores = np.zeros(periods)
    turnover = np.zeros(periods)
    previous_direction = 0.0
    previous_weights = np.zeros(2)

    for row, t in enumerate(range(lookback, x.size - 1)):
        train_x = log_x[t - lookback : t]
        train_y = log_y[t - lookback : t]
        intercept, beta = _ols(train_y, train_x)
        residuals = train_y - (intercept + beta * train_x)
        residual_std = float(residuals.std(ddof=1))
        z = 0.0 if residual_std <= 1e-14 else float(
            (log_y[t] - (intercept + beta * log_x[t]) - residuals.mean()) / residual_std
        )

        direction = previous_direction
        if direction == 0.0 and abs(z) >= entry_z:
            direction = -float(np.sign(z))
        elif direction != 0.0 and abs(z) <= exit_z:
            direction = 0.0

        gross = 1.0 + abs(beta)
        weights = np.array([-direction * beta / gross, direction / gross])
        traded = float(np.abs(weights - previous_weights).sum())
        next_returns = np.array([x[t + 1] / x[t] - 1.0, y[t + 1] / y[t] - 1.0])
        pnl[row] = float(weights @ next_returns) - traded * cost_bps * 1e-4
        positions[row] = weights
        betas[row] = beta
        z_scores[row] = z
        turnover[row] = traded
        previous_direction = direction
        previous_weights = weights

    return BacktestResult(pnl, positions, betas, z_scores, turnover, lookback)


def performance(result: BacktestResult, periods_per_year: int = 252) -> Performance:
    """Compute simple cost-adjusted return, Sharpe, drawdown and turnover."""
    pnl = np.asarray(result.pnl, dtype=float)
    mean = float(pnl.mean())
    volatility = float(pnl.std(ddof=1)) if pnl.size > 1 else 0.0
    sharpe = 0.0 if volatility <= 1e-14 else sqrt(periods_per_year) * mean / volatility
    equity = np.cumprod(1.0 + pnl)
    running_peak = np.maximum.accumulate(np.concatenate(([1.0], equity)))
    drawdowns = np.concatenate(([1.0], equity)) / running_peak - 1.0
    return Performance(
        total_return=float(equity[-1] - 1.0),
        annualised_sharpe=float(sharpe),
        maximum_drawdown=float(drawdowns.min()),
        average_turnover=float(result.turnover.mean()),
    )


def block_bootstrap_mean_ci(
    pnl: np.ndarray,
    *,
    block_size: int = 10,
    samples: int = 2_000,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile CI for mean P&L using a circular moving-block bootstrap."""
    values = np.asarray(pnl, dtype=float)
    if values.ndim != 1 or values.size < 2:
        raise ValueError("pnl must be a one-dimensional array with at least two values")
    if not 1 <= block_size <= values.size or samples < 100:
        raise ValueError("invalid block_size or samples")
    rng = np.random.default_rng(seed)
    blocks_needed = int(np.ceil(values.size / block_size))
    offsets = np.arange(block_size)
    means = np.empty(samples)
    for i in range(samples):
        starts = rng.integers(0, values.size, size=blocks_needed)
        indices = (starts[:, None] + offsets[None, :]) % values.size
        means[i] = values[indices.ravel()[: values.size]].mean()
    low, high = np.quantile(means, [0.025, 0.975])
    return float(low), float(high)


if __name__ == "__main__":
    px, py = generate_cointegrated_prices()
    result = walk_forward_backtest(px, py)
    stats = performance(result)
    ci = block_bootstrap_mean_ci(result.pnl)
    print(stats)
    print(f"95% block-bootstrap CI for mean daily P&L: {ci}")
