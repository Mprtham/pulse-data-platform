CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.orders (
    invoice_no      VARCHAR,
    stock_code      VARCHAR,
    description     VARCHAR,
    quantity        INTEGER,
    invoice_date    TIMESTAMP,
    unit_price      DOUBLE,
    customer_id     VARCHAR,
    country         VARCHAR,
    ingested_at     TIMESTAMP DEFAULT now()
);
