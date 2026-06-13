WITH dates AS (

    SELECT DISTINCT
        date AS full_date
    FROM {{ source('silver', 'silver_orders') }}

)

SELECT
    TO_CHAR(full_date, 'YYYYMMDD')::INTEGER AS date_key,

    full_date,

    EXTRACT(YEAR FROM full_date) AS year,
    EXTRACT(MONTH FROM full_date) AS month,
    EXTRACT(QUARTER FROM full_date) AS quarter,
    EXTRACT(WEEK FROM full_date) AS week,

    TO_CHAR(full_date, 'Day') AS day_name,

    CASE
        WHEN EXTRACT(ISODOW FROM full_date) IN (6,7)
        THEN TRUE
        ELSE FALSE
    END AS is_weekend

FROM dates