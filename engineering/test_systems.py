import json
import random
import sqlite3
import pytest
from engineering.orderbook import OrderBook, replay
from engineering.data_pipeline import connect, ingest, summary


def test_price_time_priority_and_partial_fills():
    b = OrderBook()
    b.submit("expensive", "sell", 3, 102)
    b.submit("first", "sell", 4, 100)
    b.submit("second", "sell", 5, 100)
    result = b.submit("buyer", "buy", 7, 102)
    assert [(t["maker"], t["quantity"], t["price"]) for t in result["trades"]] == [("first", 4, 100), ("second", 3, 100)]
    assert b.active["second"].quantity == 2
    assert b.snapshot()["sell"][0]["quantity"] == 2


def test_ioc_market_and_limit_remainders():
    b = OrderBook()
    b.submit("ask", "sell", 2, 110)
    assert b.submit("ioc", "buy", 3, 109, "IOC")["expired"] == 3
    assert b.submit("market", "buy", 5)["expired"] == 3
    assert not b.active
    assert b.submit("limit", "buy", 5, 99)["resting"] == 5


def test_cancel_then_reuse_price_level():
    b = OrderBook()
    b.submit("old", "buy", 4, 100)
    assert b.cancel("old") == 4
    b.submit("new", "buy", 2, 100)
    assert b.submit("sell", "sell", 3)["filled"] == 2
    assert b.snapshot() == {"buy": [], "sell": []}
    with pytest.raises(KeyError):
        b.cancel("old")


@pytest.mark.parametrize("kwargs", [dict(side="bad",quantity=1,price=1), dict(side="buy",quantity=0,price=1), dict(side="buy",quantity=True,price=1), dict(side="buy",quantity=1,price=1.5)])
def test_rejected_order_does_not_consume_id(kwargs):
    b = OrderBook()
    with pytest.raises(ValueError):
        b.submit("id", **kwargs)
    assert not b.seen


def test_id_cannot_be_reused_after_fill():
    b = OrderBook()
    b.submit("id", "buy", 1)
    with pytest.raises(ValueError):
        b.submit("id", "buy", 1)


def test_deterministic_replay(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text('\n'.join(json.dumps(x) for x in [
        dict(type="submit",order_id="a",side="sell",quantity=2,price=101),
        dict(type="submit",order_id="b",side="buy",quantity=1,price=101),
        dict(type="cancel",order_id="a")]))
    assert replay(path) == replay(path)
    assert replay(path)["book"] == {"buy": [], "sell": []}


def test_random_stream_matches_independent_reference():
    rng = random.Random(7)
    b = OrderBook()
    # Deliberately slow list-based oracle, independent of production heaps/queues.
    active = []
    for i in range(2000):
        side, price, qty = rng.choice(["buy", "sell"]), rng.randint(95,105), rng.randint(1,10)
        original = qty
        expected = []
        while qty:
            eligible = [o for o in active if o[1] != side and (o[2] <= price if side == "buy" else o[2] >= price)]
            if not eligible:
                break
            maker = min(eligible, key=lambda o: (o[2] if side == "buy" else -o[2], o[0]))
            fill = min(qty, maker[3])
            expected.append((str(maker[0]), maker[2], fill))
            qty -= fill
            maker[3] -= fill
            if not maker[3]:
                active.remove(maker)
        if qty:
            active.append([i,side,price,qty])
        result = b.submit(str(i),side,original,price)
        assert [(t["maker"],t["price"],t["quantity"]) for t in result["trades"]] == expected
        assert sum(o.quantity for o in b.active.values()) == sum(o[3] for o in active)


def csv_file(tmp_path, rows, name="data.csv"):
    p = tmp_path / name
    p.write_text("symbol,date,close,volume\n" + rows)
    return p


def test_ingestion_quarantine_duplicates_and_idempotency(tmp_path):
    p = csv_file(tmp_path,"AAA,2025-01-01,10,100\nAAA,2025-01-01,10.0,100\nAAA,2025-01-01,11,100\nBBB,2025-02-30,5,1\nBBB,2025-01-01,NaN,1\n")
    db = connect(":memory:")
    result = ingest(db,p)
    assert (result["loaded"],result["duplicates"],result["rejected"]) == (1,1,3)
    assert ingest(db,p)["already_loaded"]
    assert db.execute("SELECT COUNT(*) FROM quarantine").fetchone()[0] == 3
    assert summary(db)[0]["volume"] == 100


def test_cross_batch_conflict_and_persistence(tmp_path):
    path = tmp_path / "db.sqlite"
    db = connect(path)
    ingest(db,csv_file(tmp_path,"AAA,2025-01-01,10,100\n"))
    db.close()
    db = connect(path)
    result = ingest(db,csv_file(tmp_path,"AAA,2025-01-01,12,100\nAAA,2025-01-02,11,200\n","second.csv"))
    assert (result["loaded"], result["rejected"]) == (1,1)
    assert db.execute("SELECT close FROM prices WHERE day='2025-01-01'").fetchone()[0] == "10"


def test_database_failure_rolls_back_whole_batch(tmp_path):
    db = connect(":memory:")
    db.executescript("CREATE TRIGGER fail_insert BEFORE INSERT ON prices WHEN NEW.symbol='FAIL' BEGIN SELECT RAISE(ABORT,'injected failure'); END;")
    p = csv_file(tmp_path,"AAA,2025-01-01,10,1\nFAIL,2025-01-01,10,1\n")
    with pytest.raises(sqlite3.IntegrityError):
        ingest(db,p)
    assert db.execute("SELECT COUNT(*) FROM prices").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM batches").fetchone()[0] == 0


def test_bad_header_and_field_count(tmp_path):
    db = connect(":memory:")
    p = tmp_path / "bad.csv"
    p.write_text("x,y\n1,2\n")
    with pytest.raises(ValueError):
        ingest(db,p)
    p = csv_file(tmp_path,"AAA,2025-01-01,10\nAAA,2025-01-02,10,1,extra\n")
    assert ingest(db,p)["rejected"] == 2
