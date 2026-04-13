with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

delivery as (
    select * from {{ ref('int_delivery_performance') }}
),

final as (
    select
        o.order_id,
        o.customer_unique_id,
        o.customer_city,
        o.customer_state,
        o.order_status,
        o.ordered_at,
        o.approved_at,
        o.estimated_delivery_at,
        o.delivered_to_customer_at,
        o.total_items,
        o.total_items_price,
        o.total_freight_value,
        o.total_payment_value,
        o.total_payment_installments,
        d.hours_to_carrier,
        d.days_to_deliver,
        d.days_early_or_late
    from orders o
    left join delivery d
        on o.order_id = d.order_id
)

select * from final