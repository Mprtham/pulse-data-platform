-- Singular test: returns rows on FAILURE (dbt convention).
-- Any day where total revenue is negative means corrupted price data
-- slipped through the staging filter — this should never happen.
select
    revenue_date,
    total_revenue_gbp
from {{ ref('mart_daily_revenue') }}
where total_revenue_gbp < 0
