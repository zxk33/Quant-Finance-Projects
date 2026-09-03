import numpy as np

from bond_risk_engine import (
    Bond,
    bootstrap_zero_curve,
    modified_duration,
    scenario_analysis,
    yield_to_maturity,
)


def test_par_bond_prices_near_par_on_flat_curve() -> None:
    curve = bootstrap_zero_curve(np.full(5, 0.04))
    bond = Bond(100.0, 0.04, 5.0, 1)
    assert np.isclose(curve.price(bond), 100.0, atol=1e-10)


def test_ytm_recovers_coupon_for_par_bond() -> None:
    bond = Bond(100.0, 0.05, 4.0, 2)
    assert np.isclose(yield_to_maturity(bond, 100.0), 0.05, atol=1e-10)


def test_duration_is_positive_and_below_maturity() -> None:
    bond = Bond(100.0, 0.045, 5.0, 2)
    duration = modified_duration(bond, 0.04)
    assert 0.0 < duration < bond.maturity


def test_rate_rise_reduces_price() -> None:
    curve = bootstrap_zero_curve(np.array([0.03, 0.032, 0.034, 0.036, 0.038]))
    bond = Bond(100.0, 0.04, 5.0, 2)
    results = scenario_analysis(bond, curve)
    assert results["Rates +100bp"]["pnl"] < 0
    assert results["Rates -100bp"]["pnl"] > 0
