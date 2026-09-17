from dataclasses import replace
import pytest
from corporate_finance.valuation import Assumptions, dcf, comparables, acquisition, sensitivity


def inputs():
    return Assumptions(100,(0,0,0,0,0),.2,.25,.03,.03,.1,.1,0,20,10)


def test_flat_cashflow_equals_perpetuity():
    r = dcf(inputs())
    assert r["enterprise_value"] == pytest.approx(15/.1)
    assert r["equity_value"] == pytest.approx(130)
    assert r["value_per_share"] == pytest.approx(13)


def test_working_capital_and_cashflow_bridge():
    r = dcf(replace(inputs(), growth=(.1,)))
    f = r["forecast"][0]
    assert f["change_nwc"] == pytest.approx(1)
    assert f["ufcf"] == pytest.approx(15.5)


def test_sensitivity_and_net_debt():
    a = inputs()
    assert dcf(replace(a,wacc=.12))["value_per_share"] < dcf(a)["value_per_share"]
    assert dcf(replace(a,net_debt=30))["value_per_share"] == pytest.approx(12)
    assert len(sensitivity(a,[.08,.1,.12],[0,.01,.02])) == 9


@pytest.mark.parametrize("change", [dict(wacc=0),dict(terminal_growth=.1),dict(shares=0),dict(revenue=float('nan')),dict(growth=(-1,)),dict(tax_rate=1.1)])
def test_invalid_assumptions(change):
    with pytest.raises(ValueError):
        replace(inputs(),**change)


def test_comparables_exclude_nonmeaningful_multiples():
    r = comparables([dict(name="A",enterprise_value=100,ebitda=10),dict(name="B",enterprise_value=240,ebitda=20),dict(name="Loss",enterprise_value=100,ebitda=-1)],10,20,10)
    assert r["median_ev_ebitda"] == 11
    assert r["implied_value_per_share"] == 9
    assert r["excluded"] == ["Loss"]


def merger(**changes):
    args = dict(acquirer_net_income=100,acquirer_shares=50,acquirer_price=20,
                target_net_income=20,purchase_equity=200,cash_fraction=0,debt_fraction=0,
                debt_rate=.05,cash_yield=.02,pretax_synergies=0,tax_rate=.25)
    args.update(changes)
    return acquisition(**args)


def test_equal_pe_stock_deal_is_eps_neutral():
    assert merger()["accretion_dilution"] == pytest.approx(0)
    assert merger()["new_shares"] == 10


def test_debt_cost_and_after_tax_synergy():
    r = merger(debt_fraction=1,pretax_synergies=4)
    assert r["proforma_income"] == pytest.approx(115.5)
    assert r["proforma_eps"] == pytest.approx(2.31)


def test_invalid_financing_mix():
    with pytest.raises(ValueError):
        merger(cash_fraction=.6,debt_fraction=.5)
