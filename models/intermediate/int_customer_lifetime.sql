with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

final as (
    select
        customer_unique_id,
        count(order_id)                                    as total_orders,
        sum(total_payment_value)                           as lifetime_value,
        avg(total_payment_value)                           as avg_order_value,
        min(ordered_at)                                    as first_order_at,
        max(ordered_at)                                    as last_order_at,
        sum(total_items)                                   as total_items_purchased
    from orders
    group by customer_unique_id
)

select * from final