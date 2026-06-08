"""
data_loader.py — Chargement depuis DuckDB schéma en étoile.
"""

import duckdb
import pandas as pd
import streamlit as st
from config import DB_PATH


@st.cache_data
def load_data() -> pd.DataFrame:
    conn = duckdb.connect(DB_PATH)

    df = conn.execute("""
        SELECT
            f.order_id,
            f.quantity,
            f.price          AS unit_price,
            f.revenue        AS revenue_prod,
            f.total_revenue,
            f.freight,
            d.Date           AS date,
            d.year,
            d.month,
            d.month_name,
            d.quarter,
            d.week,
            d.day_name       AS day_of_week,
            d.is_weekend,
            p.product_name   AS category,
            p.category       AS category_group,
            p.price_tier,
            r.region_name    AS region,
            r.zone           AS region_state,
            r.continent,
            pm.payment_method,
            pm.payment_type
        FROM main.fact_orders f
        JOIN main.dim_date    d  ON f.date_key    = d.date_key
        JOIN main.dim_product p  ON f.product_key = p.product_key
        JOIN main.dim_region  r  ON f.region_key  = r.region_key
        JOIN main.dim_payment pm ON f.payment_key = pm.payment_key
    """).df()

    conn.close()

    # colonnes calculées supplémentaires
    df['date']       = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.strftime('%Y-%m')

    return df


def filter_data(df, years, regions, groups, payments) -> pd.DataFrame:
    mask = (
        (df['year'].isin(years))          &
        (df['region'].isin(regions))      &
        (df['category_group'].isin(groups)) &
        (df['payment_method'].isin(payments))
    )
    return df[mask]