# Mathematical Notes: Limit Order Book and Data Pipeline

The engineering modules emphasise correctness, deterministic behaviour and reproducible data handling.

## 1. Price-time priority

A resting order ranks first by **price priority**, then by arrival time within that price level:

- A buy order at the higher price ranks first.
- A sell order at the lower price ranks first.
- At equal price, the earlier accepted order ranks first.

With no currently crossing matchable orders, a valid book obeys

$$
best\ bid < best\ ask.
$$

## 2. Matched quantity

For incoming remaining quantity \(q_{in}\) and a matchable resting quantity \(q_{rest}\):

$$
q_{fill}=\min(q_{in},q_{rest}).
$$

Both quantities are reduced by exactly \(q_{fill}\). This produces a basic conservation invariant: a fill cannot consume more quantity than either side had available.

## 3. Reproducible ingestion

The price-data pipeline is a software-engineering project. Its invariants include deduplicating accepted observations, making replay idempotent, applying atomic transactions and quarantining invalid rows. The design prioritises predictable failure and recovery rather than any trading-performance claim.
