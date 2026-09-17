import numpy as np
import pytest
from quant_research.inventory_study import Policy,Regime,paths,simulate,summarise,run_study


def test_hand_checked_adverse_selection_and_costs():
    # Sell at 100.1, then fair rises to 101; buy back at 100.9.
    moves=np.array([[1.,1.],[0.,0.]])
    signals=np.array([[2.,2.],[-2.,-2.]])
    r=simulate(Policy(.1,0,5),moves,signals,fee=.01)
    np.testing.assert_allclose(r['pnl'],-.82)
    np.testing.assert_array_equal(r['final_inventory'],0)
    np.testing.assert_array_equal(r['trades'],2)


def test_fee_identity_without_execution_feedback():
    data=paths(1,30,50,Regime())
    p=Policy(.1,.02,5)
    free=simulate(p,*data,fee=0,liquidation_cost=0)
    paid=simulate(p,*data,fee=.01,liquidation_cost=.03)
    np.testing.assert_allclose(free['pnl']-paid['pnl'],.01*paid['trades']+.03*abs(paid['final_inventory']),atol=1e-10)


def test_limits_and_no_trade_zero_pnl():
    m=np.zeros((100,2));s=np.ones((100,2))
    r=simulate(Policy(.1,0,3),m,s,fee=0,liquidation_cost=0)
    np.testing.assert_array_equal(r['max_inventory'],3)
    np.testing.assert_allclose(r['pnl'],.3)
    r=simulate(Policy(.1,0,3),m,m)
    np.testing.assert_array_equal(r['pnl'],0)


def test_independent_splits_and_reproducibility():
    a=paths(101,10,20,Regime()); b=paths(202,10,20,Regime())
    assert not np.array_equal(a[0],b[0])
    np.testing.assert_array_equal(a[0],paths(101,10,20,Regime())[0])


def test_test_sample_size_cannot_change_selection():
    a=run_study(20,20,20,20); b=run_study(20,20,40,20)
    assert a['selected']==b['selected']
    assert a['validation']==b['validation']
    assert a['protocol']['candidates']==18
    assert len(a['evaluation'])==12


@pytest.mark.parametrize('p',[(-1,0,2),(.1,-1,2),(.1,0,0)])
def test_invalid_policy(p):
    with pytest.raises(ValueError): Policy(*p)


def test_expected_shortfall_hand_calculation():
    r=dict(pnl=np.arange(-10,10,dtype=float),max_drawdown=np.zeros(20),max_inventory=np.zeros(20),trades=np.zeros(20))
    assert summarise(r)['expected_shortfall_95']==10
