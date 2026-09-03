# Quantitative Finance Projects

Three compact, tested Python models covering market microstructure, derivatives and fixed-income risk. Each project is built from the underlying mathematics, uses seeded synthetic data and includes explicit validation rather than presenting simulation output as fact.

| Project | Core question | Mathematics | Code and notes |
|---|---|---|---|
| Market Making Under Uncertainty | How do inventory-aware quotes change a dealer's risk? | Stochastic price dynamics, inventory skew, paired Monte Carlo, confidence intervals | [`market_making.py`](market_making.py) · [derivation](MARKET_MAKING_MATHS.md) |
| Monte Carlo Derivatives Pricing | How accurately can simulation recover a European option value? | Risk-neutral GBM, antithetic sampling, sampling error, Black-Scholes | [`derivatives_pricing.py`](derivatives_pricing.py) · [derivation](DERIVATIVES_PRICING_MATHS.md) |
| Bond Yield-Curve and Risk Engine | How does a bond respond to yield-curve shocks? | Curve bootstrapping, YTM, duration, convexity, scenario analysis | [`bond_risk_engine.py`](bond_risk_engine.py) · [derivation](BOND_RISK_ENGINE_MATHS.md) |

## Reproducible result

The market-making comparison uses 2,000 paired trials and identical random paths for both strategies. Against symmetric quoting, the inventory-aware strategy reduced P&L volatility by **86.3%**, loss frequency from **19.6% to 0.2%**, and average maximum inventory from **21.3 to 4.7 units**. These figures are outputs of the stated synthetic model, not claims about live trading performance.

## Run locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

All **10 tests** should pass. The code is educational and is not investment advice.
