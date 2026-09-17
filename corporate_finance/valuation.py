"""DCF, trading comparables and simplified acquisition EPS scenarios.

Amounts share one currency/unit. Rates are decimals. End-year discounting;
terminal cash flow grows the final forecast UFCF at g. No tax loss carryforwards.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, replace
from math import isfinite
from statistics import median
import argparse
import json
from pathlib import Path


@dataclass(frozen=True)
class Assumptions:
    revenue: float
    growth: tuple[float, ...]
    ebit_margin: float
    tax_rate: float
    da_ratio: float
    capex_ratio: float
    nwc_ratio: float
    wacc: float
    terminal_growth: float
    net_debt: float
    shares: float

    def __post_init__(self):
        values = [self.revenue, *self.growth, self.ebit_margin, self.tax_rate,
                  self.da_ratio, self.capex_ratio, self.nwc_ratio, self.wacc,
                  self.terminal_growth, self.net_debt, self.shares]
        if not all(isfinite(v) for v in values):
            raise ValueError("all inputs must be finite")
        if self.revenue <= 0 or self.shares <= 0 or not self.growth:
            raise ValueError("positive revenue, shares and nonempty forecast required")
        if min(self.growth) <= -1 or self.terminal_growth <= -1:
            raise ValueError("growth must exceed -100%")
        if not self.wacc > self.terminal_growth or self.wacc <= 0:
            raise ValueError("WACC must be positive and greater than terminal growth")
        if not 0 <= self.tax_rate <= 1 or not -1 <= self.ebit_margin <= 1:
            raise ValueError("invalid tax rate or margin")
        if min(self.da_ratio, self.capex_ratio, self.nwc_ratio) < 0:
            raise ValueError("operating ratios cannot be negative")


def dcf(a: Assumptions) -> dict:
    previous = a.revenue
    forecast = []
    for year, growth in enumerate(a.growth, start=1):
        revenue = previous * (1 + growth)
        ebit = revenue * a.ebit_margin
        tax = max(ebit, 0) * a.tax_rate
        da, capex = revenue * a.da_ratio, revenue * a.capex_ratio
        change_nwc = (revenue - previous) * a.nwc_ratio
        ufcf = ebit - tax + da - capex - change_nwc
        forecast.append(dict(year=year, revenue=revenue, ebit=ebit, tax=tax,
                             depreciation=da, capex=capex, change_nwc=change_nwc,
                             ufcf=ufcf, pv=ufcf / (1 + a.wacc)**year))
        previous = revenue
    terminal = forecast[-1]["ufcf"] * (1 + a.terminal_growth) / (a.wacc - a.terminal_growth)
    terminal_pv = terminal / (1 + a.wacc)**len(a.growth)
    enterprise = sum(row["pv"] for row in forecast) + terminal_pv
    equity = enterprise - a.net_debt
    return dict(forecast=forecast, terminal_value=terminal, terminal_pv=terminal_pv,
                enterprise_value=enterprise, net_debt=a.net_debt, equity_value=equity,
                value_per_share=equity / a.shares,
                terminal_share_of_ev=terminal_pv / enterprise if enterprise else None)


def sensitivity(a: Assumptions, waccs: list[float], growths: list[float]) -> list[dict]:
    return [dict(wacc=w, terminal_growth=g,
                 value_per_share=dcf(replace(a, wacc=w, terminal_growth=g))["value_per_share"])
            for w in waccs for g in growths]


def comparables(peers: list[dict], target_ebitda: float, net_debt: float, shares: float) -> dict:
    if not all(isfinite(v) for v in [target_ebitda, net_debt, shares]) or target_ebitda <= 0 or shares <= 0:
        raise ValueError("positive EBITDA and shares required")
    included, excluded = [], []
    for p in peers:
        ev, ebitda = p["enterprise_value"], p["ebitda"]
        if not isfinite(ev) or not isfinite(ebitda) or ev <= 0 or ebitda <= 0:
            excluded.append(p["name"])
        else:
            included.append(dict(name=p["name"], ev_ebitda=ev / ebitda))
    if not included:
        raise ValueError("no peers with positive finite EV and EBITDA")
    multiple = median(p["ev_ebitda"] for p in included)
    ev = target_ebitda * multiple
    return dict(included=included, excluded=excluded, median_ev_ebitda=multiple,
                implied_enterprise_value=ev, implied_equity_value=ev-net_debt,
                implied_value_per_share=(ev-net_debt)/shares)


def acquisition(*, acquirer_net_income: float, acquirer_shares: float,
                acquirer_price: float, target_net_income: float, purchase_equity: float,
                cash_fraction: float, debt_fraction: float, debt_rate: float,
                cash_yield: float, pretax_synergies: float, tax_rate: float) -> dict:
    values = locals().copy()
    if not all(isfinite(v) for v in values.values()):
        raise ValueError("inputs must be finite")
    if min(acquirer_net_income, acquirer_shares, acquirer_price, purchase_equity) <= 0:
        raise ValueError("positive acquirer income, shares, price and purchase price required")
    if min(cash_fraction, debt_fraction, debt_rate, cash_yield, pretax_synergies) < 0:
        raise ValueError("financing inputs cannot be negative")
    if cash_fraction + debt_fraction > 1 or not 0 <= tax_rate <= 1:
        raise ValueError("invalid financing mix or tax rate")
    stock_fraction = 1 - cash_fraction - debt_fraction
    new_shares = purchase_equity * stock_fraction / acquirer_price
    interest = purchase_equity * debt_fraction * debt_rate
    foregone_interest = purchase_equity * cash_fraction * cash_yield
    adjustment = (pretax_synergies - interest - foregone_interest) * (1 - tax_rate)
    proforma_income = acquirer_net_income + target_net_income + adjustment
    standalone_eps = acquirer_net_income / acquirer_shares
    proforma_eps = proforma_income / (acquirer_shares + new_shares)
    return dict(new_shares=new_shares, interest_expense=interest,
                foregone_cash_interest=foregone_interest, proforma_income=proforma_income,
                standalone_eps=standalone_eps, proforma_eps=proforma_eps,
                accretion_dilution=proforma_eps/standalone_eps-1)


def report(config: dict) -> dict:
    a = Assumptions(**config["dcf"])
    scenarios = {name: dcf(replace(a, **changes)) for name, changes in config["scenarios"].items()}
    return {"label": config["label"], "assumptions": asdict(a), "dcf": dcf(a),
            "scenarios": scenarios,
            "sensitivity": sensitivity(a, config["waccs"], config["terminal_growths"]),
            "comparables": comparables(**config["comparables"]),
            "acquisition": acquisition(**config["acquisition"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    args = parser.parse_args()
    print(json.dumps(report(json.loads(Path(args.config).read_text())), indent=2, allow_nan=False))
