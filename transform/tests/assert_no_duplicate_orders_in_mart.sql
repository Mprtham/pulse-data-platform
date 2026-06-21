-- Singular test: returns rows on FAILURE.
-- Each revenue_date must appear exactly once.
-- A duplicate would indicate a broken GROUP BY or a schema collision.
select
    revenue_date,
    count(*) as n
from {{ ref('mart_daily_revenue') }}
group by revenue_date
having count(*) > 1
