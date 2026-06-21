# Case Study: Pulse — Real-Time Data Platform

**Author:** Prathamesh Mishra
**Stack:** Redpanda · DuckDB · dbt · Python · FastAPI · Vite+React · Docker · GitHub Actions · Power BI (PBIP)
**Repo:** `pulse-data-platform`

---

## For a non-technical reader

### What is this?

Pulse is a live data system built to answer one question:

> *How do you make sure the number in a board report is actually right?*

Most data platforms move data from A to B and hope for the best. Pulse is different: it checks every piece of data as it arrives, blocks the broken pieces before they reach any report, and raises an alarm the moment something goes wrong — automatically, without anyone having to look.

### The problem it solves (in UK business terms)

Imagine a retailer whose daily revenue figure in Monday's board pack is wrong because a batch of orders came through with negative prices — a data entry error that nobody noticed. The board makes a pricing decision based on that number. That decision costs money.

This is not a hypothetical. The [IBM Cost of Bad Data report](https://www.ibm.com/downloads/cas/GBMJZ5BQ) estimated poor data quality costs UK organisations billions annually. GDPR adds a compliance dimension: if customer data is processed incorrectly due to bad pipeline hygiene, that is a regulatory risk, not just a reporting inconvenience.

Pulse makes that class of error **structurally impossible**:

- A negative price is caught by an automated test before it reaches the revenue table.
- A missing order ID is filtered at the cleaning stage and never aggregated.
- If the pipeline itself goes quiet — no data arriving for five minutes — an alarm fires.

The business can look at the dashboard and trust it, because the platform refuses to show anything it cannot verify.

### What you can see running

Open `http://localhost:5173` after `docker compose up`. You will see:

- **Last event** — how many seconds ago the most recent order arrived (updates every 5 s)
- **Rows today** — how many order events have landed in the warehouse today
- **Tests passing** — how many of the automated quality checks are currently green
- **Pipeline status** — HEALTHY / DEGRADED / DOWN, with a colour change and an alert when state changes

Stop the event generator and watch the status flip to DEGRADED, then DOWN. Restart it and watch it recover. That is the reliability story in thirty seconds.

### Power BI

A Power BI executive report connects to the governed marts (daily revenue, hourly volume, and a data-quality scorecard). The semantic model is version-controlled in git as a PBIP project. To build and open the report: follow `serve/powerbi/SETUP.md`.

---

## For a senior engineer

### Architecture

```
[Python generator]  →  [Redpanda: orders.raw]  →  [Python consumer]  →  [DuckDB: raw.orders]
     ~15% faults          Kafka-API, 1 broker         micro-batch             append-only
         |                                                 |
         |                                         [dbt: staging → marts]
         |                                          view + table models
         |                                          23 schema tests
         |                                          2 custom singular tests
         |                                          source freshness
         |                                          2 exposures (lineage)
         |                                                 |
         |                              ┌──────────────────┤
         |                              |                  |
         |                    [FastAPI /status]    [Power BI PBIP]
         |                    [Vite+React page]    (see SETUP.md)
         |                              |
         └──────────── [Python monitor: 60s checks → console + Discord]
                       [GitHub Actions: dbt build on push → blocks failures]
```

### Fault injection — what's injected and what catches it

`generator/faults.py` corrupts approximately 15% of events at the producer, before they enter the Kafka topic. Four fault types:

| Fault | How injected | Where caught |
|---|---|---|
| `invoice_no = NULL` | `faults.py` sets key to `None` | `stg_orders.sql` `WHERE invoice_no IS NOT NULL` — row never reaches staging |
| `unit_price < 0` | `faults.py` negates the price | `assert_revenue_non_negative.sql` — custom singular test fails if any mart day has negative total revenue |
| `quantity = NULL` | `faults.py` sets quantity to `None` | `stg_orders.sql` `WHERE quantity IS NOT NULL` — row dropped at staging |
| Duplicate `invoice_no` | `faults.py` replaces with a recent ID from a 200-item rolling window | `unique_stg_orders_invoice_no` schema test — surfaces duplicates in staging |

The null-invoice and null-quantity faults are silently dropped by the staging WHERE clause — they never appear in the marts and generate no noise. The negative-price fault is designed to surface in the mart so the custom test fires visibly during a demo.

### dbt project structure

```
transform/
├── models/
│   ├── staging/
│   │   ├── sources.yml          # raw.orders declared; freshness warn=5m error=15m
│   │   ├── stg_orders.sql       # materialized: view; casts, renames, null filter
│   │   └── stg_orders.yml       # 12 column tests (not_null, unique, accepted_values)
│   ├── marts/
│   │   ├── mart_daily_revenue.sql    # materialized: table; GROUP BY date
│   │   ├── mart_daily_revenue.yml    # 6 column tests
│   │   ├── mart_hourly_volume.sql    # materialized: table; GROUP BY hour
│   │   ├── mart_hourly_volume.yml    # 4 column tests
│   └── exposures.yml            # pulse_executive_report + pulse_status_page
├── tests/
│   ├── assert_revenue_non_negative.sql       # custom: returns rows on failure
│   └── assert_no_duplicate_orders_in_mart.sql
├── seeds/
│   └── orders.csv               # 10 clean rows; CI fixture for in-memory build
└── macros/
    └── generate_schema_name.sql  # exact schema names (raw / staging / marts)
```

**Test coverage at a glance:**
- 12 column tests on `stg_orders` (not_null × 8, unique × 1, accepted_values × 1 on country)
- 6 column tests on `mart_daily_revenue`
- 4 column tests on `mart_hourly_volume`
- 1 custom singular test: `assert_revenue_non_negative`
- 1 custom singular test: `assert_no_duplicate_orders_in_mart`
- Source freshness: warn after 5 min, error after 15 min

`dbt build` on clean seed data: **PASS=27 WARN=0 ERROR=0** (1 seed + 3 models + 23 tests).
`dbt build` against live data with fault injection active: the `assert_revenue_non_negative` test fails — which is the intended behaviour. The CI run uses clean seed data and must be fully green.

### Lineage via exposures

`transform/models/exposures.yml` declares:

```yaml
exposures:
  - name: pulse_executive_report
    type: dashboard
    depends_on:
      - ref('mart_daily_revenue')
      - ref('mart_hourly_volume')

  - name: pulse_status_page
    type: application
    depends_on:
      - ref('mart_daily_revenue')
      - ref('mart_hourly_volume')
```

This means `dbt docs generate` produces a lineage graph from `raw.orders` → `stg_orders` → both marts → both downstream consumers. If a mart model breaks, the graph shows immediately which surfaces are affected.

### CI gate

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

1. Install `dbt-duckdb`
2. `dbt build --target ci --profiles-dir .`
   - Target `ci` uses `CI_DUCKDB_PATH=/tmp/pulse_ci.duckdb`
   - `dbt build` includes the seed step — no separate `dbt seed` required
   - Seeds populate `raw.orders`; models build on top; all 27 artefacts tested in one command
3. Upload `transform/target/` as a GitHub Actions artifact (run results visible in the UI)
4. Non-zero exit = workflow fails = merge blocked

The CI seed is clean by design. The fault-injection story is a runtime property of the live generator, not a CI failure. The CI gate proves the *platform* is sound; the monitor proves the *pipeline* is healthy.

### Monitor

`monitor/watch.py` runs every 60 seconds and computes one of three states:

| State | Condition |
|---|---|
| `HEALTHY` | Freshness < 5 min AND all dbt tests passing (if results available) |
| `DEGRADED` | Freshness 5–15 min OR ≥1 dbt test failing OR today's row volume < 10% of 7-day average |
| `DOWN` | Freshness > 15 min OR no rows in `raw.orders` at all |

Alerts fire **only on state transitions**, not every tick — avoiding Discord spam during a sustained outage. The Discord webhook URL is optional (passed via environment variable).

### Design decisions worth defending in an interview

**Why Redpanda instead of Kafka?**
Redpanda is Kafka-API compatible and runs as a single binary/container with no ZooKeeper dependency. For a portfolio project that must run on a laptop with `docker compose up`, it is strictly better. Any code written against it works against a production Kafka cluster unchanged.

**Why DuckDB instead of BigQuery/Snowflake?**
The brief required £0 and no cloud account. DuckDB's analytical SQL dialect is close enough to BigQuery that the dbt models would require minimal changes to run against either. More importantly, any reviewer can clone and run this in under five minutes with no credentials.

**Why dbt-duckdb?**
dbt is the analytics engineering standard. The dbt Fundamentals certification is already held. Using dbt-duckdb means the same SQL models, tests, and exposure declarations that run locally would run against BigQuery or Snowflake with only a profile change. The governance story is portable.

**Why exact schema names via `generate_schema_name`?**
The default dbt-DuckDB behaviour prefixes custom schemas with the target schema name (e.g. `raw` becomes `main_raw`). Overriding the macro means `raw`, `staging`, and `marts` are exact — the same names in CI, dev, and Docker. This makes the SQL in application code (`raw.orders`, `marts.mart_daily_revenue`) consistent across environments.

**Why PBIP over PBIX for Power BI?**
PBIP saves the report definition as JSON files, making the semantic model reviewable in a pull request diff. A PBIX binary is opaque — you cannot `git diff` it meaningfully. Committing the PBIP skeleton means the project structure is in version control even before the report visuals are built.

---

*Built by Prathamesh Mishra. Synthetic data only.*
