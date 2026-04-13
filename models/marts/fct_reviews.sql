with reviews as (
    select * from {{ ref('stg_order_reviews') }}
),

orders as (
    select * from {{ ref('fct_orders') }}
),

final as (
    select
        r.review_id,
        r.order_id,
        o.customer_unique_id,
        o.customer_city,
        o.customer_state,
        o.total_payment_value,
        o.days_to_deliver,
        o.days_early_or_late,
        r.review_score,
        r.comment_title,
        r.comment_message,
        r.created_at                  as review_created_at,
        r.answered_at                 as review_answered_at
    from reviews r
    left join orders o
        on r.order_id = o.order_id
)

select * from final