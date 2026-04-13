with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

final as (
    select
        order_id,
        customer_unique_id,
        customer_city,
        customer_state,
        order_status,
        ordered_at,
        delivered_to_customer_at,
        estimated_delivery_at,

        extract(epoch from (delivered_to_carrier_at - ordered_at)) / 3600
            as hours_to_carrier,

        extract(epoch from (delivered_to_customer_at - ordered_at)) / 86400
            as days_to_deliver,

        extract(epoch from (estimated_delivery_at - delivered_to_customer_at)) / 86400
            as days_early_or_late

    from orders
    where delivered_to_customer_at is not null
)

select * from final