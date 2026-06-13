WITH dates AS (

    SELECT DISTINCT
        date AS full_date
    FROM {{ source('silver', 'silver_orders') }}

)

SELECT
    CAST(strftime(full_date, '%Y%m%d') AS INTEGER) AS date_key,

    full_date,

    EXTRACT(year FROM full_date) AS year,
    EXTRACT(month FROM full_date) AS month,
    EXTRACT(quarter FROM full_date) AS quarter,
    EXTRACT(week FROM full_date) AS week,

    strftime(full_date, '%A') AS day_name,

    CASE
        WHEN EXTRACT(dow FROM full_date) IN (6, 0)
        THEN TRUE
        ELSE FALSE
    END AS is_weekend

FROM dates