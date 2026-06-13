"""
data_loader.py
Chargement sécurisé des données depuis DuckDB.
"""

import os
import duckdb
import pandas as pd
import streamlit as st

from config import DB_PATH

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:

    print("DB PATH =", DB_PATH)

    # =====================================================
    # Vérification fichier
    # =====================================================

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"DuckDB introuvable : {DB_PATH}"
        )

    # =====================================================
    # Connexion
    # =====================================================

    con = duckdb.connect(DB_PATH, read_only=True)

    # =====================================================
    # Vérification tables
    # =====================================================

    tables = con.execute(
        "SHOW TABLES"
    ).fetchall()

    print("\n=== TABLES ===")
    print(tables)

    # =====================================================
    # QUERY PRINCIPALE
    # =====================================================

    query = """
        SELECT
            f.order_id,

            d.date_key              AS date,
            d.year,
            d.month,
            d.quarter,
            d.week_number           AS week,
            d.day_name              AS day_of_week,
            d.is_weekend,
            d.year_month,

            f.quantity,
            f.unit_price,
            f.revenue_products      AS revenue_prod,
            f.total_revenue,
            f.freight_value         AS freight,

            dp.category,
            dp.category_group,
            dp.price_tier,

            dr.region_name          AS region,
            dr.state_code           AS region_state,
            dr.country,

            pm.payment_method,
            pm.payment_type

        FROM fact_orders f

        LEFT JOIN dim_date d
            ON f.date_key = d.date_key

        LEFT JOIN dim_product dp
            ON f.product_key = dp.product_key

        LEFT JOIN dim_region dr
            ON f.region_key = dr.region_key

        LEFT JOIN dim_payment pm
            ON f.payment_key = pm.payment_key
    """

    df = con.execute(query).df()

    con.close()

    # =====================================================
    # DATE
    # =====================================================

    df["date"] = pd.to_datetime(df["date"])

    # =====================================================
    # DEBUG
    # =====================================================

    print("\n=== DF SHAPE ===")
    print(df.shape)

    print("\n=== COLONNES ===")
    print(df.columns.tolist())

    return df


# =========================================================
# FILTER DATA
# =========================================================

def filter_data(
    df,
    years,
    regions,
    groups,
    payments
):

    mask = (
        (df["year"].isin(years))
        &
        (df["region"].isin(regions))
        &
        (df["category_group"].isin(groups))
        &
        (df["payment_method"].isin(payments))
    )

    return df.loc[mask]