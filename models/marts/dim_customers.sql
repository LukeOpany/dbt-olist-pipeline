with customers as (
    select * from {{ ref('stg_customers') }}
),

lifetime as (
    select * from {{ ref('int_customer_lifetime') }}
),

final as (
    select
        c.customer_unique_id,
        c.city                        as customer_city,
        c.state                       as customer_state,
        l.total_orders,
        l.lifetime_value,
        l.avg_order_value,
        l.first_order_at,
        l.last_order_at,
        l.total_items_purchased
    from customers c
    inner join lifetime l
        on c.customer_unique_id = l.customer_unique_id
)

select * from final