WITH regions AS (

    SELECT DISTINCT
        region,
        region_state
    FROM {{ source('silver', 'silver_orders') }}

)

SELECT

    ROW_NUMBER() OVER () AS region_key,

    region AS region_name,

    region_state,

    CASE
        WHEN region IN ('Sudeste', 'Sul')
        THEN 'South'

        ELSE 'North'
    END AS zone

FROM regions