"""
Pulse monitor — checks freshness, row volume, and dbt test results every 60s.
Alerts via console + Discord webhook on state transitions only.

Usage:
    DUCKDB_PATH=warehouse/pulse.duckdb python monitor/watch.py

Optional:
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... python monitor/watch.py
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import requests

DUCKDB_PATH = os.getenv("DUCKDB_PATH", "warehouse/pulse.duckdb")
DBT_RUN_RESULTS = os.getenv("DBT_RUN_RESULTS", "transform/target/run_results.json")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

CHECK_INTERVAL_S = 60
FRESHNESS_WARN_S = 300    # 5 min
FRESHNESS_ERROR_S = 900   # 15 min
VOLUME_DROP_PCT = 0.10    # alert if today's rows < 10% of rolling 7-day avg


# ── State ────────────────────────────────────────────────────────────────────

_previous_status: str | None = None   # track transitions


# ── Data collectors ──────────────────────────────────────────────────────────

def _check_duckdb() -> dict:
    try:
        conn = duckdb.connect(DUCKDB_PATH, read_only=True)

        row = conn.execute("SELECT MAX(ingested_at) FROM raw.orders").fetchone()
        last_at = row[0] if row else None

        if last_at is not None:
            if last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=timezone.utc)
            freshness_s = max(0, int((datetime.now(timezone.utc) - last_at).total_seconds()))
        else:
            freshness_s = None

        rows_today = conn.execute(
            "SELECT COUNT(*) FROM raw.orders WHERE cast(ingested_at as date) = current_date"
        ).fetchone()[0]

        avg_7d = conn.execute("""
            SELECT AVG(daily_count) FROM (
                SELECT cast(ingested_at as date) as d, COUNT(*) as daily_count
                FROM raw.orders
                WHERE cast(ingested_at as date) >= current_date - INTERVAL 7 DAY
                GROUP BY d
            )
        """).fetchone()[0] or 0

        conn.close()
        return {"freshness_s": freshness_s, "rows_today": rows_today, "avg_7d": avg_7d}
    except Exception as e:
        return {"freshness_s": None, "rows_today": 0, "avg_7d": 0, "error": str(e)}


def _check_tests() -> dict:
    path = Path(DBT_RUN_RESULTS)
    if not path.exists():
        return {"passing": 0, "total": 0, "available": False}
    try:
        data = json.loads(path.read_text())
        results = data.get("results", [])
        tests = [r for r in results if r.get("unique_id", "").startswith("test.")]
        total = len(tests)
        passing = sum(1 for r in tests if r.get("status") == "pass")
        return {"passing": passing, "total": total, "available": True}
    except Exception:
        return {"passing": 0, "total": 0, "available": False}


# ── Status logic ─────────────────────────────────────────────────────────────

def _compute_status(db: dict, tests: dict) -> tuple[str, list[str]]:
    reasons = []

    if db.get("error"):
        return "DOWN", [f"DuckDB unreachable: {db['error']}"]

    freshness = db["freshness_s"]
    if freshness is None:
        return "DOWN", ["No data in raw.orders — pipeline has never run or table is empty"]

    if freshness > FRESHNESS_ERROR_S:
        reasons.append(f"No new data for {freshness // 60}m {freshness % 60}s (threshold: 15m)")
        return "DOWN", reasons

    if freshness > FRESHNESS_WARN_S:
        reasons.append(f"Data stale — last event {freshness // 60}m ago (warn threshold: 5m)")

    avg = db["avg_7d"]
    today = db["rows_today"]
    if avg > 0 and today < avg * VOLUME_DROP_PCT:
        reasons.append(
            f"Volume drop — {today} rows today vs 7-day avg {avg:.0f} "
            f"(below {VOLUME_DROP_PCT*100:.0f}% threshold)"
        )

    if tests["available"] and tests["total"] > 0:
        failing = tests["total"] - tests["passing"]
        if failing > 0:
            reasons.append(f"{failing} dbt test(s) failing ({tests['passing']}/{tests['total']} passing)")

    return ("DEGRADED" if reasons else "HEALTHY"), reasons


# ── Alerting ─────────────────────────────────────────────────────────────────

_STATUS_EMOJI = {"HEALTHY": "[OK]", "DEGRADED": "[WARN]", "DOWN": "[DOWN]"}
_DISCORD_EMOJI = {"HEALTHY": "✅", "DEGRADED": "⚠️", "DOWN": "\U0001f534"}


def _console_alert(status: str, reasons: list[str], db: dict, tests: dict) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    emoji = _STATUS_EMOJI.get(status, "?")
    lines = [
        f"[{ts}] {emoji} PULSE {status}",
        f"  Freshness : {db.get('freshness_s', 'N/A')}s",
        f"  Rows today: {db.get('rows_today', 0)}",
        f"  Tests     : {tests.get('passing', 0)}/{tests.get('total', 0)} passing",
    ]
    for r in reasons:
        lines.append(f"  >> {r}")
    print("\n".join(lines), flush=True)


def _discord_alert(status: str, reasons: list[str], prev: str | None) -> None:
    if not DISCORD_WEBHOOK_URL:
        return
    emoji = _DISCORD_EMOJI.get(status, "?")
    prev_str = f" (was {prev})" if prev else ""
    body = f"{emoji} **Pulse is {status}**{prev_str}\n"
    if reasons:
        body += "\n".join(f"• {r}" for r in reasons)
    else:
        body += "All checks passing."
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": body}, timeout=5)
    except Exception as e:
        print(f"[monitor] Discord alert failed: {e}", flush=True)


# ── Main loop ────────────────────────────────────────────────────────────────

def check_once() -> str:
    global _previous_status
    db = _check_duckdb()
    tests = _check_tests()
    status, reasons = _compute_status(db, tests)

    if status != _previous_status:
        _console_alert(status, reasons, db, tests)
        _discord_alert(status, reasons, _previous_status)
        _previous_status = status
    else:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(
            f"[{ts}] {status} — "
            f"freshness={db.get('freshness_s', 'N/A')}s "
            f"rows_today={db.get('rows_today', 0)} "
            f"tests={tests.get('passing', 0)}/{tests.get('total', 0)}",
            flush=True,
        )

    return status


def main() -> None:
    print(f"[monitor] starting — checking every {CHECK_INTERVAL_S}s", flush=True)
    print(f"[monitor] DuckDB  : {DUCKDB_PATH}", flush=True)
    print(f"[monitor] Results : {DBT_RUN_RESULTS}", flush=True)
    print(f"[monitor] Discord : {'configured' if DISCORD_WEBHOOK_URL else 'not configured'}", flush=True)

    while True:
        try:
            check_once()
        except Exception as e:
            print(f"[monitor] unexpected error: {e}", flush=True)
        time.sleep(CHECK_INTERVAL_S)


if __name__ == "__main__":
    main()
