with products as (
    select * from {{ ref('stg_products') }}
),

translations as (
    select * from {{ ref('stg_product_category_translations') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

product_metrics as (
    select
        product_id,
        count(distinct order_id)   as total_orders,
        sum(price)                 as total_revenue,
        avg(price)                 as avg_price,
        sum(freight_value)         as total_freight_value,
        count(order_item_id)       as total_units_sold
    from order_items
    group by product_id
),

final as (
    select
        p.product_id,
        p.category_name,
        coalesce(t.category_name_english, p.category_name, 'unknown') as category_name_english,
        p.weight_g,
        p.length_cm,
        p.height_cm,
        p.width_cm,
        p.photos_qty,
        m.total_orders,
        m.total_revenue,
        m.avg_price,
        m.total_freight_value,
        m.total_units_sold
    from products p
    left join translations t
        on p.category_name = t.category_name
    left join product_metrics m
        on p.product_id = m.product_id
)

select * from final