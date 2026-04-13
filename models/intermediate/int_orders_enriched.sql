with orders as (
    select * from {{ ref('stg_orders') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

order_payments as (
    select * from {{ ref('stg_order_payments') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

payment_aggregated as (
    select
        order_id,
        sum(payment_value)        as total_payment_value,
        count(payment_sequential) as total_payment_installments
    from order_payments
    group by order_id
),

items_aggregated as (
    select
        order_id,
        count(order_item_id)  as total_items,
        sum(price)            as total_items_price,
        sum(freight_value)    as total_freight_value
    from order_items
    group by order_id
),

final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        c.city                        as customer_city,
        c.state                       as customer_state,
        o.order_status,
        o.ordered_at,
        o.approved_at,
        o.delivered_to_carrier_at,
        o.delivered_to_customer_at,
        o.estimated_delivery_at,
        i.total_items,
        i.total_items_price,
        i.total_freight_value,
        p.total_payment_value,
        p.total_payment_installments
    from orders o
    left join customers c
        on o.customer_id = c.customer_id
    left join items_aggregated i
        on o.order_id = i.order_id
    left join payment_aggregated p
        on o.order_id = p.order_id
)

select * from final