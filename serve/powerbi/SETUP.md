# Power BI Report — Build Guide

## Prerequisites
- Power BI Desktop (March 2024 or later — required for PBIP save format)
- Python 3.10+ with `duckdb` installed

## Step 1 — Export marts to Parquet

Run once before opening Power BI (and again any time you want fresh data):

```bash
python serve/powerbi/export_parquet.py
```

This writes three files to `serve/powerbi/data/`:

| File | Contents |
|---|---|
| `mart_daily_revenue.parquet` | Daily revenue, order count, avg order value |
| `mart_hourly_volume.parquet` | Hourly order count and revenue |
| `raw_quality_summary.parquet` | Daily data-quality scorecard (valid %, fault counts) |

## Step 2 — Load data into Power BI Desktop

1. Open Power BI Desktop.
2. **Home → Get Data → Parquet**.
3. Load each of the three files above as separate tables.
4. In the **Transform Data** editor:
   - On `mart_daily_revenue`: set `revenue_date` type to **Date**.
   - On `mart_hourly_volume`: set `event_date` to **Date**, `hour_of_day` to **Whole Number**.
   - On `raw_quality_summary`: set `ingest_date` to **Date**.
5. **Close & Apply**.

## Step 3 — Apply the Deep Signal theme

1. **View → Themes → Browse for themes**.
2. Load `serve/powerbi/DeepSignal.json` (see colour tokens below).

Paste this into a new file `DeepSignal.json` in this folder:

```json
{
  "name": "Deep Signal",
  "dataColors": ["#06B6D4","#10B981","#F59E0B","#F43F5E","#8B5CF6","#EC4899"],
  "background": "#0F172A",
  "foreground": "#F1F5F9",
  "tableAccent": "#06B6D4"
}
```

## Step 4 — Build report pages

### Page 1: Revenue Trend

| Visual | Fields |
|---|---|
| **Line chart** | X-axis: `revenue_date`, Y-axis: `total_revenue_gbp`, Tooltip: `order_count`, `avg_order_value_gbp` |
| **Card** | `total_revenue_gbp` (sum, formatted as £#,##0.00) — title: "Total Revenue" |
| **Card** | `order_count` (sum) — title: "Total Orders" |
| **Card** | `unique_customers` (sum) — title: "Unique Customers" |

Page title: **Revenue Trend** | Canvas background: `#0F172A` | Visual backgrounds: `#1E293B`

### Page 2: Hourly Volume

| Visual | Fields |
|---|---|
| **Clustered bar chart** | Y-axis: `hour_of_day`, X-axis: `order_count`, colour: `#06B6D4` |
| **Line chart** | X-axis: `hour_of_day`, Y-axis: `total_revenue_gbp` |
| **Slicer** | `event_date` (between) |

Page title: **Order Volume by Hour**

### Page 3: Data Quality Scorecard

| Visual | Fields |
|---|---|
| **Card** | `pct_valid` (last value) — title: "% Valid Rows", format: `0.00%`, conditional: green ≥ 95, amber 80–95, red < 80 |
| **Card** | `missing_invoice` (sum) — title: "Missing Invoice No." |
| **Card** | `negative_price` (sum) — title: "Negative Price Rows" |
| **Card** | `null_quantity` (sum) — title: "Null Quantity Rows" |
| **Clustered bar chart** | X-axis: `ingest_date`, Y-axis: `valid_invoice` vs `missing_invoice` (stacked) |

Page title: **Data Quality**

Talking point for interviews: *"This page is the governance story — it shows exactly how many bad rows were caught before they reached the revenue figures, and it trends over time so stakeholders can see the platform getting cleaner."*

## Step 5 — Format to match the Deep Signal palette

Apply these settings globally (**View → Format**):

| Setting | Value |
|---|---|
| Canvas background | `#0F172A` |
| Visual background | `#1E293B` |
| Visual border | `#334155`, 1 px |
| Font (titles) | Space Grotesk, 14 pt, `#F1F5F9` |
| Font (values) | JetBrains Mono, 20 pt, `#F1F5F9` |
| Font (labels) | Inter, 10 pt, `#94A3B8` |

## Step 6 — Save as PBIP

1. **File → Save As → Power BI Project (.pbip)**.
2. Save into `serve/powerbi/PulseReport.pbip` — this overwrites the skeleton already in git.
3. The `PulseReport.Report/` and `PulseReport.SemanticModel/` folders become JSON-diffable files.
4. `git add serve/powerbi/PulseReport.pbip serve/powerbi/PulseReport.Report serve/powerbi/PulseReport.SemanticModel`
5. Commit: `feat: add Power BI executive report (PBIP)`

## What NOT to commit

`serve/powerbi/data/*.parquet` is in `.gitignore`. Reviewers run `export_parquet.py` locally to regenerate them.

## Interview talking points

- *"I version-control the semantic model as JSON in git, so the data model is as reviewable as code."*
- *"The report reads from governed dbt marts — if a dbt test fails, the Parquet export won't contain the bad data."*
- *"The quality scorecard page gives stakeholders a daily view of data trustworthiness — they can see exactly how many bad rows were blocked."*
