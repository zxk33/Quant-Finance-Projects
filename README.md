# Quantitative Finance Projects

A collection of three tested Python models exploring problems across Global Markets and Investment Banking. The projects use synthetic inputs and focus on transparent assumptions, reproducible experiments and interpretable risk measures.

## Market Making Under Uncertainty

`market_making.py` implements an event-driven dealer model with adverse selection, stochastic price jumps and inventory-sensitive quotes. A paired Monte Carlo experiment compares symmetric quoting with a risk-aware strategy using identical random paths. Across 2,000 trials, the inventory-aware controls reduced P&L volatility by 86.3%, loss frequency from 19.6% to 0.2%, and average maximum inventory from 21.3 to 4.7 units.

## Monte Carlo Derivatives Pricing

`derivatives_pricing.py` prices European calls and puts under risk-neutral geometric Brownian motion. It includes antithetic variance reduction, standard errors, 95% confidence intervals, convergence analysis and a Black-Scholes benchmark.

## Bond Yield-Curve and Risk Engine

`bond_risk_engine.py` bootstraps zero rates from par yields and calculates bond prices, yield to maturity, Macaulay and modified duration, convexity, and P&L under parallel and curve-shape shocks.

## Run locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

All ten automated tests should pass. The code is educational and is not investment advice.
