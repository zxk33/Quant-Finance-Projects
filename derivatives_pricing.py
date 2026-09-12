from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, sqrt

import numpy as np


@dataclass(frozen=True)
class Estimate:
    price: float
    standard_error: float
    confidence_interval_95: tuple[float, float]
    paths: int


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def black_scholes_price(
    spot: float,
    strike: float,
    rate: float,
    volatility: float,
    maturity: float,
    option_type: str = "call",
) -> float:
    if min(spot, strike, volatility, maturity) <= 0:
        raise ValueError("spot, strike, volatility and maturity must be positive")
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")
    d1 = (log(spot / strike) + (rate + 0.5 * volatility**2) * maturity) / (volatility * sqrt(maturity))
    d2 = d1 - volatility * sqrt(maturity)
    if option_type == "call":
        return spot * _normal_cdf(d1) - strike * exp(-rate * maturity) * _normal_cdf(d2)
    return strike * exp(-rate * maturity) * _normal_cdf(-d2) - spot * _normal_cdf(-d1)


def _discounted_payoff(
    z: np.ndarray,
    spot: float,
    strike: float,
    rate: float,
    volatility: float,
    maturity: float,
    option_type: str,
) -> np.ndarray:
    terminal = spot * np.exp(
        (rate - 0.5 * volatility**2) * maturity + volatility * sqrt(maturity) * z
    )
    payoff = (
        np.maximum(terminal - strike, 0.0)
        if option_type == "call"
        else np.maximum(strike - terminal, 0.0)
    )
    return exp(-rate * maturity) * payoff


def monte_carlo_price(
    spot: float,
    strike: float,
    rate: float,
    volatility: float,
    maturity: float,
    paths: int = 100_000,
    option_type: str = "call",
    seed: int = 0,
    antithetic: bool = True,
) -> Estimate:
    if paths < 2:
        raise ValueError("paths must be at least 2")
    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")
    if antithetic and paths % 2:
        raise ValueError("antithetic sampling requires an even path count")

    rng = np.random.default_rng(seed)
    if antithetic:
        z = rng.standard_normal(paths // 2)
        positive = _discounted_payoff(z, spot, strike, rate, volatility, maturity, option_type)
        negative = _discounted_payoff(-z, spot, strike, rate, volatility, maturity, option_type)
        # Pair means, rather than individual correlated payoffs, are the IID
        # sampling units used to estimate uncertainty.
        sampling_units = 0.5 * (positive + negative)
    else:
        z = rng.standard_normal(paths)
        sampling_units = _discounted_payoff(
            z, spot, strike, rate, volatility, maturity, option_type
        )

    price = float(sampling_units.mean())
    standard_error = float(sampling_units.std(ddof=1) / sqrt(sampling_units.size))
    margin = 1.96 * standard_error
    return Estimate(price, standard_error, (price - margin, price + margin), paths)


def convergence_table(path_counts: tuple[int, ...] = (1_000, 5_000, 25_000, 100_000)) -> list[Estimate]:
    return [monte_carlo_price(100.0, 100.0, 0.04, 0.20, 1.0, paths=n, seed=42) for n in path_counts]
