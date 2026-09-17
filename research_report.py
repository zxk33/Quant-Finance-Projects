"""Reproduce the market-making comparison and stress its model assumptions."""
from dataclasses import asdict
import json
import numpy as np
from market_making import Strategy, simulate_path, paired_experiment


def stress(trials=500, steps=500, seed=17):
    strategies = [Strategy("Symmetric", .10), Strategy("Inventory-aware", .10, .035, .0025, 10)]
    rows = []
    regimes = [("Base",.08,.85,.012),("Higher volatility",.16,.85,.012),
               ("More informed flow",.08,1.2,.012),("More jumps",.08,.85,.04)]
    for name, volatility, informedness, jump_probability in regimes:
        rng = np.random.default_rng(seed)
        pnls = [[],[]]
        inventories = [[],[]]
        for _ in range(trials):
            innovations = rng.standard_normal(steps)
            noise = rng.normal(0,.18,steps)
            jumps = (rng.random(steps)<jump_probability)*rng.normal(0,.65,steps)
            for i,s in enumerate(strategies):
                r = simulate_path(s,innovations,noise,jumps,volatility=volatility,informedness=informedness)
                pnls[i].append(r.pnl)
                inventories[i].append(r.max_abs_inventory)
        delta = np.array(pnls[1])-pnls[0]
        margin = float(1.96*delta.std(ddof=1)/np.sqrt(trials))
        rows.append(dict(regime=name,trials=trials,steps=steps,seed=seed,
                         volatility=volatility,informedness=informedness,jump_probability=jump_probability,
                         strategies=[dict(name=s.name,mean_pnl=float(np.mean(pnls[i])),
                                          pnl_std=float(np.std(pnls[i],ddof=1)),
                                          loss_frequency=float(np.mean(np.array(pnls[i])<0)),
                                          mean_max_inventory=float(np.mean(inventories[i]))) for i,s in enumerate(strategies)],
                         paired_mean_pnl_difference=float(delta.mean()),
                         paired_difference_ci95=[float(delta.mean()-margin),float(delta.mean()+margin)]))
    return rows


if __name__ == "__main__":
    print(json.dumps(dict(label="Synthetic model results; not live trading performance",
                          base=[asdict(r) for r in paired_experiment()],
                          stress=stress()),indent=2))
