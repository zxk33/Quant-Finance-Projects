"""Single-instrument, single-threaded limit order book using integer price ticks.

Heap-indexed price levels hold insertion-ordered queues. Trades execute at the
resting order's price. Market/IOC remainders expire; IDs cannot be reused.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import argparse
import heapq
import json
from pathlib import Path


@dataclass
class Order:
    order_id: str
    side: str
    quantity: int
    price: int | None


@dataclass(frozen=True)
class Trade:
    maker: str
    taker: str
    price: int
    quantity: int


class OrderBook:
    def __init__(self) -> None:
        self.levels: dict[str, dict[int, dict[str, Order]]] = {"buy": {}, "sell": {}}
        self.heaps: dict[str, list[int]] = {"buy": [], "sell": []}
        self.active: dict[str, Order] = {}
        self.seen: set[str] = set()
        self.trades: list[Trade] = []

    def _best(self, side: str) -> int | None:
        heap = self.heaps[side]
        while heap:
            price = -heap[0] if side == "buy" else heap[0]
            if self.levels[side].get(price):
                return price
            heapq.heappop(heap)
        return None

    def submit(self, order_id: str, side: str, quantity: int,
               price: int | None = None, tif: str = "GTC") -> dict:
        if not isinstance(order_id, str) or not order_id or order_id in self.seen:
            raise ValueError("order_id must be nonempty and never previously used")
        if side not in self.levels or tif not in {"GTC", "IOC"}:
            raise ValueError("invalid side or time in force")
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if price is not None and (type(price) is not int or price <= 0):
            raise ValueError("price must be positive integer ticks")
        self.seen.add(order_id)
        incoming = Order(order_id, side, quantity, price)
        opposite = "sell" if side == "buy" else "buy"
        fills = []
        while incoming.quantity:
            best = self._best(opposite)
            if best is None or (price is not None and
                 ((side == "buy" and best > price) or (side == "sell" and best < price))):
                break
            queue = self.levels[opposite][best]
            maker = next(iter(queue.values()))
            matched = min(incoming.quantity, maker.quantity)
            fill = Trade(maker.order_id, order_id, best, matched)
            fills.append(fill)
            self.trades.append(fill)
            maker.quantity -= matched
            incoming.quantity -= matched
            if maker.quantity == 0:
                del queue[maker.order_id]
                del self.active[maker.order_id]
            if not queue:
                del self.levels[opposite][best]
        remaining = incoming.quantity
        resting = bool(remaining and price is not None and tif == "GTC")
        if resting:
            if price not in self.levels[side]:
                self.levels[side][price] = {}
                heapq.heappush(self.heaps[side], -price if side == "buy" else price)
            self.levels[side][price][order_id] = incoming
            self.active[order_id] = incoming
        return {"order_id": order_id, "filled": quantity - remaining,
                "resting": remaining if resting else 0,
                "expired": remaining if not resting else 0,
                "trades": [asdict(t) for t in fills]}

    def cancel(self, order_id: str) -> int:
        if order_id not in self.active:
            raise KeyError(order_id)
        order = self.active.pop(order_id)
        queue = self.levels[order.side][order.price]
        del queue[order_id]
        if not queue:
            del self.levels[order.side][order.price]
        return order.quantity

    def snapshot(self) -> dict:
        result = {}
        for side in ("buy", "sell"):
            result[side] = [
                {"price": p, "quantity": sum(o.quantity for o in queue.values()),
                 "orders": list(queue)}
                for p, queue in sorted(self.levels[side].items(), reverse=side == "buy")
            ]
        return result

    def apply(self, event: dict) -> dict:
        data = dict(event)
        kind = data.pop("type")
        if kind == "submit":
            return self.submit(**data)
        if kind == "cancel" and set(data) == {"order_id"}:
            return {"cancelled": self.cancel(data["order_id"])}
        raise ValueError("unknown event or invalid fields")


def replay(path: str | Path) -> dict:
    book = OrderBook()
    outcomes = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            outcomes.append(book.apply(json.loads(line)))
    return {"outcomes": outcomes, "book": book.snapshot(),
            "trades": [asdict(t) for t in book.trades]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", help="JSONL event file")
    args = parser.parse_args()
    print(json.dumps(replay(args.events), indent=2))
