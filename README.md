# Quantitative Finance Projects

Reproducible Python projects covering market microstructure, statistical
research, derivatives, fixed-income risk, software systems and corporate valuation. Each project starts from the
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

All **45 tests** should pass (including parametrized cases). The code is educational and is not investment advice.

## New systems and valuation projects

| Project | Evidence | Run / documentation |
|---|---|---|
| Limit Order Book | Price-time matching, IOC, partial fills, cancellations; 2,000-event reference-model comparison | [Engineering README](engineering/README.md) |
| Auditable Price Pipeline | SQLite transactions, SHA-256 idempotency, row quarantine, failure rollback | [Engineering README](engineering/README.md#2-price-data-ingestion) |
| Corporate Valuation | Five-year DCF, 25 sensitivities, peer multiples and acquisition EPS | [Valuation README](corporate_finance/README.md) |

### Reproduce and stress the market-making result

```bash
python research_report.py > research_results.json
```

The 2,000-trial base comparison reduces mean simulated P&L from **17.95 to
13.85** while reducing its standard deviation from **30.14 to 4.13**. Lower
risk is accompanied by lower expected profit in this experiment. The report
also checks four regimes (500 paired paths each), varying volatility, informed
flow and jump frequency. Each comparison shares random paths across strategies
and reports a paired confidence interval for the mean P&L difference.

See [stored results](research_results.json) for complete parameters and outputs.
A narrow confidence interval reflects sampling uncertainty within this model,
not confidence that its assumptions describe live markets. No fees, latency,
queue dynamics or calibration to observed order flow are included in this
market-making simulator; the order book is a separate systems project.

### Development and reproducibility

New engineering, valuation and stress-report additions were implemented with
Codex assistance. Sample financial inputs and event streams are explicitly
synthetic. See module READMEs for algorithms, constraints and limitations.
Run `python -m pytest -q` from the repository root; examples require no API keys.
