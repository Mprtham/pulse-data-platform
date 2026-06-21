with orders as (
    select * from {{ ref('stg_orders') }}
),

daily as (
    select
        invoice_date_day                        as revenue_date,
        count(distinct invoice_no)              as order_count,
        count(distinct customer_id)             as unique_customers,
        round(sum(line_total_gbp), 2)           as total_revenue_gbp,
        round(avg(line_total_gbp), 2)           as avg_order_value_gbp,
        min(invoice_date)                       as first_order_at,
        max(invoice_date)                       as last_order_at
    from orders
    group by invoice_date_day
)

select * from daily
order by revenue_date desc
