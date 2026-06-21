with source as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        invoice_no,
        stock_code,
        upper(trim(description))                      as description,
        quantity,
        cast(invoice_date as timestamp)               as invoice_date,
        cast(invoice_date as date)                    as invoice_date_day,
        unit_price,
        round(quantity * unit_price, 2)               as line_total_gbp,
        coalesce(upper(trim(customer_id)), 'GUEST')   as customer_id,
        upper(trim(country))                          as country,
        ingested_at
    from source
    -- drop rows where the natural key is missing — these are injected faults
    where invoice_no is not null
      and quantity   is not null
)

select * from cleaned
