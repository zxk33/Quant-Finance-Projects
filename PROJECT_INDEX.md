# Project Index

A compact map of the repository. Each project links the implementation to its
mathematics, methodology and tests.

| Project | What it studies | Mathematics / methodology | Main code |
|---|---|---|---|
| Cross-Sectional Equity Signals | Ranking equities using valuation, momentum and quality features | [Maths](EQUITY_SIGNAL_MATHS.md) · [Methodology](EQUITY_SIGNAL_RESEARCH.md) | [Code](equity_signal_research.py) · [Tests](test_equity_signal_research.py) |
| Walk-Forward Pairs Research | Relative-value signals without look-ahead bias | [Maths](PAIRS_RESEARCH_MATHS.md) | [Code](pairs_research.py) · [Tests](test_pairs_research.py) |
| Market Making Under Uncertainty | Inventory risk and quoting behaviour | [Maths](MARKET_MAKING_MATHS.md) | [Code](market_making.py) · [Tests](test_market_making.py) |
| Monte Carlo Derivatives Pricing | European option valuation under risk-neutral GBM | [Maths](DERIVATIVES_PRICING_MATHS.md) | [Code](derivatives_pricing.py) · [Tests](test_derivatives_pricing.py) |
| Bond Yield-Curve & Risk Engine | Curve bootstrapping, duration, convexity and shocks | [Maths](BOND_RISK_ENGINE_MATHS.md) | [Code](bond_risk_engine.py) · [Tests](test_bond_risk_engine.py) |
| Corporate Valuation | DCF, trading comparables and acquisition EPS | [Maths](corporate_finance/MATHS.md) · [Notes](corporate_finance/README.md) | [Code](corporate_finance/valuation.py) · [Tests](corporate_finance/test_valuation.py) |
| Inventory-Policy Research | Held-out comparison of simulated quoting policies | [Maths](quant_research/MATHS.md) · [Study](quant_research/README.md) | [Code](quant_research/inventory_study.py) · [Tests](quant_research/test_inventory_study.py) |
| Limit Order Book & Data Pipeline | Matching logic and auditable market-data ingestion | [Mathematical notes](engineering/MATHS.md) · [Engineering notes](engineering/README.md) | Engineering modules in [engineering/](engineering/) |

## Principles

- State the mathematical model before reporting results.
- Separate synthetic experiments from claims about real markets.
- Use walk-forward or held-out evaluation where appropriate.
- Include transaction costs when they materially affect the experiment.
- Keep assumptions, limitations and tests visible.
