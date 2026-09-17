"""Synthetic inventory-control study with training/validation/test separation.

Unit trades, arbitrary currency units, no live prices. Randomness is shared
between strategies within each sample and independent between sample splits.
The informed trader sees part of the next move; the dealer sees current fair
value and inventory only. This is a stylized adverse-selection mechanism.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from itertools import product
from math import ceil
from pathlib import Path
import json
import numpy as np

@dataclass(frozen=True)
class Policy:
    spread: float
    skew: float
    limit: int

    def __post_init__(self):
        if not np.isfinite(self.spread) or self.spread <= 0:
            raise ValueError('spread must be finite and positive')
        if not np.isfinite(self.skew) or self.skew < 0:
            raise ValueError('skew must be finite and nonnegative')
        if type(self.limit) is not int or self.limit < 1:
            raise ValueError('limit must be a positive integer')

    @property
    def name(self):
        return f'spread={self.spread:g}, skew={self.skew:g}, limit={self.limit}'

@dataclass(frozen=True)
class Regime:
    volatility: float = .08
    informedness: float = .85
    jump_probability: float = .012


def paths(seed: int, trials: int, steps: int, regime: Regime) -> tuple[np.ndarray,np.ndarray]:
    if trials < 2 or steps < 1:
        raise ValueError('at least two trials and one step required')
    if not all(np.isfinite(v) for v in asdict(regime).values()):
        raise ValueError('regime inputs must be finite')
    if regime.volatility < 0 or regime.informedness < 0 or not 0 <= regime.jump_probability <= 1:
        raise ValueError('invalid regime')
    rng = np.random.default_rng(seed)
    moves = regime.volatility * rng.standard_normal((steps,trials))
    moves += (rng.random((steps,trials)) < regime.jump_probability) * rng.normal(0,.65,(steps,trials))
    signals = regime.informedness*moves + rng.normal(0,.18,(steps,trials))
    return moves, signals


def simulate(policy: Policy, moves: np.ndarray, signals: np.ndarray,
             fee: float = .005, liquidation_cost: float = .02) -> dict[str,np.ndarray]:
    if moves.shape != signals.shape or moves.ndim != 2 or moves.shape[0] < 1 or moves.shape[1] < 2:
        raise ValueError('equal nonempty step-by-trial arrays required')
    if not np.isfinite(moves).all() or not np.isfinite(signals).all():
        raise ValueError('finite paths required')
    if not np.isfinite(fee) or not np.isfinite(liquidation_cost) or min(fee,liquidation_cost)<0:
        raise ValueError('costs must be finite and nonnegative')
    n = moves.shape[1]
    fair = np.full(n,100.)
    cash = np.zeros(n)
    inventory = np.zeros(n,dtype=int)
    max_inventory = np.zeros(n,dtype=int)
    trades = np.zeros(n,dtype=int)
    peak = np.zeros(n)
    max_drawdown = np.zeros(n)
    for move, signal in zip(moves,signals):
        reservation = fair-policy.skew*inventory
        bid,ask = reservation-policy.spread,reservation+policy.spread
        trader = fair+signal
        dealer_sells = (trader>ask)&(inventory>-policy.limit)
        dealer_buys = (~dealer_sells)&(trader<bid)&(inventory<policy.limit)
        cash += np.where(dealer_sells,ask-fee,0)-np.where(dealer_buys,bid+fee,0)
        inventory += dealer_buys.astype(int)-dealer_sells.astype(int)
        trades += dealer_buys.astype(int)+dealer_sells.astype(int)
        fair += move
        max_inventory = np.maximum(max_inventory,abs(inventory))
        equity = cash+inventory*fair
        peak = np.maximum(peak,equity)
        max_drawdown = np.maximum(max_drawdown,peak-equity)
    pnl = cash+inventory*fair-liquidation_cost*abs(inventory)
    max_drawdown = np.maximum(max_drawdown,peak-pnl)
    return dict(pnl=pnl,max_inventory=max_inventory,trades=trades,
                final_inventory=inventory,max_drawdown=max_drawdown)


def summarise(result: dict) -> dict:
    pnl = result['pnl']
    mean,std = float(pnl.mean()),float(pnl.std(ddof=1))
    margin = 1.96*std/np.sqrt(len(pnl))
    tail_size = max(1,ceil(.05*len(pnl)))
    return dict(mean_pnl=mean,pnl_std=std,mean_ci95=[mean-margin,mean+margin],
                loss_frequency=float(np.mean(pnl<0)),
                expected_shortfall_95=float(-np.sort(pnl)[:tail_size].mean()),
                mean_max_drawdown=float(result['max_drawdown'].mean()),
                mean_max_inventory=float(result['max_inventory'].mean()),
                mean_trades=float(result['trades'].mean()))


def objective(stats: dict, risk_penalty: float = .1) -> float:
    # Chosen before test evaluation. Currency units; not a Sharpe ratio.
    return stats['mean_pnl']-risk_penalty*stats['pnl_std']


def paired_delta(selected: dict, baseline: dict) -> dict:
    d = selected['pnl']-baseline['pnl']
    margin = 1.96*float(d.std(ddof=1))/np.sqrt(len(d))
    return dict(mean=float(d.mean()),ci95=[float(d.mean()-margin),float(d.mean()+margin)])


def run_study(train_n=1000, validation_n=1000, test_n=2000, steps=500) -> dict:
    grid = [Policy(s,k,l) for s,k,l in product((.08,.12,.16),(0,.02,.04),(5,10))]
    train = paths(101,train_n,steps,Regime())
    ranked = sorted([(p,summarise(simulate(p,*train))) for p in grid],key=lambda x:objective(x[1]),reverse=True)
    shortlist = [x[0] for x in ranked[:3]]
    validation = paths(202,validation_n,steps,Regime())
    validation_rows = [(p,summarise(simulate(p,*validation))) for p in shortlist]
    selected = max(validation_rows,key=lambda x:objective(x[1]))[0]
    # Unchanged spread and position limit isolate the effect of inventory skew.
    baseline = Policy(selected.spread,0,selected.limit)
    symmetric_reference = Policy(.10,0,50)
    regimes = {'base':Regime(),'high_volatility':Regime(.16,.85,.012),
               'informed_flow':Regime(.08,1.2,.012),'frequent_jumps':Regime(.08,.85,.04)}
    evaluation = []
    for i,(name,regime) in enumerate(regimes.items()):
        data = paths(303+i,test_n,steps,regime)
        for fee in (0,.005,.02):
            results = {label:simulate(p,*data,fee=fee) for label,p in
                       [('selected',selected),('matched_control',baseline),('wide_limit_reference',symmetric_reference)]}
            evaluation.append(dict(regime=name,fee_per_fill=fee,
                                   statistics={k:summarise(v) for k,v in results.items()},
                                   selected_minus_control=paired_delta(results['selected'],results['matched_control'])))
    return dict(model='Synthetic unit-order dealer model; not a market-data backtest',
                protocol=dict(train_seed=101,validation_seed=202,test_seeds=[303,304,305,306],
                              train_trials=train_n,validation_trials=validation_n,test_trials_per_regime=test_n,
                              steps=steps,candidates=len(grid),shortlist=3,
                              objective='mean P&L - 0.1 * P&L standard deviation',
                              selection_fee=.005,liquidation_cost_per_unit=.02),
                selected=asdict(selected),matched_control=asdict(baseline),
                reference=asdict(symmetric_reference),
                training=[dict(policy=asdict(p),statistics=s,score=objective(s)) for p,s in ranked],
                validation=[dict(policy=asdict(p),statistics=s,score=objective(s)) for p,s in validation_rows],
                evaluation=evaluation)


if __name__=='__main__':
    output = run_study()
    target = Path(__file__).with_name('results.json')
    target.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print('Selected:',output['selected'])
    for row in output['evaluation']:
        if row['fee_per_fill']==.005:
            s=row['statistics']
            print(row['regime'], {k:round(v['mean_pnl'],3) for k,v in s.items()},row['selected_minus_control'])
