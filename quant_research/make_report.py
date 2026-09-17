"""Render the stored numerical output; never reruns or reselects policies."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root=Path(__file__).parent
r=json.loads((root/'results.json').read_text())
base=next(x for x in r['evaluation'] if x['regime']=='base' and x['fee_per_fill']==.005)
s,c=base['statistics']['selected'],base['statistics']['matched_control']
text='''# Inventory control: profit, risk and model uncertainty

**Research question:** does inventory-dependent quoting improve the profit/risk
trade-off after trading costs, and does that conclusion survive changes in the
simulated market?

This is a synthetic model study, not a backtest on observed market data.
Implemented and tested with Codex assistance. All results are reproducible.

## Reproduce

```bash
python -m quant_research.inventory_study
python -m quant_research.make_report
python -m pytest -q
```

The numerical study needs NumPy; rendering the chart also needs Matplotlib.
`results.json` records every parameter, sample size and candidate score.

## Protocol fixed before evaluation

- Candidate grid: 3 half-spreads x 3 inventory skews x 2 position limits = 18 policies.
- Training: 1,000 paths, seed 101. Rank by mean P&L minus 0.1 times P&L standard deviation.
- Validation: 1,000 independent paths, seed 202. Select one of the top three training policies.
- Evaluation: 2,000 new paths per regime, 500 steps per path, seeds 303–306.
- Freeze the policy before evaluating 4 regimes x 3 fees = 12 cases.
- Charge 0.005 currency units per execution during selection and 0.02 per unit
  to liquidate terminal inventory. Evaluation fees: 0, 0.005 and 0.02.
- Reuse random paths across policies within each comparison. Costs do not feed
  back into quotes. Report paired mean differences and approximate 95% CIs.

The comparison policy has the **same spread and position limit**, with skew
set to zero. The separate wide-limit reference changes several parameters and
cannot isolate inventory skew. The objective's 0.1 risk penalty is a modelling
choice, not a universal investor preference, and is not an annualised Sharpe ratio.

## Dealer and counterparty model

At step t, a dealer sees fair value S and inventory q, then quotes:

`reservation = S - skew * q`

`bid = reservation - half_spread; ask = reservation + half_spread`

The counterparty valuation is `S + informedness * next_move + noise`.
It buys above the ask or sells below the bid, subject to dealer inventory
limits. Only the counterparty sees a component of the next price move.
The dealer then marks its inventory at the new fair value. This deliberately
creates adverse selection: fills can precede unfavourable price changes.

Terminal P&L equals cash plus marked inventory, less liquidation cost.
Maximum drawdown measures the largest peak-to-trough decline in marked P&L,
including terminal liquidation. Expected shortfall is minus the average P&L
of the worst 5% of paths; it can be negative when that tail remains profitable.

## Held-out base case

'''
text+=f"Selected policy: half-spread **{r['selected']['spread']}**, skew **{r['selected']['skew']}**, limit **{r['selected']['limit']}**.\n\n"
text+='| Metric | Selected policy | Matched zero-skew control |\n|---|---:|---:|\n'
for label,key in [('Mean net P&L','mean_pnl'),('P&L standard deviation','pnl_std'),('Loss frequency','loss_frequency'),('95% expected shortfall','expected_shortfall_95'),('Mean maximum drawdown','mean_max_drawdown'),('Mean maximum inventory','mean_max_inventory')]:
 text+=f'| {label} | {s[key]:.4f} | {c[key]:.4f} |\n'
delta=base['selected_minus_control']
text+=f"\nThe selected policy reduced P&L standard deviation by **{100*(1-s['pnl_std']/c['pnl_std']):.1f}%** while reducing mean P&L by **{100*(1-s['mean_pnl']/c['mean_pnl']):.1f}%**. The paired mean difference is **{delta['mean']:.3f}**, with 95% CI **[{delta['ci95'][0]:.3f}, {delta['ci95'][1]:.3f}]**. This supports a risk reduction with a profit cost in this model, not profit dominance.\n\n"
text+='## Stress cases at the selection fee\n\n| Regime | Selected mean P&L | Control mean P&L | Selected SD | Control SD |\n|---|---:|---:|---:|---:|\n'
for x in r['evaluation']:
 if x['fee_per_fill']==.005:
  a,b=x['statistics']['selected'],x['statistics']['matched_control']
  text+=f"| {x['regime']} | {a['mean_pnl']:.3f} | {b['mean_pnl']:.3f} | {a['pnl_std']:.3f} | {b['pnl_std']:.3f} |\n"
text+='''
![Training profit-risk points and held-out fee sensitivity](study.svg)

Left: each candidate is evaluated on the same training paths. This plot is
selection evidence, not held-out performance. Right: the frozen selected policy
on independent test paths. Fee cases within a regime reuse paths, so they are
correlated comparisons, not additional independent observations.

## What could invalidate the result?

1. The arrival/value mechanism, noise distribution and regime changes are
   invented. Independent random seeds prevent sample reuse; they do not validate
   the market model or establish generalisation to real order flow.
2. The dealer observes fair value directly. Real fair value is latent.
3. Unit orders, one potential fill per step, no queue priority, latency, partial
   fills, market impact, exchange tick constraints or competition.
4. Fees are flat per unit and do not change quoting behaviour. No funding costs.
5. The test suite verifies selected accounting identities, risk limits and
   split separation. Passing tests does not establish economic realism.
6. CIs describe Monte Carlo sampling error conditional on a selected policy and
   fixed model. They omit selection uncertainty, model error and simultaneous
   multiple-comparison adjustments. Do not cherry-pick one of the 12 cases.
7. A final inventory haircut is a simple liquidation assumption. It is not an
   executable liquidation model. Price dynamics are additive rather than a
   calibrated positive-price process.

## Interview discussion: explain these without reading the code

- **Why does a long position lower both quotes?** The dealer becomes more eager
  to sell and less eager to buy; it shifts its reservation price downward.
- **Why paired randomness?** Var(A-B) = Var(A) + Var(B) - 2 Cov(A,B). Positive
  covariance from shared market shocks can reduce comparison noise.
- **Why three samples?** Training narrows the search; validation selects; the
  untouched test sample estimates performance after selection. Repeatedly
  modifying the model after inspecting test results would consume that holdout.
- **Why isn't lower volatility enough?** Profit, tail loss, capital usage and
  the cost of the risk reduction all matter. A strategy that never trades has
  zero inventory risk but is not automatically useful.
- **Why match spread and limit?** Otherwise multiple controls change at once,
  so attributing the outcome specifically to skew would be unjustified.
- **How can this become a stronger empirical study?** Calibrate arrival and fill
  assumptions using properly licensed order-flow data; model queue position and
  costs; predefine a chronological validation protocol before testing.

## Independent extension exercises

1. Derive the zero-fee/paid-fee P&L identity and write it as a test.
2. Add a funding charge on inventory, then explain how the optimal skew changes.
3. Add a delayed dealer observation without letting future prices enter quotes.
4. Replace the terminal haircut with a simple depth-dependent liquidation model.
5. Explain why a confidence interval for profit is not an interval for future
   live returns, and why a positive mean does not imply statistical significance.
'''
(root/'README.md').write_text(text)
plt.rcParams.update({'font.size':10,'svg.fonttype':'none'})
fig,ax=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
for row in r['training']:
 st=row['statistics'];sel=row['policy']==r['selected']
 ax[0].scatter(st['pnl_std'],st['mean_pnl'],color='#dc6b38' if sel else '#235a77',s=85 if sel else 30)
ax[0].set(xlabel='P&L standard deviation',ylabel='Mean net P&L',title='18 policies: training sample')
for regime in ['base','high_volatility','informed_flow','frequent_jumps']:
 rows=[x for x in r['evaluation'] if x['regime']==regime]
 ax[1].plot([x['fee_per_fill'] for x in rows],[x['statistics']['selected']['mean_pnl'] for x in rows],marker='o',label=regime.replace('_',' '))
ax[1].set(xlabel='Fee per fill (currency units)',ylabel='Mean net P&L',title='Frozen policy: held-out fee sensitivity')
ax[1].axhline(0,color='#777777',linewidth=.7)
ax[1].legend(frameon=False,fontsize=8)
for a in ax:a.spines[['top','right']].set_visible(False);a.grid(alpha=.15)
fig.savefig(root/'study.svg')
