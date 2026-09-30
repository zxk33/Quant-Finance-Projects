# Mathematical Notes: Market Systems Engineering

The engineering projects are software systems, but their design is built around
precise invariants and deterministic rules.

## Limit order book

Orders are ranked lexicographically by price priority and then time priority.
For bids, higher price ranks first; for asks, lower price ranks first. Within a
price level, earlier sequence number ranks first.

A valid book obeys the spread condition

[
best bid < best ask
]

whenever no crossing order is currently being matched.

For every execution with size q,

[
q = min(q_{incoming}, q_{resting}),
]

and remaining quantities are reduced by exactly q. This gives a simple
conservation invariant: executed quantity cannot exceed either side's available
quantity.

## Price-data pipeline

The data-ingestion project focuses on reproducibility rather than modelling.
Important invariants are uniqueness of accepted observations, idempotent replay,
atomic writes and explicit quarantine of invalid rows. A SHA-256 content key is
used to make repeated ingestion deterministic.
