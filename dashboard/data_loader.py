import duckdb
import pandas as pd
import streamlit as st
from pathlib import Path

# =====================================
# Configuration
# =====================================

from config import DB_PATH

# =====================================
# Vérification de la base
# =====================================

def check_database():
    """
    Vérifie que la base DuckDB existe.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"""
            Base DuckDB introuvable :

            {DB_PATH}

            Vérifiez le chemin du fichier.
            """
        )

# =====================================
# Connexion DuckDB
# =====================================

def get_connection():
    check_database()
    return duckdb.connect(str(DB_PATH))

# =====================================
# Charger toutes les données dashboard
# =====================================

@st.cache_data
def load_data():

    conn = get_connection()

    query = """
    SELECT *
    FROM vw_dashboard
    """

    df = conn.execute(query).fetchdf()

    conn.close()

    return df

# =====================================
# KPI principaux
# =====================================

@st.cache_data
def load_kpis():

    conn = get_connection()

    query = """
    SELECT
        SUM(total_revenue) AS revenue,
        COUNT(DISTINCT order_id) AS orders,
        AVG(total_revenue) AS avg_order,
        SUM(quantity) AS quantity
    FROM vw_dashboard
    """

    result = conn.execute(query).fetchdf()

    conn.close()

    return result

# =====================================
# Revenue mensuel
# =====================================

@st.cache_data
def monthly_revenue():

    conn = get_connection()

    query = """
    SELECT
        year,
        month,
        SUM(total_revenue) AS revenue
    FROM vw_dashboard
    GROUP BY 1,2
    ORDER BY 1,2
    """

    df = conn.execute(query).fetchdf()

    conn.close()

    return df

# =====================================
# Top catégories
# =====================================

@st.cache_data
def top_categories(limit=10):

    conn = get_connection()

    query = f"""
    SELECT
        category_group,
        SUM(total_revenue) AS revenue
    FROM vw_dashboard
    GROUP BY category_group
    ORDER BY revenue DESC
    LIMIT {limit}
    """

    df = conn.execute(query).fetchdf()

    conn.close()

    return df

# =====================================
# Répartition région
# =====================================

@st.cache_data
def revenue_by_region():

    conn = get_connection()

    query = """
    SELECT
        region,
        SUM(total_revenue) AS revenue
    FROM vw_dashboard
    GROUP BY region
    ORDER BY revenue DESC
    """

    df = conn.execute(query).fetchdf()

    conn.close()

    return df

# =====================================
# Liste catégories
# =====================================

@st.cache_data
def get_categories():

    conn = get_connection()

    query = """
    SELECT DISTINCT category_group
    FROM vw_dashboard
    ORDER BY category_group
    """

    df = conn.execute(query).fetchdf()

    conn.close()

    return df["category_group"].tolist()

# =====================================
# Liste régions
# =====================================

@st.cache_data
def get_regions():

    conn = get_connection()

    query = """
    SELECT DISTINCT region
    FROM vw_dashboard
    ORDER BY region
    """

    df = conn.execute(query).fetchdf()

    conn.close()

    return df["region"].tolist()

# =====================================
# Affichage des tables
# =====================================

def show_tables():

    conn = get_connection()

    tables = conn.execute(
        "SHOW TABLES"
    ).fetchdf()

    conn.close()

    return tables