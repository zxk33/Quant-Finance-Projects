# Quantitative Finance Projects

Reproducible Python research covering cross-sectional equity signals, relative
value, market microstructure, derivatives, fixed-income risk and corporate
valuation. The emphasis is on transparent assumptions, walk-forward evaluation,
transaction costs and reproducible tests rather than headline backtest results.

| Project | Investment / research question | Methods | Code and notes |
|---|---|---|---|
| Cross-sectional Equity Signals | Can valuation, momentum or quality characteristics help rank next-period returns after costs? | Cross-sectional z-scores, market-neutral long/short portfolios, turnover costs | [`equity_signal_research.py`](equity_signal_research.py) · [methodology](EQUITY_SIGNAL_RESEARCH.md) |
| Walk-Forward Pairs Research | Can a relative-value signal be tested without leakage and after trading costs? | Rolling OLS, z-scores, cost-aware P&L, drawdown, block bootstrap | [`pairs_research.py`](pairs_research.py) · [methodology](PAIRS_RESEARCH_MATHS.md) |
| Corporate Valuation | How do operating assumptions flow through DCF, peer valuation and acquisition EPS? | Five-year DCF, WACC/g sensitivity, trading comparables, accretion/dilution | [valuation module](corporate_finance/README.md) |
| Market Making Under Uncertainty | How do inventory-aware quotes change dealer risk? | Stochastic price dynamics, inventory skew, paired Monte Carlo, confidence intervals | [`market_making.py`](market_making.py) · [derivation](MARKET_MAKING_MATHS.md) |
| Bond Yield-Curve and Risk Engine | How does a bond respond to yield-curve shocks? | Curve bootstrapping, YTM, duration, convexity, scenario analysis | [`bond_risk_engine.py`](bond_risk_engine.py) · [derivation](BOND_RISK_ENGINE_MATHS.md) |
| Monte Carlo Derivatives Pricing | How accurately can simulation recover a European option value? | Risk-neutral GBM, antithetic estimators, sampling error, Black-Scholes | [`derivatives_pricing.py`](derivatives_pricing.py) · [derivation](DERIVATIVES_PRICING_MATHS.md) |

## Research controls

The equity-signal framework is data-source agnostic and is designed for archived
real-market panels. Signals are standardised within each date, weights are fixed
before the subsequent return is evaluated, and turnover costs are charged
explicitly. Fundamental data must be lagged to its actual publication date.

The pairs engine estimates each signal from a trailing window ending strictly
before the decision time, applies it only to the next return, charges costs on
portfolio turnover and uses a moving-block bootstrap for uncertainty. A test
mutates future observations after a cutoff and verifies that earlier results do
not change.

The market-making comparison uses paired synthetic trials and identical random
paths across strategies. Reported results are model outputs, not claims about
live trading performance.

## Run locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

## Additional engineering work

- Limit-order-book engine with price-time matching, IOC handling, partial fills
  and cancellations.
- Auditable price-data pipeline with SQLite transactions, idempotency,
  quarantining and rollback.
- Inventory-policy research using independent train/validation/test simulations,
  matched controls and stress cases.

See [Engineering](engineering/README.md) and
[Inventory Research](quant_research/README.md) for details.

## Reproducibility and limitations

The repository contains explicit model assumptions, methodology notes and tests.
Synthetic examples are labelled as such. Real-market research still depends on
the quality of the supplied dataset, survivorship handling, publication lags,
transaction costs and the choice of universe.

Selected modules were developed with coding assistance; the repository keeps the
source, assumptions and tests visible so the work can be audited and explained.
