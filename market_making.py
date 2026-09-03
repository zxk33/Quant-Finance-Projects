from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Strategy:
    name: str
    half_spread: float = 0.10
    inventory_skew: float = 0.0
    inventory_widening: float = 0.0
    position_limit: int | None = None


@dataclass(frozen=True)
class PathResult:
    pnl: float
    max_abs_inventory: int
    trades: int


@dataclass(frozen=True)
class ExperimentResult:
    strategy: str
    mean_pnl: float
    pnl_volatility: float
    loss_frequency: float
    mean_max_inventory: float
    confidence_interval_95: tuple[float, float]


def simulate_path(
    strategy: Strategy,
    innovations: np.ndarray,
    noise: np.ndarray,
    jumps: np.ndarray,
    *,
    start_price: float = 100.0,
    volatility: float = 0.08,
    informedness: float = 0.85,
) -> PathResult:
    if not (len(innovations) == len(noise) == len(jumps)):
        raise ValueError("all random input arrays must have equal length")

    fair = start_price
    cash = 0.0
    inventory = 0
    max_abs_inventory = 0
    trades = 0

    for innovation, order_noise, jump in zip(innovations, noise, jumps, strict=True):
        next_move = volatility * innovation + jump
        reservation = fair - strategy.inventory_skew * inventory
        width = strategy.half_spread + strategy.inventory_widening * abs(inventory)
        bid, ask = reservation - width, reservation + width
        trader_value = fair + informedness * next_move + order_noise

        can_buy = strategy.position_limit is None or inventory > -strategy.position_limit
        can_sell = strategy.position_limit is None or inventory < strategy.position_limit
        if trader_value > ask and can_buy:
            inventory -= 1
            cash += ask
            trades += 1
        elif trader_value < bid and can_sell:
            inventory += 1
            cash -= bid
            trades += 1

        fair += next_move
        max_abs_inventory = max(max_abs_inventory, abs(inventory))

    return PathResult(cash + inventory * fair, max_abs_inventory, trades)


def _summarise(name: str, paths: list[PathResult]) -> ExperimentResult:
    pnl = np.array([path.pnl for path in paths], dtype=float)
    max_inventory = np.array([path.max_abs_inventory for path in paths], dtype=float)
    std = float(pnl.std(ddof=1))
    margin = 1.96 * std / np.sqrt(len(pnl))
    mean = float(pnl.mean())
    return ExperimentResult(
        strategy=name,
        mean_pnl=mean,
        pnl_volatility=std,
        loss_frequency=float(np.mean(pnl < 0.0)),
        mean_max_inventory=float(max_inventory.mean()),
        confidence_interval_95=(mean - margin, mean + margin),
    )


def paired_experiment(trials: int = 2_000, steps: int = 500, seed: int = 7) -> tuple[ExperimentResult, ExperimentResult]:
    if trials < 2 or steps < 1:
        raise ValueError("trials must be at least 2 and steps positive")
    rng = np.random.default_rng(seed)
    baseline = Strategy("Symmetric quoting", half_spread=0.10)
    risk_aware = Strategy(
        "Inventory-aware quoting",
        half_spread=0.10,
        inventory_skew=0.035,
        inventory_widening=0.0025,
        position_limit=10,
    )
    baseline_paths: list[PathResult] = []
    risk_paths: list[PathResult] = []
    for _ in range(trials):
        innovations = rng.standard_normal(steps)
        noise = rng.normal(0.0, 0.18, steps)
        shock_occurs = rng.random(steps) < 0.012
        jumps = shock_occurs * rng.normal(0.0, 0.65, steps)
        baseline_paths.append(simulate_path(baseline, innovations, noise, jumps))
        risk_paths.append(simulate_path(risk_aware, innovations, noise, jumps))
    return _summarise(baseline.name, baseline_paths), _summarise(risk_aware.name, risk_paths)
