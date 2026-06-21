import json
import os
import time
from datetime import datetime, timezone

import duckdb
from confluent_kafka import Consumer, KafkaError

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "../warehouse/pulse.duckdb")
TOPIC = "orders.raw"
BATCH_SIZE = 50
FLUSH_INTERVAL = 5.0  # seconds


def bootstrap(path: str):
    conn = duckdb.connect(path)
    conn.execute("""
        CREATE SCHEMA IF NOT EXISTS raw;
        CREATE TABLE IF NOT EXISTS raw.orders (
            invoice_no   VARCHAR,
            stock_code   VARCHAR,
            description  VARCHAR,
            quantity     INTEGER,
            invoice_date TIMESTAMP,
            unit_price   DOUBLE,
            customer_id  VARCHAR,
            country      VARCHAR,
            ingested_at  TIMESTAMP
        );
    """)
    conn.close()


def flush(path: str, batch: list[dict]) -> int:
    if not batch:
        return 0
    # Open, write, checkpoint, close — hold the lock for milliseconds only.
    # This lets the status API (read-only, separate container) connect freely
    # between flushes without hitting a cross-container PID-namespace lock conflict.
    conn = duckdb.connect(path)
    conn.executemany(
        """
        INSERT INTO raw.orders
            (invoice_no, stock_code, description, quantity,
             invoice_date, unit_price, customer_id, country, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r.get("invoice_no"),
                r.get("stock_code"),
                r.get("description"),
                r.get("quantity"),
                r.get("invoice_date"),
                r.get("unit_price"),
                r.get("customer_id"),
                r.get("country"),
                r.get("ingested_at") or datetime.now(timezone.utc).isoformat(),
            )
            for r in batch
        ],
    )
    conn.execute("CHECKPOINT")
    conn.close()
    return len(batch)


def main():
    time.sleep(5)  # wait for Redpanda to be fully ready

    bootstrap(DUCKDB_PATH)

    consumer = Consumer(
        {
            "bootstrap.servers": BROKER,
            "group.id": "pulse-ingest",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([TOPIC])
    print(f"[ingest] subscribed to {TOPIC} on {BROKER}", flush=True)

    batch: list[dict] = []
    last_flush = time.time()
    total = 0

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                pass
            elif msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"[ingest] error: {msg.error()}", flush=True)
            else:
                try:
                    batch.append(json.loads(msg.value()))
                except json.JSONDecodeError:
                    print(f"[ingest] bad JSON: {msg.value()}", flush=True)

            age = time.time() - last_flush
            if len(batch) >= BATCH_SIZE or (batch and age >= FLUSH_INTERVAL):
                n = flush(DUCKDB_PATH, batch)
                total += n
                print(f"[ingest] flushed {n} rows (total={total})", flush=True)
                batch.clear()
                last_flush = time.time()

    except KeyboardInterrupt:
        pass
    finally:
        flush(DUCKDB_PATH, batch)
        consumer.close()
