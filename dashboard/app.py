import streamlit as st
import plotly.graph_objects as go
from utils import run_query, apply_custom_style, PALETTE, COLOR_SEQ, PLOTLY_BASE

st.set_page_config(
    page_title="Olist Marketplace Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_style()

# ── Hero ───────────────────────────────────────────────────────────────────
st.title(" Olist Marketplace Analytics")
st.markdown(
    "<p style='color:#94a3b8;font-size:1.05rem;margin-top:-.5rem'>"
    "Pipeline analytique complet sur le dataset Olist Brazilian E-Commerce (2016–2018) "
    "· dbt · DuckDB · Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Global KPIs ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def global_kpis():
    return run_query("""
        SELECT
            SUM(total_revenue)           AS revenue,
            COUNT(DISTINCT order_id)     AS orders,
            AVG(total_revenue)           AS avg_order,
            SUM(quantity)                AS quantity
        FROM vw_dashboard
    """)

kpi = global_kpis()
rev  = kpi["revenue"][0]   or 0
ordr = kpi["orders"][0]    or 0
aov  = kpi["avg_order"][0] or 0
qty  = kpi["quantity"][0]  or 0

c1, c2, c3, c4 = st.columns(4)
c1.metric(" CA Total",         f"R$ {rev:,.0f}")
c2.metric(" Commandes",         f"{ordr:,}")
c3.metric(" Panier Moyen",      f"R$ {aov:.2f}")
c4.metric(" Articles Vendus",   f"{qty:,}")

st.markdown("---")

# ── Navigation cards ───────────────────────────────────────────────────────
st.markdown("###  Modules du Dashboard")

n1, n2, n3, n4 = st.columns(4)

card_style = """
<div style="background:linear-gradient(135deg,#1e293b,#162032);
            border:1px solid #334155; border-radius:16px; padding:20px;
            height:220px; transition:.3s;">
    <div style="font-size:2rem">{icon}</div>
    <div style="font-weight:800;font-size:1rem;color:#f8fafc;margin:.5rem 0">{title}</div>
    <div style="color:#94a3b8;font-size:.85rem;line-height:1.5">{body}</div>
</div>
"""

with n1:
    st.markdown(card_style.format(
        icon="", title="Vue Exécutive",
        body="KPIs globaux, sparklines, évolution mensuelle du CA, carte des régions et répartition par catégorie."
    ), unsafe_allow_html=True)

with n2:
    st.markdown(card_style.format(
        icon="", title="Produits & Catégories",
        body="Top 10 catégories, heatmap semaine×catégorie, scatter prix×volume, stacked bar gamme de prix, tendances multi-lignes."
    ), unsafe_allow_html=True)

with n3:
    st.markdown(card_style.format(
        icon="", title="Saisonnalité",
        body="Heatmap mois×jour, comparaison Year-over-Year, décomposition saisonnière, croissance cumulée."
    ), unsafe_allow_html=True)

with n4:
    st.markdown(card_style.format(
        icon="", title="Géographie",
        body="Carte choroplèthe, ranking régions, bullet AOV vs moyenne, mix catégorie 100%, matrix région×catégorie."
    ), unsafe_allow_html=True)

st.markdown("---")

# ── Stack technique ────────────────────────────────────────────────────────
st.markdown("###  Stack Technique")
s1, s2, s3, s4, s5 = st.columns(5)
for col, icon, label in [
    (s1, "", "Python 3.12"), (s2, "", "DuckDB 1.5"),
    (s3, "", "dbt Core 1.11"), (s4, "", "Streamlit 1.58"),
    (s5, "", "Plotly 6.7"),
]:
    col.markdown(
        f"<div style='text-align:center;background:#1e293b;border:1px solid #334155;"
        f"border-radius:12px;padding:16px;'>"
        f"<div style='font-size:1.8rem'>{icon}</div>"
        f"<div style='color:#94a3b8;font-size:.8rem;font-weight:600;margin-top:.4rem'>{label}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown(
    "<p style='color:#475569;font-size:.8rem;text-align:center'>"
    "Projet réalisé par EL KIHAL KHAOULA · EL HAJOUI MARIAM · HARBOULI HAJAR · OUARADI ASSIYA"
    "</p>",
    unsafe_allow_html=True,
)