import numpy as np

from derivatives_pricing import black_scholes_price, monte_carlo_price


def test_monte_carlo_confidence_interval_contains_benchmark() -> None:
    benchmark = black_scholes_price(100.0, 100.0, 0.04, 0.20, 1.0)
    estimate = monte_carlo_price(100.0, 100.0, 0.04, 0.20, 1.0, paths=200_000, seed=4)
    assert estimate.confidence_interval_95[0] <= benchmark <= estimate.confidence_interval_95[1]


def test_put_call_parity() -> None:
    call = black_scholes_price(100.0, 105.0, 0.03, 0.25, 2.0, "call")
    put = black_scholes_price(100.0, 105.0, 0.03, 0.25, 2.0, "put")
    assert np.isclose(call - put, 100.0 - 105.0 * np.exp(-0.03 * 2.0))


def test_antithetic_estimate_is_reproducible() -> None:
    first = monte_carlo_price(100.0, 100.0, 0.04, 0.20, 1.0, paths=5_000, seed=9)
    second = monte_carlo_price(100.0, 100.0, 0.04, 0.20, 1.0, paths=5_000, seed=9)
    assert first == second
