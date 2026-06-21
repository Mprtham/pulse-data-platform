import json
import os
import random
import time
from datetime import datetime, timezone
from collections import deque

from confluent_kafka import Producer
from faults import maybe_inject

BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC = "orders.raw"

STOCK_ITEMS = [
    ("85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 2.55),
    ("71053",  "WHITE METAL LANTERN",                3.39),
    ("84406B", "CREAM CUPID HEARTS COAT HANGER",     2.75),
    ("84029G", "KNITTED UNION FLAG HOT WATER BOTTLE", 3.39),
    ("84029E", "RED WOOLLY HOTTIE WHITE HEART",       3.39),
    ("22752",  "SET 7 BABUSHKA NESTING BOXES",        7.65),
    ("21730",  "GLASS STAR FROSTED T-LIGHT HOLDER",   4.25),
    ("22633",  "HAND WARMER UNION JACK",               1.85),
    ("22632",  "HAND WARMER RED POLKA DOT",            1.85),
    ("47566",  "PARTY BUNTING",                        5.50),
]

COUNTRIES = [
    "United Kingdom", "United Kingdom", "United Kingdom",
    "Germany", "France", "Spain", "Netherlands", "Australia",
]

CUSTOMER_IDS = [f"C{i:05d}" for i in range(10000, 10200)]

_recent_invoices: deque = deque(maxlen=200)
_invoice_counter = 536000


def next_invoice_no() -> str:
    global _invoice_counter
    _invoice_counter += 1
    no = str(_invoice_counter)
    _recent_invoices.append(no)
    return no


def build_event() -> dict:
    stock_code, description, base_price = random.choice(STOCK_ITEMS)
    qty = random.randint(1, 12)
    price = round(base_price * random.uniform(0.9, 1.1), 2)

    now = datetime.now(timezone.utc).isoformat()
    return {
        "invoice_no":   next_invoice_no(),
        "stock_code":   stock_code,
        "description":  description,
        "quantity":     qty,
        "invoice_date": now,
        "unit_price":   price,
        "customer_id":  random.choice(CUSTOMER_IDS),
        "country":      random.choice(COUNTRIES),
        "ingested_at":  now,
    }


def delivery_report(err, msg):
    if err:
        print(f"[generator] delivery failed: {err}")


def main():
    producer = Producer({"bootstrap.servers": BROKER})
    print(f"[generator] connected to {BROKER}, streaming to {TOPIC}")

    while True:
        event = build_event()
        event = maybe_inject(event)

        if event.pop("_force_duplicate", False) and _recent_invoices:
            event["invoice_no"] = random.choice(list(_recent_invoices))

        producer.produce(
            TOPIC,
            key=event.get("invoice_no", "null"),
            value=json.dumps(event),
            callback=delivery_report,
        )
        producer.poll(0)

        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)


if __name__ == "__main__":
    main()
