from research_report import stress


def test_stress_reproducibility_and_paired_comparison():
    rows = stress(trials=20,steps=30,seed=3)
    assert rows == stress(trials=20,steps=30,seed=3)
    assert len(rows) == 4
    for row in rows:
        delta = row["strategies"][1]["mean_pnl"]-row["strategies"][0]["mean_pnl"]
        assert abs(delta-row["paired_mean_pnl_difference"]) < 1e-10
        lo,hi = row["paired_difference_ci95"]
        assert lo <= delta <= hi
