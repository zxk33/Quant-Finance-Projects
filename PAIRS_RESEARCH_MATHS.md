# Walk-Forward Pairs Research

## Research question

Can a temporary dislocation in a stable relative-price relationship be measured
and tested without using future information? This project is a research harness,
not a claim that a strategy will remain profitable on live markets.

## Model

For positive prices `X_t` and `Y_t`, each training window estimates

`log(Y_t) = alpha + beta log(X_t) + epsilon_t`

by ordinary least squares. The current residual is standardised using residuals
from the trailing training window. A position enters when the absolute z-score
crosses the entry threshold and exits inside a smaller band, which introduces
hysteresis and avoids unnecessary switching near one threshold.

## Walk-forward protocol

At decision time `t`:

1. Estimate `alpha`, `beta`, residual mean and residual volatility from
   `[t-lookback, t)` only.
2. Observe prices at `t` and form the z-score.
3. Set gross-normalised spread weights.
4. Apply those weights to returns from `t` to `t+1`.
5. Deduct turnover times the assumed one-way transaction cost.

The test suite changes all observations after a cutoff and verifies that every
earlier result remains bit-for-bit unchanged.

## Cost and risk accounting

For portfolio weights `w_t`, turnover is

`sum(abs(w_t - w_(t-1)))`.

Net period P&L is the weighted next-period return less turnover multiplied by
the cost rate. The report includes total compounded return, annualised Sharpe,
maximum drawdown and average turnover.

## Uncertainty

Daily strategy returns are not generally independent. The moving-block
bootstrap resamples contiguous circular blocks and reports a percentile
confidence interval for mean P&L, retaining short-range dependence more
faithfully than an IID resample.

## Synthetic validation and limitations

The demo generator creates a common log-price random walk and a stationary AR(1)
spread with a known hedge ratio. It is useful for testing recovery, leakage and
cost logic. It does not capture structural breaks, borrow constraints, execution
latency, market impact or the multiple-testing problem present in real research.
