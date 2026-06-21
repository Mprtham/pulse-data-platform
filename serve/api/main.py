import json
import os
from datetime import datetime, timezone
from pathlib import Path

import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "../../warehouse/pulse.duckdb")
RUN_RESULTS_PATH = os.getenv(
    "DBT_RUN_RESULTS",
    "../../transform/target/run_results.json",
)

FRESHNESS_WARN_S = 300    # 5 min
FRESHNESS_ERROR_S = 900   # 15 min

app = FastAPI(title="Pulse Status API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


class StatusResponse(BaseModel):
    last_event_ago_s: int | None
    rows_today: int
    tests_passing: int
    tests_total: int
    pipeline_status: str   # HEALTHY | DEGRADED | DOWN
    updated_at: str


def _read_duckdb() -> tuple[int | None, int]:
    """Returns (seconds_since_last_event, rows_today). Read-only connection."""
    try:
        conn = duckdb.connect(DUCKDB_PATH, read_only=True)
        row = conn.execute(
            "SELECT MAX(ingested_at) FROM raw.orders"
        ).fetchone()
        last_at = row[0] if row else None

        if last_at is not None:
            # DuckDB TIMESTAMP (no tz) stores local wall-clock time.
            # Treat it as UTC for comparison; clamp negatives to 0 (sub-second skew).
            if last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=timezone.utc)
            ago = max(0, int((datetime.now(timezone.utc) - last_at).total_seconds()))
        else:
            ago = None

        today_row = conn.execute(
            "SELECT COUNT(*) FROM raw.orders "
            "WHERE cast(ingested_at as date) = current_date"
        ).fetchone()
        rows_today = int(today_row[0]) if today_row else 0

        conn.close()
        return ago, rows_today
    except Exception:
        return None, 0


def _read_test_results() -> tuple[int, int]:
    """Returns (passing, total) from dbt run_results.json."""
    path = Path(RUN_RESULTS_PATH)
    if not path.exists():
        return 0, 0
    try:
        data = json.loads(path.read_text())
        results = data.get("results", [])
        tests = [r for r in results if r.get("unique_id", "").startswith("test.")]
        total = len(tests)
        passing = sum(1 for r in tests if r.get("status") == "pass")
        return passing, total
    except Exception:
        return 0, 0


def _pipeline_status(ago_s: int | None, passing: int, total: int) -> str:
    if ago_s is None or ago_s > FRESHNESS_ERROR_S:
        return "DOWN"
    if ago_s > FRESHNESS_WARN_S:
        return "DEGRADED"
    if total > 0 and passing < total:
        return "DEGRADED"
    return "HEALTHY"


@app.get("/status", response_model=StatusResponse)
def get_status():
    ago, rows_today = _read_duckdb()
    passing, total = _read_test_results()
    status = _pipeline_status(ago, passing, total)
    return StatusResponse(
        last_event_ago_s=ago,
        rows_today=rows_today,
        tests_passing=passing,
        tests_total=total,
        pipeline_status=status,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/healthz")
def healthz():
    return {"ok": True}
