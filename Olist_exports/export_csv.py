import duckdb

conn = duckdb.connect("/Users/macbook/Documents/DBT/My_dbt_project/data/ecommerce.duckdb")

conn.execute("""
COPY dim_date
TO 'dim_date.csv'
(HEADER, DELIMITER ',');
""")

conn.execute("""
COPY dim_product
TO 'dim_product.csv'
(HEADER, DELIMITER ',');
""")

conn.execute("""
COPY dim_region
TO 'dim_region.csv'
(HEADER, DELIMITER ',');
""")

conn.execute("""
COPY dim_payment
TO 'dim_payment.csv'
(HEADER, DELIMITER ',');
""")

conn.execute("""
COPY fact_orders
TO 'fact_orders.csv'
(HEADER, DELIMITER ',');
""")

conn.close()

print("Export terminé.")