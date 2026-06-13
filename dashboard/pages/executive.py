import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import run_query, apply_custom_style, get_filters, compute_mom_growth, PALETTE, COLOR_SEQ, PLOTLY_BASE

st.set_page_config(page_title="Vue Exécutive — Olist", page_icon="", layout="wide")
apply_custom_style()
where, dates, sel_cats, sel_regs = get_filters()

st.title(" Vue Exécutive")
st.markdown("<p style='color:#94a3b8;margin-top:-.5rem'>Lecture instantanée de la santé du business</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ── KPI Cards ──────────────────────────────────────────────────────────────
kpi_df = run_query(f"""
    SELECT
        SUM(total_revenue)           AS revenue,
        COUNT(DISTINCT order_id)     AS orders,
        AVG(total_revenue)           AS avg_order,
        SUM(quantity)                AS quantity
    FROM vw_dashboard {where}
""")

mom = compute_mom_growth(where)

# Sparkline helper — last 30 days trend
def sparkline_fig(series: pd.Series, color: str) -> go.Figure:
    fig = go.Figure(go.Scatter(
        y=series, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=color.replace(")", ",0.15)").replace("rgb", "rgba"),
    ))
    fig.update_layout(
        height=60, margin=dict(t=0, b=0, l=0, r=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig

# 30-day daily series for sparklines
spark_df = run_query(f"""
    SELECT date, SUM(total_revenue) AS rev, COUNT(DISTINCT order_id) AS ord
    FROM vw_dashboard {where}
    GROUP BY date ORDER BY date
""")
spark_df["date"] = pd.to_datetime(spark_df["date"])
last30 = spark_df.tail(30)

rev   = kpi_df["revenue"][0] or 0
ordr  = kpi_df["orders"][0]  or 0
aov   = kpi_df["avg_order"][0] or 0
qty   = kpi_df["quantity"][0] or 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("CA Total", f"R$ {rev:,.0f}", delta=f"{mom:+.1f}% MoM")
    if not last30.empty:
        st.plotly_chart(sparkline_fig(last30["rev"], "#38bdf8"), use_container_width=True)
with c2:
    st.metric("Commandes", f"{ordr:,}")
    if not last30.empty:
        st.plotly_chart(sparkline_fig(last30["ord"], "#818cf8"), use_container_width=True)
with c3:
    st.metric("Panier Moyen", f"R$ {aov:,.2f}")
    if not last30.empty:
        st.plotly_chart(sparkline_fig(last30["rev"] / last30["ord"].replace(0, 1), "#34d399"),
                        use_container_width=True)
with c4:
    st.metric("Articles Vendus", f"{qty:,}")
    if not last30.empty:
        st.plotly_chart(sparkline_fig(last30["ord"], "#fbbf24"), use_container_width=True)

st.markdown("---")

# ── Row 2 : Line Chart CA mensuel  +  Donut catégorie ────────────────────
col_line, col_donut = st.columns([3, 2])

with col_line:
    st.markdown("### Évolution du CA (mensuel)")
    monthly = run_query(f"""
        SELECT year, month, SUM(total_revenue) AS revenue
        FROM vw_dashboard {where}
        GROUP BY 1, 2 ORDER BY 1, 2
    """)
    if not monthly.empty:
        monthly["période"] = (monthly["year"].astype(str) + "-" +
                            monthly["month"].astype(str).str.zfill(2))
        fig = px.line(monthly, x="période", y="revenue",
                    markers=True, color_discrete_sequence=[PALETTE["blue"]],
                    labels={"revenue": "CA (R$)", "période": ""})
        fig.update_layout(**PLOTLY_BASE,
                        xaxis=dict(showgrid=False, tickangle=-30),
                        yaxis=dict(gridcolor=PALETTE["border"]))
        fig.update_traces(line_width=2.5)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée pour la période sélectionnée.")

with col_donut:
    st.markdown("###  CA par Catégorie")
    cat_df = run_query(f"""
        SELECT category_group AS category_group, SUM(total_revenue) AS revenue
        FROM vw_dashboard {where}
        GROUP BY 1 ORDER BY revenue DESC
    """)
    if not cat_df.empty:
        fig = px.pie(cat_df, names="category_group", values="revenue",
                    hole=0.45, color_discrete_sequence=COLOR_SEQ)
        fig.update_layout(**PLOTLY_BASE)
        fig.update_traces(textposition="inside", textinfo="percent+label",
                        textfont_size=11)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ── Row 3 : Carte géographique + Bar catégorie ────────────────────────────
col_map, col_bar = st.columns([3, 2])

with col_map:
    st.markdown("###  Carte — Revenue par Macro-Région")
    # Mapping macro-regions to representative Brazilian state codes for the map
    region_map_df = run_query(f"""
        SELECT region AS region, SUM(total_revenue) AS revenue
        FROM vw_dashboard {where}
        GROUP BY 1 ORDER BY revenue DESC
    """)
    if not region_map_df.empty:
        # Add representative lat/lon for each macro-region
        coords = {
            "Sudeste":      dict(lat=-22.0, lon=-46.0),
            "Sul":          dict(lat=-27.0, lon=-51.0),
            "Nordeste":     dict(lat=-9.0,  lon=-38.0),
            "Centro-Oeste": dict(lat=-15.0, lon=-53.0),
            "Norte":        dict(lat=-4.0,  lon=-63.0),
        }
        region_map_df["lat"] = region_map_df["region"].map(lambda r: coords.get(r, {}).get("lat", 0))
        region_map_df["lon"] = region_map_df["region"].map(lambda r: coords.get(r, {}).get("lon", 0))
        region_map_df["size"] = region_map_df["revenue"] / region_map_df["revenue"].max() * 60 + 10

        fig = px.scatter_geo(
            region_map_df, lat="lat", lon="lon",
            size="size", color="region", hover_name="region",
            hover_data={"revenue": ":,.0f", "lat": False, "lon": False, "size": False},
            scope="south america",
            color_discrete_sequence=COLOR_SEQ,
            labels={"revenue": "CA (R$)"},
            title="",
        )
        fig.update_layout(
            **PLOTLY_BASE,
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                landcolor="#1e293b",
                oceancolor="#0f172a",
                showocean=True,
                showlakes=False,
                coastlinecolor="#334155",
                countrycolor="#334155",
            ),
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_bar:
    st.markdown("###  Classement Catégories")
    if not cat_df.empty:
        fig = px.bar(cat_df.head(8), x="revenue", y="category_group",
                    orientation="h", color="revenue",
                    color_continuous_scale=[[0, "#1e293b"], [1, "#38bdf8"]],
                    labels={"revenue": "CA (R$)", "category_group": ""})
        fig.update_layout(**PLOTLY_BASE,
                        yaxis=dict(categoryorder="total ascending"),
                        xaxis=dict(gridcolor=PALETTE["border"]),
                        showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")