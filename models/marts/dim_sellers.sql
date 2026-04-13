with sellers as (
    select * from {{ ref('stg_sellers') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

seller_metrics as (
    select
        oi.seller_id,
        count(distinct oi.order_id)   as total_orders,
        sum(oi.price)                 as total_revenue,
        avg(oi.price)                 as avg_item_price,
        sum(oi.freight_value)         as total_freight_value,
        count(oi.order_item_id)       as total_items_sold
    from order_items oi
    inner join orders o
        on oi.order_id = o.order_id
    where o.order_status = 'delivered'
    group by oi.seller_id
),

final as (
    select
        s.seller_id,
        s.city                        as seller_city,
        s.state                       as seller_state,
        m.total_orders,
        m.total_revenue,
        m.avg_item_price,
        m.total_freight_value,
        m.total_items_sold
    from sellers s
    inner join seller_metrics m
        on s.seller_id = m.seller_id
)

select * from final