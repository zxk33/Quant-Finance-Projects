from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class Bond:
    face: float
    coupon_rate: float
    maturity: float
    frequency: int = 2

    def __post_init__(self) -> None:
        if self.face <= 0 or self.maturity <= 0:
            raise ValueError("face and maturity must be positive")
        if self.coupon_rate < 0 or self.frequency <= 0:
            raise ValueError("coupon_rate must be non-negative and frequency positive")
        periods = self.maturity * self.frequency
        if not np.isclose(periods, round(periods)):
            raise ValueError("maturity must contain a whole number of coupon periods")

    def cashflows(self) -> tuple[np.ndarray, np.ndarray]:
        periods = int(round(self.maturity * self.frequency))
        times = np.arange(1, periods + 1, dtype=float) / self.frequency
        cash = np.full(periods, self.face * self.coupon_rate / self.frequency)
        cash[-1] += self.face
        return times, cash


@dataclass(frozen=True)
class ZeroCurve:
    maturities: np.ndarray
    zero_rates: np.ndarray

    def __post_init__(self) -> None:
        t = np.asarray(self.maturities, dtype=float)
        r = np.asarray(self.zero_rates, dtype=float)
        if t.ndim != 1 or r.ndim != 1 or len(t) != len(r) or len(t) < 2:
            raise ValueError("maturities and zero_rates must be equal-length 1D arrays")
        if np.any(t <= 0) or np.any(np.diff(t) <= 0):
            raise ValueError("maturities must be positive and strictly increasing")
        object.__setattr__(self, "maturities", t)
        object.__setattr__(self, "zero_rates", r)

    def rates(self, times: np.ndarray) -> np.ndarray:
        return np.interp(times, self.maturities, self.zero_rates)

    def discount_factors(self, times: np.ndarray) -> np.ndarray:
        return np.exp(-self.rates(times) * times)

    def price(self, bond: Bond) -> float:
        times, cash = bond.cashflows()
        return float(np.dot(cash, self.discount_factors(times)))

    def shocked(self, shifts_bps: np.ndarray) -> "ZeroCurve":
        shifts = np.asarray(shifts_bps, dtype=float)
        if shifts.shape != self.zero_rates.shape:
            raise ValueError("one shift is required for each curve maturity")
        return ZeroCurve(self.maturities.copy(), self.zero_rates + shifts / 10_000.0)


def bootstrap_zero_curve(par_yields: np.ndarray) -> ZeroCurve:
    """Bootstrap annual discount factors from annual par yields."""
    par = np.asarray(par_yields, dtype=float)
    if par.ndim != 1 or len(par) < 2 or np.any(par <= -1):
        raise ValueError("par_yields must be a 1D array with at least two valid rates")
    discount_factors: list[float] = []
    for maturity, coupon in enumerate(par, start=1):
        earlier_coupons = coupon * sum(discount_factors)
        final_discount = (1.0 - earlier_coupons) / (1.0 + coupon)
        if final_discount <= 0:
            raise ValueError("par yields imply a non-positive discount factor")
        discount_factors.append(final_discount)
    maturities = np.arange(1, len(par) + 1, dtype=float)
    zeros = -np.log(np.asarray(discount_factors)) / maturities
    return ZeroCurve(maturities, zeros)


def _price_from_yield(bond: Bond, annual_yield: float) -> float:
    times, cash = bond.cashflows()
    base = 1.0 + annual_yield / bond.frequency
    if base <= 0:
        return float("inf")
    periods = times * bond.frequency
    return float(np.sum(cash / base**periods))


def yield_to_maturity(bond: Bond, market_price: float, tolerance: float = 1e-12) -> float:
    if market_price <= 0:
        raise ValueError("market_price must be positive")
    low, high = -0.99 * bond.frequency, 1.0
    while _price_from_yield(bond, high) > market_price:
        high *= 2.0
    for _ in range(200):
        mid = (low + high) / 2.0
        if _price_from_yield(bond, mid) > market_price:
            low = mid
        else:
            high = mid
        if high - low < tolerance:
            break
    return (low + high) / 2.0


def macaulay_duration(bond: Bond, annual_yield: float) -> float:
    times, cash = bond.cashflows()
    periods = times * bond.frequency
    pv = cash / (1.0 + annual_yield / bond.frequency) ** periods
    return float(np.dot(times, pv) / pv.sum())


def modified_duration(bond: Bond, annual_yield: float) -> float:
    return macaulay_duration(bond, annual_yield) / (1.0 + annual_yield / bond.frequency)


def convexity(bond: Bond, annual_yield: float) -> float:
    times, cash = bond.cashflows()
    n = times * bond.frequency
    base = 1.0 + annual_yield / bond.frequency
    price = _price_from_yield(bond, annual_yield)
    weighted = np.sum(cash * n * (n + 1.0) / base ** (n + 2.0))
    return float(weighted / (price * bond.frequency**2))


def scenario_analysis(bond: Bond, curve: ZeroCurve) -> Mapping[str, dict[str, float]]:
    anchor = np.linspace(-1.0, 1.0, len(curve.maturities))
    scenarios = {
        "Rates -100bp": np.full(len(anchor), -100.0),
        "Rates +100bp": np.full(len(anchor), 100.0),
        "Steepener": 50.0 * anchor,
        "Flattener": -50.0 * anchor,
    }
    base_price = curve.price(bond)
    return {
        name: {
            "price": shocked.price(bond),
            "pnl": shocked.price(bond) - base_price,
            "return_pct": 100.0 * (shocked.price(bond) / base_price - 1.0),
        }
        for name, shifts in scenarios.items()
        for shocked in [curve.shocked(shifts)]
    }
