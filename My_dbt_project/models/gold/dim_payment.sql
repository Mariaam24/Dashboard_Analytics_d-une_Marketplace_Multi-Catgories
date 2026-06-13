WITH payments AS (

    SELECT DISTINCT
        payment_method
    FROM {{ source('silver', 'silver_orders') }}

)

SELECT

    ROW_NUMBER() OVER () AS payment_key,

    payment_method,

    CASE
        WHEN payment_method = 'credit_card'
        THEN 'Card'

        WHEN payment_method = 'debit_card'
        THEN 'Card'

        WHEN payment_method = 'voucher'
        THEN 'Voucher'

        ELSE 'Bank Transfer'
    END AS payment_type

FROM payments