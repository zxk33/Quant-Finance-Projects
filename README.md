# Quantitative Finance Projects

A collection of reproducible Python projects in quantitative investing, market
microstructure, derivatives, fixed-income risk and valuation.

The focus is simple: explain the mathematics, make assumptions explicit, keep
the code readable, and separate synthetic experiments from claims about real
markets.

**Start here:** [Project Index](PROJECT_INDEX.md)

| Project | Core idea | Mathematics | Code |
|---|---|---|---|
| Cross-Sectional Equity Signals | Rank equities using valuation, momentum and quality features | [Maths](EQUITY_SIGNAL_MATHS.md) · [Methodology](EQUITY_SIGNAL_RESEARCH.md) | [Python](equity_signal_research.py) · [Tests](test_equity_signal_research.py) |
| Walk-Forward Pairs Research | Test relative-value signals without look-ahead bias | [Maths](PAIRS_RESEARCH_MATHS.md) | [Python](pairs_research.py) · [Tests](test_pairs_research.py) |
| Market Making Under Uncertainty | Compare symmetric and inventory-aware quoting | [Maths](MARKET_MAKING_MATHS.md) | [Python](market_making.py) · [Tests](test_market_making.py) |
| Monte Carlo Derivatives Pricing | Price European options under risk-neutral GBM | [Maths](DERIVATIVES_PRICING_MATHS.md) | [Python](derivatives_pricing.py) · [Tests](test_derivatives_pricing.py) |
| Bond Yield-Curve & Risk Engine | Bootstrap curves and measure rate sensitivity | [Maths](BOND_RISK_ENGINE_MATHS.md) | [Python](bond_risk_engine.py) · [Tests](test_bond_risk_engine.py) |
| Corporate Valuation | DCF, comparables and acquisition EPS | [Maths](corporate_finance/MATHS.md) · [Notes](corporate_finance/README.md) | [Python](corporate_finance/valuation.py) · [Tests](corporate_finance/test_valuation.py) |
| Inventory-Policy Research | Compare simulated quoting policies with held-out evaluation | [Maths](quant_research/MATHS.md) · [Study](quant_research/README.md) | [Python](quant_research/inventory_study.py) · [Tests](quant_research/test_inventory_study.py) |
| Limit Order Book & Data Pipeline | Matching logic and reproducible market-data ingestion | [Mathematical notes](engineering/MATHS.md) · [Engineering notes](engineering/README.md) | [Engineering modules](engineering/) |

## Research principles

- Use only information available at the decision time.
- Include transaction costs where they materially affect the result.
- Prefer walk-forward or held-out evaluation over in-sample headline metrics.
- Show the mathematical model alongside the implementation.
- Label synthetic-model results clearly.
- Keep limitations and tests visible.

## Reproducibility

```bash
python -m pip install -r requirements.txt
pytest -q
```

The projects are educational research, not investment advice and not claims of
live trading performance.
