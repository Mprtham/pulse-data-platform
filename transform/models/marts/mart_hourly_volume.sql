with orders as (
    select * from {{ ref('stg_orders') }}
),

hourly as (
    select
        cast(invoice_date as date)                              as event_date,
        datepart('hour', invoice_date)                          as hour_of_day,
        count(distinct invoice_no)                              as order_count,
        count(distinct customer_id)                             as unique_customers,
        round(sum(line_total_gbp), 2)                          as total_revenue_gbp
    from orders
    group by
        cast(invoice_date as date),
        datepart('hour', invoice_date)
)

select * from hourly
order by event_date desc, hour_of_day desc
