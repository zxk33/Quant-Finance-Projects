# Quantitative Finance Projects

Four compact, tested Python models covering market microstructure, statistical
research, derivatives and fixed-income risk. Each project starts from the
underlying mathematics, uses reproducible experiments and distinguishes
synthetic-model output from evidence about live markets.

| Project | Core question | Mathematics | Code and notes |
|---|---|---|---|
| Market Making Under Uncertainty | How do inventory-aware quotes change a dealer's risk? | Stochastic price dynamics, inventory skew, paired Monte Carlo, confidence intervals | [`market_making.py`](market_making.py) · [derivation](MARKET_MAKING_MATHS.md) |
| Walk-Forward Pairs Research | Can a relative-value signal be tested without leakage and after trading costs? | Rolling OLS, z-scores, cost-aware P&L, drawdown, block bootstrap | [`pairs_research.py`](pairs_research.py) · [methodology](PAIRS_RESEARCH_MATHS.md) |
| Monte Carlo Derivatives Pricing | How accurately can simulation recover a European option value? | Risk-neutral GBM, antithetic pair estimators, sampling error, Black-Scholes | [`derivatives_pricing.py`](derivatives_pricing.py) · [derivation](DERIVATIVES_PRICING_MATHS.md) |
| Bond Yield-Curve and Risk Engine | How does a bond respond to yield-curve shocks? | Curve bootstrapping, YTM, duration, convexity, scenario analysis | [`bond_risk_engine.py`](bond_risk_engine.py) · [derivation](BOND_RISK_ENGINE_MATHS.md) |

## Research controls

The pairs engine estimates each signal from a trailing window ending strictly
before the decision time, applies it only to the next return, charges costs on
portfolio turnover and uses a moving-block bootstrap for uncertainty. A test
mutates every future observation after a cutoff and verifies that all earlier
results remain unchanged.

The market-making comparison uses 2,000 paired synthetic trials and identical
random paths for both strategies. Under the stated model, inventory-aware
quoting reduced P&L volatility by **86.3%**, loss frequency from **19.6% to
0.2%**, and average maximum inventory from **21.3 to 4.7 units**. These are
simulation outputs, not claims about live trading performance.

## Run locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

All **17 tests** should pass. The code is educational and is not investment advice.
