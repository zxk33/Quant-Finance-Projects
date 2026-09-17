# Matching engine and auditable data pipeline

Two self-contained Python systems. All example events/prices are synthetic.
These are local educational tools, not deployed exchange infrastructure.

## 1. Limit order book

```bash
python -m engineering.orderbook engineering/sample_events.jsonl
python -m pytest engineering/test_systems.py -q
```

The book matches by best price, then arrival order. Prices are integer ticks,
quantities are integer units, and execution uses the resting order price.
Supported operations: limit orders, market orders, immediate-or-cancel (IOC),
partial fills, cancellation, depth snapshots, and deterministic JSONL replay.
GTC limit remainders rest; IOC and market remainders expire. IDs stay consumed
after cancellation or execution. Invalid requests leave the book unchanged.

**Design:** heaps index price levels; insertion-ordered dictionaries implement
FIFO queues and allow cancellation without scanning every order. Adding a new
price level costs O(log L); each fill removes or updates the oldest order at
that level. Cancellation removes an order in expected O(1), with stale heap
entries removed lazily. Snapshots sort levels and scan resting orders.

**Correctness:** tests cover FIFO, price priority, partial fills, cancellations,
expired quantities, duplicate IDs and replay. A separate slow list-based oracle
checks every fill in a seeded 2,000-order randomized stream. This is stronger
evidence than timing a few happy-path examples.

**Boundaries:** one instrument, one thread, no networking, persistence,
self-trade prevention, auctions or regulatory checks. The consumed-ID set,
trade history and lazily removed price heaps can grow over long sessions.

## 2. Price data ingestion

```bash
python -m engineering.data_pipeline engineering/sample_prices.csv --database /tmp/demo-prices.sqlite
# Run twice: the second load is identified by its content hash and skipped.
```

Schema: `symbol,date,close,volume`. The loader normalizes symbols and exact
decimal prices, validates dates and positive finite prices, and quarantines
malformed rows with original values and rejection reasons. Exact observations
are deduplicated. A different value for an existing symbol/date is quarantined;
it never silently changes the historical series.

**Design:** SHA-256 hashes make batch imports idempotent; a composite primary
key enforces one observation per symbol/date. `BEGIN IMMEDIATE` obtains the
SQLite writer lock before checking the batch, and the batch, observations and
quarantine records commit together. Parameterized SQL avoids string-built
queries. Prices are stored as decimal text to preserve source precision.

Tests check repeat imports, cross-batch conflicts, reopening the database,
malformed rows, and full rollback after an injected database failure.
The supplied fixture has three valid observations, one exact duplicate, and
three quarantined rows. CLI summaries include dates, observation counts and volume.

**Boundaries:** local batch tool, no authentication or web API; no corporate
action adjustment, calendar validation, feed licensing or automatic correction
workflow. SQL summary volume uses SQLite integers, so extremely large aggregate
volumes can overflow. Symbol/date uniqueness assumes a single price convention
and currency per symbol.

## Development provenance

These additions were implemented and tested with Codex assistance. The source,
tests and design notes are provided for review, modification and independent
reproduction. No production usage or independent authorship is claimed.
