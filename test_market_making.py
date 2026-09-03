import numpy as np

from market_making import Strategy, paired_experiment, simulate_path


def test_position_limit_is_respected() -> None:
    strategy = Strategy("limited", position_limit=3)
    n = 50
    result = simulate_path(strategy, np.zeros(n), np.full(n, -1.0), np.zeros(n))
    assert result.max_abs_inventory == 3


def test_common_random_number_experiment_is_reproducible() -> None:
    first = paired_experiment(trials=30, steps=50, seed=11)
    second = paired_experiment(trials=30, steps=50, seed=11)
    assert first == second


def test_risk_controls_reduce_inventory_and_volatility() -> None:
    baseline, risk_aware = paired_experiment(trials=500, steps=250, seed=5)
    assert risk_aware.mean_max_inventory < baseline.mean_max_inventory
    assert risk_aware.pnl_volatility < baseline.pnl_volatility
