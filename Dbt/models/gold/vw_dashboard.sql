{{ config(materialized='view') }}

WITH fact AS (
    SELECT * FROM {{ ref('fact_orders') }}
),
dim_d AS (
    SELECT * FROM {{ ref('dim_date') }}
),
dim_p AS (
    SELECT * FROM {{ ref('dim_product') }}
),
dim_r AS (
    SELECT * FROM {{ ref('dim_region') }}
),
dim_pay AS (
    SELECT * FROM {{ ref('dim_payment') }}
)

SELECT
    f.order_id,
    f.quantity,
    f.revenue,
    f.unit_price,
    f.total_revenue,
    f.freight,
    d.full_date AS date,
    d.year,
    d.month,
    d.quarter,
    d.week,
    d.day_name,
    d.is_weekend,
    p.category,
    p.category_group,
    p.price_tier,
    r.region_name AS region,
    r.region_state,
    r.zone,
    pay.payment_method,
    pay.payment_type
FROM fact f
LEFT JOIN dim_d d ON f.date_key = d.date_key
LEFT JOIN dim_p p ON f.product_key = p.product_key
LEFT JOIN dim_r r ON f.region_key = r.region_key
LEFT JOIN dim_pay pay ON f.payment_key = pay.payment_key
