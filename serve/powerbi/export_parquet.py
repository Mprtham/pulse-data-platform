"""
Export DuckDB marts to Parquet files for Power BI Desktop consumption.

Run from the repo root:
    python serve/powerbi/export_parquet.py

Or with a custom DB path:
    DUCKDB_PATH=warehouse/pulse.duckdb python serve/powerbi/export_parquet.py

Files land in serve/powerbi/data/ (gitignored — run this before opening Power BI).
"""

import os
import sys
from pathlib import Path

import duckdb

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "warehouse/pulse.duckdb")
OUT_DIR = Path(__file__).parent / "data"

EXPORTS = {
    "mart_daily_revenue": "SELECT * FROM marts.mart_daily_revenue",
    "mart_hourly_volume": "SELECT * FROM marts.mart_hourly_volume",
    "raw_quality_summary": """
        SELECT
            cast(ingested_at as date)                   AS ingest_date,
            COUNT(*)                                    AS total_rows,
            COUNT(invoice_no)                           AS valid_invoice,
            COUNT(*) - COUNT(invoice_no)                AS missing_invoice,
            COUNT(*) FILTER (unit_price < 0)            AS negative_price,
            COUNT(*) FILTER (quantity IS NULL)          AS null_quantity,
            ROUND(
                100.0 * COUNT(invoice_no) / COUNT(*), 2
            )                                           AS pct_valid
        FROM raw.orders
        GROUP BY cast(ingested_at as date)
        ORDER BY ingest_date DESC
    """,
}


def main() -> None:
    db = Path(DUCKDB_PATH)
    if not db.exists():
        print(f"[export] ERROR: DuckDB not found at {db.resolve()}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db), read_only=True)

    for name, sql in EXPORTS.items():
        out = OUT_DIR / f"{name}.parquet"
        conn.execute(f"COPY ({sql}) TO '{out}' (FORMAT PARQUET)")
        row_count = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{out}')").fetchone()[0]
        print(f"[export] {name}.parquet  {row_count:,} rows  {out}")

    conn.close()
    print("[export] Done. Open Power BI Desktop and Get Data > Parquet > serve/powerbi/data/")


if __name__ == "__main__":
    main()
