import duckdb
import pandas as pd
import streamlit as st
from config import DB_PATH


# ─────────────────────────────────────────────
# Connexion DuckDB
# ─────────────────────────────────────────────
def get_connection():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Base de données introuvable : {DB_PATH}")
    return duckdb.connect(str(DB_PATH), read_only=True)


@st.cache_data(ttl=300)
def run_query(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        df = conn.execute(query).fetchdf()
    finally:
        conn.close()
    return df


# ─────────────────────────────────────────────
# STYLE
# ─────────────────────────────────────────────
PALETTE = {
    "blue": "#38bdf8",
    "indigo": "#818cf8",
    "green": "#34d399",
    "red": "#f43f5e",
    "amber": "#fbbf24",
    "purple": "#a78bfa",
    "bg": "#0f172a",
    "card": "#1e293b",
    "border": "#334155",
    "text": "#f8fafc",
    "muted": "#94a3b8",
}

COLOR_SEQ = [
    "#38bdf8", "#818cf8", "#34d399", "#f43f5e",
    "#fbbf24", "#a78bfa", "#06b6d4", "#f97316",
    "#84cc16", "#ec4899",
]

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#f8fafc"),
    margin=dict(t=40, b=30, l=20, r=20),
)


def apply_custom_style():
    st.markdown("""<style> ... ton CSS inchangé ... </style>""",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FILTRES (CORRIGÉ ICI)
# ─────────────────────────────────────────────
def get_filters():
    st.sidebar.markdown("### 🔍 Filtres")

    meta = run_query("SELECT MIN(date) AS mn, MAX(date) AS mx FROM vw_dashboard")
    min_d = pd.to_datetime(meta["mn"][0]).date()
    max_d = pd.to_datetime(meta["mx"][0]).date()

    dates = st.sidebar.date_input(
        "Période",
        value=(min_d, max_d),
        min_value=min_d,
        max_value=max_d
    )

    cats_df = run_query("""
        SELECT DISTINCT Category_Group
        FROM vw_dashboard
        WHERE Category_Group IS NOT NULL
        ORDER BY 1
    """)
    sel_cats = st.sidebar.multiselect(
        "Catégories",
        cats_df["Category_Group"].tolist(),
        default=[]
    )

    reg_df = run_query("""
        SELECT DISTINCT region
        FROM vw_dashboard
        WHERE region IS NOT NULL
        ORDER BY 1
    """)
    sel_regs = st.sidebar.multiselect(
        "Régions",
        reg_df["region"].tolist(),
        default=[]
    )

    # ─────────────────────────────────────────────
    # WHERE SAFE BUILDER (IMPORTANT)
    # ─────────────────────────────────────────────
    clauses = []

    if isinstance(dates, (list, tuple)) and len(dates) == 2:
        clauses.append(f"date BETWEEN '{dates[0]}' AND '{dates[1]}'")

    if sel_cats:
        cats = ", ".join(f"'{c}'" for c in sel_cats)
        clauses.append(f"category_group IN ({cats})")

    if sel_regs:
        regs = ", ".join(f"'{r}'" for r in sel_regs)
        clauses.append(f"region IN ({regs})")

    #  IMPORTANT : toujours commencer vide proprement
    where = ""
    if clauses:
        where = "WHERE " + " AND ".join(clauses)

    return where, dates, sel_cats, sel_regs


# ─────────────────────────────────────────────
# KPI MOM
# ─────────────────────────────────────────────
def compute_mom_growth(where: str) -> float:
    q = f"""
        WITH monthly AS (
            SELECT year, month, SUM(total_revenue) AS rev
            FROM vw_dashboard
            {where}
            GROUP BY 1, 2
            ORDER BY 1 DESC, 2 DESC
            LIMIT 2
        )
        SELECT rev FROM monthly
    """

    df = run_query(q)

    if len(df) < 2:
        return 0.0

    last, prev = df["rev"].iloc[0], df["rev"].iloc[1]

    if prev == 0:
        return 0.0

    return round((last - prev) / prev * 100, 1)