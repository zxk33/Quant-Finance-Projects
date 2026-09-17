"""Transactional CSV-to-SQLite price loader with quarantine and content hashes.

One immutable close per (symbol,date). Exact duplicates are skipped; conflicting
observations are quarantined rather than silently overwriting history.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
 digest TEXT PRIMARY KEY, source TEXT NOT NULL, loaded INTEGER NOT NULL,
 rejected INTEGER NOT NULL, duplicates INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS prices (
 symbol TEXT NOT NULL, day TEXT NOT NULL, close TEXT NOT NULL,
 volume INTEGER NOT NULL CHECK(volume>=0), digest TEXT NOT NULL,
 PRIMARY KEY(symbol,day));
CREATE TABLE IF NOT EXISTS quarantine (
 digest TEXT NOT NULL, row_number INTEGER NOT NULL, raw TEXT NOT NULL,
 reason TEXT NOT NULL, PRIMARY KEY(digest,row_number));
"""


def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    return db


def validate(row: dict) -> tuple[str, str, str, int]:
    symbol = row["symbol"].strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", symbol):
        raise ValueError("invalid symbol")
    raw_day = row["date"].strip()
    day = date.fromisoformat(raw_day).isoformat()
    if day != raw_day:
        raise ValueError("date must use YYYY-MM-DD")
    close = Decimal(row["close"])
    if not close.is_finite() or close <= 0:
        raise ValueError("close must be finite and positive")
    if not re.fullmatch(r"\d+", row["volume"].strip()):
        raise ValueError("volume must be a nonnegative integer")
    volume = int(row["volume"])
    if volume > 2**63 - 1:
        raise ValueError("volume exceeds SQLite integer range")
    return symbol, day, format(close.normalize(), "f"), volume


def ingest(db: sqlite3.Connection, path: str | Path) -> dict:
    path = Path(path)
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames != ["symbol", "date", "close", "volume"]:
        raise ValueError("required CSV header: symbol,date,close,volume")
    # BEGIN IMMEDIATE serializes competing loaders before the idempotency check.
    db.execute("BEGIN IMMEDIATE")
    try:
        previous = db.execute("SELECT loaded,rejected,duplicates FROM batches WHERE digest=?", (digest,)).fetchone()
        if previous:
            db.commit()
            return {"digest": digest, "loaded": 0, "rejected": 0, "duplicates": 0, "already_loaded": True}
        loaded = rejected = duplicates = 0
        for row_number, row in enumerate(reader, start=2):
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("wrong field count")
                symbol, day, close, volume = validate(row)
                existing = db.execute("SELECT close,volume FROM prices WHERE symbol=? AND day=?", (symbol, day)).fetchone()
                if existing:
                    if existing == (close, volume):
                        duplicates += 1
                        continue
                    raise ValueError("conflicting observation for existing symbol/date")
                db.execute("INSERT INTO prices VALUES (?,?,?,?,?)", (symbol, day, close, volume, digest))
                loaded += 1
            except (ValueError, InvalidOperation, TypeError) as exc:
                db.execute("INSERT INTO quarantine VALUES (?,?,?,?)",
                           (digest, row_number, json.dumps(row, sort_keys=False), str(exc)))
                rejected += 1
        db.execute("INSERT INTO batches VALUES (?,?,?,?,?)", (digest, path.name, loaded, rejected, duplicates))
        db.commit()
        return {"digest": digest, "loaded": loaded, "rejected": rejected,
                "duplicates": duplicates, "already_loaded": False}
    except BaseException:
        db.rollback()
        raise


def summary(db: sqlite3.Connection) -> list[dict]:
    return [dict(zip(("symbol", "observations", "first_date", "last_date", "volume"), row))
            for row in db.execute("SELECT symbol,COUNT(*),MIN(day),MAX(day),SUM(volume) FROM prices GROUP BY symbol ORDER BY symbol")]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--database", default="prices.sqlite")
    args = parser.parse_args()
    db = connect(args.database)
    try:
        print(json.dumps({"ingestion": ingest(db, args.csv), "summary": summary(db)}, indent=2))
    finally:
        db.close()
