import numpy as np

from pairs_research import (
    block_bootstrap_mean_ci,
    generate_cointegrated_prices,
    performance,
    walk_forward_backtest,
)


def test_generator_and_backtest_are_reproducible() -> None:
    x1, y1 = generate_cointegrated_prices(500, seed=11)
    x2, y2 = generate_cointegrated_prices(500, seed=11)
    assert np.array_equal(x1, x2)
    assert np.array_equal(y1, y2)
    first = walk_forward_backtest(x1, y1)
    second = walk_forward_backtest(x2, y2)
    assert np.array_equal(first.pnl, second.pnl)


def test_future_data_cannot_change_earlier_results() -> None:
    x, y = generate_cointegrated_prices(500, seed=19)
    altered_y = y.copy()
    altered_y[350:] *= np.linspace(1.0, 1.7, altered_y.size - 350)
    original = walk_forward_backtest(x, y)
    altered = walk_forward_backtest(x, altered_y)
    # Row r earns the return from t to t+1, where t = lookback + r.
    unaffected_rows = 350 - original.start_index - 1
    assert np.array_equal(original.pnl[:unaffected_rows], altered.pnl[:unaffected_rows])


def test_transaction_costs_are_charged_from_identical_gross_returns() -> None:
    x, y = generate_cointegrated_prices(600, seed=5)
    gross = walk_forward_backtest(x, y, cost_bps=0.0)
    net = walk_forward_backtest(x, y, cost_bps=2.5)
    expected_cost = net.turnover * 2.5e-4
    assert np.allclose(gross.pnl - net.pnl, expected_cost)
    assert net.pnl.sum() <= gross.pnl.sum()


def test_weights_are_gross_normalised() -> None:
    x, y = generate_cointegrated_prices(400)
    result = walk_forward_backtest(x, y)
    gross_exposure = np.abs(result.positions).sum(axis=1)
    assert np.all((np.isclose(gross_exposure, 0.0)) | (np.isclose(gross_exposure, 1.0)))


def test_performance_and_bootstrap_outputs_are_well_formed() -> None:
    x, y = generate_cointegrated_prices(500, seed=2)
    result = walk_forward_backtest(x, y)
    stats = performance(result)
    low, high = block_bootstrap_mean_ci(result.pnl, samples=300, seed=3)
    assert np.isfinite([stats.total_return, stats.annualised_sharpe, stats.maximum_drawdown]).all()
    assert stats.maximum_drawdown <= 0.0
    assert low <= high
