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


def test_antithetic_standard_error_uses_independent_pair_means() -> None:
    paths = 2_000
    spot, strike, rate, volatility, maturity = 100.0, 100.0, 0.04, 0.20, 1.0
    estimate = monte_carlo_price(spot, strike, rate, volatility, maturity, paths=paths, seed=13)
    rng = np.random.default_rng(13)
    z = rng.standard_normal(paths // 2)
    drift = (rate - 0.5 * volatility**2) * maturity
    scale = volatility * np.sqrt(maturity)
    plus = np.exp(-rate * maturity) * np.maximum(spot * np.exp(drift + scale * z) - strike, 0.0)
    minus = np.exp(-rate * maturity) * np.maximum(spot * np.exp(drift - scale * z) - strike, 0.0)
    pairs = 0.5 * (plus + minus)
    expected = pairs.std(ddof=1) / np.sqrt(pairs.size)
    assert np.isclose(estimate.standard_error, expected)


def test_antithetic_sampling_requires_even_paths() -> None:
    try:
        monte_carlo_price(100.0, 100.0, 0.04, 0.20, 1.0, paths=999)
    except ValueError:
        return
    raise AssertionError("odd antithetic path count should be rejected")
