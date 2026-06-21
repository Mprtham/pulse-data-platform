import json
import os
import time

import duckdb
from confluent_kafka import Consumer, KafkaError

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "../warehouse/pulse.duckdb")
TOPIC = "orders.raw"
BATCH_SIZE = 50
FLUSH_INTERVAL = 5.0  # seconds


def bootstrap(conn: duckdb.DuckDBPyConnection):
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
            ingested_at  TIMESTAMP DEFAULT now()
        );
    """)


def flush(conn: duckdb.DuckDBPyConnection, batch: list[dict]) -> int:
    if not batch:
        return 0
    conn.executemany(
        """
        INSERT INTO raw.orders
            (invoice_no, stock_code, description, quantity,
             invoice_date, unit_price, customer_id, country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
            )
            for r in batch
        ],
    )
    return len(batch)


def main():
    # Wait for Redpanda to be fully ready
    time.sleep(5)

    conn = duckdb.connect(DUCKDB_PATH)
    bootstrap(conn)

    consumer = Consumer(
        {
            "bootstrap.servers": BROKER,
            "group.id": "pulse-ingest",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([TOPIC])
    print(f"[ingest] subscribed to {TOPIC} on {BROKER}")

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
                    print(f"[ingest] error: {msg.error()}")
            else:
                try:
                    batch.append(json.loads(msg.value()))
                except json.JSONDecodeError:
                    print(f"[ingest] bad JSON: {msg.value()}")

            age = time.time() - last_flush
            if len(batch) >= BATCH_SIZE or (batch and age >= FLUSH_INTERVAL):
                n = flush(conn, batch)
                total += n
                print(f"[ingest] flushed {n} rows (total={total})")
                batch.clear()
                last_flush = time.time()

    except KeyboardInterrupt:
        pass
    finally:
        flush(conn, batch)
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()
