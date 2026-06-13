WITH products AS (

    SELECT DISTINCT
        category,
        category_group,
        unit_price
    FROM {{ source('silver', 'silver_orders') }}

)

SELECT

    ROW_NUMBER() OVER () AS product_key,

    category,

    category_group,

    CASE
        WHEN unit_price < 20 THEN 'Low'
        WHEN unit_price BETWEEN 20 AND 100 THEN 'Medium'
        ELSE 'High'
    END AS price_tier

FROM products