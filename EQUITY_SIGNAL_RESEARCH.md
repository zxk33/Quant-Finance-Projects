# Cross-sectional equity signal research

A small research framework for testing investment signals on an archived panel
of equities. It is deliberately data-source agnostic: the input can be an
export from Bloomberg/FactSet, a public-data API, or a saved CSV.

## Research question

Do simple, pre-specified company characteristics contain cross-sectional
information about *next-period* returns after turnover costs?

The framework is intended for experiments such as combining:
- valuation (for example earnings or free-cash-flow yield);
- medium-term momentum;
- quality/profitability;
- balance-sheet or volatility measures.

It does **not** ship with a claimed live-market alpha result. Results depend on
the chosen universe, dates, data vendor, survivorship treatment, feature
definitions and transaction-cost assumptions.

## Required data

CSV columns:

```
date,asset,forward_return,<signal_1>,<signal_2>,...
```

Each row represents information known at `date`; `forward_return` is the
subsequent holding-period return used only for evaluation.

## Method

1. Standardise each signal within the cross-section on each date.
2. Flip signs where an economically lower value is preferred.
3. Average the standardised signals into a transparent composite score.
4. Long the highest-scoring quantile and short the lowest-scoring quantile with
   equal gross exposure on each side.
5. Charge transaction costs from absolute portfolio-weight turnover.
6. Report total return, annualised Sharpe, maximum drawdown and turnover.

This is deliberately simpler than a production factor model. The point is to
make the signal construction, timing convention and cost treatment auditable.

## Leakage controls

Signals and weights for a date are computed only from that date's feature
cross-section. The subsequent `forward_return` is used only after weights are
fixed. For accounting data, the input dataset must lag fundamentals until their
actual publication date; otherwise the backtest is invalid.

## Example

```python
from equity_signal_research import load_panel, walk_forward_long_short, performance

panel = load_panel("data/equity_panel.csv")
result = walk_forward_long_short(
    panel,
    signals=["earnings_yield", "momentum_12_1", "roe"],
    directions=[1, 1, 1],
    quantile=0.2,
    cost_bps=5,
)
print(performance(result))
```

## Interpretation

A positive historical backtest is not evidence of persistent alpha by itself.
A credible study should test subperiods, alternate universes, cost assumptions,
feature lags and parameter stability, and should keep a genuinely held-out
period for final evaluation.
