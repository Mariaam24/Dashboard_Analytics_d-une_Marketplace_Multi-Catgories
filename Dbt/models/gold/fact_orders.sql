WITH base AS (

    SELECT *
    FROM {{ source('silver', 'silver_orders') }}

),

date_dim AS (

    SELECT *
    FROM {{ ref('dim_date') }}

),

product_dim AS (

    SELECT *
    FROM {{ ref('dim_product') }}

),

region_dim AS (

    SELECT *
    FROM {{ ref('dim_region') }}

),

payment_dim AS (

    SELECT *
    FROM {{ ref('dim_payment') }}

)

SELECT

    b.order_id,

    d.date_key,

    p.product_key,

    r.region_key,

    pay.payment_key,

    b.quantity,

    b.revenue_prod AS revenue,

    b.unit_price,

    b.total_revenue,

    b.freight

FROM base b

LEFT JOIN date_dim d
    ON b.date = d.full_date

LEFT JOIN product_dim p
    ON b.category = p.category
    AND b.unit_price = p.unit_price

LEFT JOIN region_dim r
    ON b.region = r.region_name
    AND b.region_state = r.region_state

LEFT JOIN payment_dim pay
    ON b.payment_method = pay.payment_method