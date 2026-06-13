import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import run_query, apply_custom_style, get_filters, PALETTE, COLOR_SEQ, PLOTLY_BASE

st.set_page_config(page_title="Produits & Catégories — Olist", page_icon="", layout="wide")
apply_custom_style()
where, dates, sel_cats, sel_regs = get_filters()


def add_condition(where: str, condition: str) -> str:
    """Ajoute une condition à une clause WHERE existante ou en crée une."""
    if where.strip():
        return f"{where} AND {condition}"
    return f"WHERE {condition}"


st.title(" Produits & Catégories")
st.markdown(
    "<p style='color:#94a3b8;margin-top:-.5rem'>Identifier les produits moteurs et catégories en déclin</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Row 1 : Top 10 catégories (bar) + Heatmap semaine × catégorie ─────────
col_top, col_heat = st.columns([2, 3])

with col_top:
    st.markdown("###  Top 10 Catégories par Chiffre d'Affaires")
    top_df = run_query(f"""
        SELECT
            Category_Group,
            SUM(total_revenue) AS revenue,
            SUM(quantity)      AS volume
        FROM vw_dashboard
        {where}
        GROUP BY 1
        ORDER BY revenue DESC
        LIMIT 10
    """)
    if not top_df.empty:
        fig = px.bar(
            top_df, x="revenue", y="Category_Group",
            orientation="h",
            color="volume",
            color_continuous_scale=[[0, "#1e3a5f"], [1, "#38bdf8"]],
            labels={"revenue": "CA (R$)", "Category_Group": "", "volume": "Volume"},
            custom_data=["volume"],
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>CA: R$ %{x:,.0f}<br>Volume: %{customdata[0]:,}<extra></extra>"
        )
        fig.update_layout(
            **PLOTLY_BASE,
            yaxis=dict(categoryorder="total ascending"),
            xaxis=dict(gridcolor=PALETTE["border"]),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_heat:
    st.markdown("###  Heatmap Revenue — Semaine × Catégorie")
    heat_where = add_condition(where, "Category_Group IS NOT NULL")
    heat_df = run_query(f"""
        SELECT
            week,
            Category_Group,
            SUM(total_revenue) AS revenue
        FROM vw_dashboard
        {heat_where}
        GROUP BY 1, 2
        ORDER BY 1
    """)
    if not heat_df.empty:
        pivot = heat_df.pivot_table(
            index="Category_Group", columns="week", values="revenue", aggfunc="sum"
        ).fillna(0)
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"S{w}" for w in pivot.columns],
            y=pivot.index.tolist(),
            colorscale="Blues",
            hovertemplate="Catégorie: %{y}<br>Semaine: %{x}<br>CA: R$ %{z:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(showgrid=False, tickfont=dict(size=9)),
            yaxis=dict(showgrid=False),
            height=340,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ── Row 2 : Scatter Prix × Volume + Stacked Bar tranche de prix ───────────
col_scatter, col_stack = st.columns(2)

with col_scatter:
    st.markdown("###  Prix Unitaire vs Volume")
    scat_df = run_query(f"""
        SELECT
            Category_Group,
            AVG(unit_price)    AS avg_price,
            SUM(quantity)      AS total_qty,
            SUM(total_revenue) AS revenue
        FROM vw_dashboard
        {where}
        GROUP BY 1
    """)
    if not scat_df.empty:
        fig = px.scatter(
            scat_df, x="avg_price", y="total_qty",
            color="Category_Group",
            size="revenue",
            size_max=60,
            color_discrete_sequence=COLOR_SEQ,
            labels={
                "avg_price": "Prix Unitaire Moyen (R$)",
                "total_qty": "Volume Total",
                "Category_Group": "Catégorie",
            },
            hover_name="Category_Group",
            custom_data=["revenue"],
        )
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Prix: R$ %{x:.2f}<br>Volume: %{y:,}<br>CA: R$ %{customdata[0]:,.0f}<extra></extra>"
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(gridcolor=PALETTE["border"]),
            yaxis=dict(gridcolor=PALETTE["border"]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_stack:
    st.markdown("###  Répartition par Tranche de Prix × Catégorie")
    tier_where = add_condition(where, "price_tier IS NOT NULL AND Category_Group IS NOT NULL")
    tier_df = run_query(f"""
        SELECT
            price_tier,
            Category_Group,
            SUM(total_revenue) AS revenue
        FROM vw_dashboard
        {tier_where}
        GROUP BY 1, 2
        ORDER BY 1
    """)
    if not tier_df.empty:
        order_map = {"Low": 0, "Medium": 1, "High": 2}
        tier_df["tier_order"] = tier_df["price_tier"].map(order_map)
        tier_df = tier_df.sort_values("tier_order")
        tier_labels = {
            "Low": "Entrée (< 20 R$)",
            "Medium": "Milieu (20–100 R$)",
            "High": "Haut (> 100 R$)",
        }
        tier_df["Gamme"] = tier_df["price_tier"].map(tier_labels)
        fig = px.bar(
            tier_df, x="Category_Group", y="revenue",
            color="Gamme",
            barmode="stack",
            color_discrete_sequence=[PALETTE["green"], PALETTE["blue"], PALETTE["indigo"]],
            labels={"revenue": "CA (R$)", "Category_Group": "Catégorie"},
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(tickangle=-30, showgrid=False),
            yaxis=dict(gridcolor=PALETTE["border"]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ── Row 3 : Tendance multi-ligne par catégorie (top 5) ────────────────────
st.markdown("###  Tendance Mensuelle par Catégorie (Top 5)")

top5 = run_query(f"""
    SELECT Category_Group, SUM(total_revenue) AS rev
    FROM vw_dashboard
    {where}
    GROUP BY 1
    ORDER BY rev DESC
    LIMIT 5
""")

if not top5.empty:
    top5_names = top5["Category_Group"].tolist()
    names_sql = ", ".join(f"'{n}'" for n in top5_names)
    multi_where = add_condition(where, f"Category_Group IN ({names_sql})")
    multi_df = run_query(f"""
        SELECT
            year,
            month,
            Category_Group,
            SUM(total_revenue) AS revenue
        FROM vw_dashboard
        {multi_where}
        GROUP BY 1, 2, 3
        ORDER BY 1, 2
    """)
    if not multi_df.empty:
        multi_df["période"] = (
            multi_df["year"].astype(str) + "-" +
            multi_df["month"].astype(str).str.zfill(2)
        )
        fig = px.line(
            multi_df, x="période", y="revenue",
            color="Category_Group",
            markers=True,
            color_discrete_sequence=COLOR_SEQ,
            labels={"revenue": "CA (R$)", "période": "", "Category_Group": "Catégorie"},
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(showgrid=False, tickangle=-30),
            yaxis=dict(gridcolor=PALETTE["border"]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")
else:
    st.info("Aucune donnée.")