import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import run_query, apply_custom_style, get_filters, PALETTE, COLOR_SEQ, PLOTLY_BASE

st.set_page_config(page_title="Performance Géographique — Olist", page_icon="", layout="wide")
apply_custom_style()
where, dates, sel_cats, sel_regs = get_filters()

st.title(" Performance Géographique")
st.markdown("<p style='color:#94a3b8;margin-top:-.5rem'>Identifier les marchés prioritaires et zones sous-performantes</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ── Load regional data ─────────────────────────────────────────────────────
region_df = run_query(f"""
    SELECT
        region AS region,
        SUM(total_revenue)       AS revenue,
        COUNT(DISTINCT order_id) AS orders,
        AVG(total_revenue)       AS aov,
        SUM(freight)             AS freight
    FROM vw_dashboard {where}
    GROUP BY 1
    ORDER BY revenue DESC
""")

global_aov = region_df["aov"].mean() if not region_df.empty else 0

# ── Row 1 : Carte choroplèthe + Ranking ───────────────────────────────────
col_map, col_rank = st.columns([3, 2])

with col_map:
    st.markdown("###  Carte Choroplèthe — Revenue par Macro-Région")
    if not region_df.empty:
        # Bubble map with representative coordinates per region
        coords = {
            "Sudeste":      dict(lat=-22.0, lon=-46.0),
            "Sul":          dict(lat=-27.0, lon=-51.0),
            "Nordeste":     dict(lat=-9.0,  lon=-38.0),
            "Centro-Oeste": dict(lat=-15.0, lon=-53.0),
            "Norte":        dict(lat=-4.0,  lon=-63.0),
        }
        region_df["lat"] = region_df["region"].map(lambda r: coords.get(r, {}).get("lat", 0))
        region_df["lon"] = region_df["region"].map(lambda r: coords.get(r, {}).get("lon", 0))

        fig = px.scatter_geo(
            region_df, lat="lat", lon="lon",
            color="revenue",
            size="revenue",
            size_max=70,
            hover_name="region",
            scope="south america",
            color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#0284c7"], [1, "#38bdf8"]],
            hover_data={"revenue": ":,.0f", "orders": ":,", "aov": ":.2f",
                        "lat": False, "lon": False},
            labels={"revenue": "CA (R$)", "orders": "Commandes", "aov": "Panier Moyen"},
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
                showcoastlines=True,
                showcountries=True,
            ),
            height=420,
            coloraxis_colorbar=dict(title="CA (R$)", tickfont=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_rank:
    st.markdown("###  Classement des Régions par Revenue")
    if not region_df.empty:
        fig = px.bar(
            region_df, x="revenue", y="region",
            orientation="h",
            color="revenue",
            color_continuous_scale=[[0, "#1e3a5f"], [1, "#38bdf8"]],
            text=region_df["revenue"].apply(lambda x: f"R$ {x/1e6:.1f}M"),
            labels={"revenue": "CA (R$)", "region": ""},
        )
        fig.update_traces(textposition="outside", textfont_size=12)
        fig.update_layout(
            **PLOTLY_BASE,
            yaxis=dict(categoryorder="total ascending"),
            xaxis=dict(showgrid=False, showticklabels=False),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Résumé chiffré
    if not region_df.empty:
        st.markdown("** Résumé par Région**")
        display_df = region_df[["region", "revenue", "orders", "aov"]].copy()
        display_df.columns = ["Région", "CA Total (R$)", "Commandes", "Panier Moyen (R$)"]
        display_df["CA Total (R$)"]     = display_df["CA Total (R$)"].map(lambda x: f"R$ {x:,.0f}")
        display_df["Commandes"]         = display_df["Commandes"].map(lambda x: f"{x:,}")
        display_df["Panier Moyen (R$)"] = display_df["Panier Moyen (R$)"].map(lambda x: f"R$ {x:.2f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Row 2 : Bullet AOV + Stacked 100% mix catégorie ─────────────────────
col_bullet, col_stack = st.columns(2)

with col_bullet:
    st.markdown("###  Panier Moyen par Région vs Moyenne Globale")
    if not region_df.empty:
        fig = go.Figure()
        for _, row in region_df.iterrows():
            color = PALETTE["green"] if row["aov"] >= global_aov else PALETTE["red"]
            fig.add_trace(go.Bar(
                x=[row["aov"]], y=[row["region"]],
                orientation="h",
                marker_color=color,
                name=row["region"],
                hovertemplate=f"<b>{row['region']}</b><br>AOV: R$ {row['aov']:,.2f}<extra></extra>",
            ))
        # Global average line
        fig.add_shape(
            type="line",
            x0=global_aov, x1=global_aov,
            y0=-0.5, y1=len(region_df) - 0.5,
            line=dict(color=PALETTE["amber"], width=2, dash="dash"),
        )
        fig.add_annotation(
            x=global_aov, y=len(region_df) - 0.5,
            text=f"Moy. globale: R$ {global_aov:.2f}",
            showarrow=False,
            xshift=10, yshift=10,
            font=dict(color=PALETTE["amber"], size=11),
        )
        fig.update_layout(
            **PLOTLY_BASE,
            yaxis=dict(categoryorder="total ascending"),
            xaxis=dict(gridcolor=PALETTE["border"], title="Panier Moyen (R$)"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_stack:
    st.markdown("###  Mix Catégorie par Région (100%)")
    mix_df = run_query(f"""
    SELECT
        region,
        Category_Group AS Category_Group,
        SUM(total_revenue) AS revenue
    FROM vw_dashboard
    {where}
    {"AND region IS NOT NULL AND Category_Group IS NOT NULL"
        if where
        else "WHERE region IS NOT NULL AND Category_Group IS NOT NULL"}
    GROUP BY 1, 2
    ORDER BY 1
""")
    if not mix_df.empty:
        # Compute pct within region
        mix_df["pct"] = mix_df.groupby("region")["revenue"].transform(lambda x: x / x.sum() * 100)
        fig = px.bar(
            mix_df, x="pct", y="region",
            color="Category_Group",
            orientation="h",
            barmode="stack",
            color_discrete_sequence=COLOR_SEQ,
            labels={"pct": "Part (%)", "region": "", "Category_Group": "Catégorie"},
            custom_data=["revenue"],
        )
        fig.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Part: %{x:.1f}%<br>CA: R$ %{customdata[0]:,.0f}<extra></extra>"
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(title="Part (%)", gridcolor=PALETTE["border"]),
            yaxis=dict(showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font_size=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ── Row 3 : Heatmap Matrix Région × Catégorie ────────────────────────────
st.markdown("###  Top Région par Catégorie — Matrix Revenue")

matrix_df = run_query(f"""
    SELECT
        region,
        Category_Group AS Category_Group,
        SUM(total_revenue) AS revenue
    FROM vw_dashboard
    {where}
    {"AND region IS NOT NULL AND Category_Group IS NOT NULL"
        if where
        else "WHERE region IS NOT NULL AND Category_Group IS NOT NULL"}
    GROUP BY 1, 2
""")

if not matrix_df.empty:
    pivot = matrix_df.pivot_table(
        index="region", columns="Category_Group",
        values="revenue", aggfunc="sum"
    ).fillna(0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f172a"], [0.3, "#1e3a5f"], [0.7, "#0284c7"], [1, "#38bdf8"]],
        hovertemplate="Région: %{y}<br>Catégorie: %{x}<br>CA: R$ %{z:,.0f}<extra></extra>",
        text=[[f"R$ {v/1e3:.0f}k" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color="#f8fafc"),
    ))
    fig.update_layout(
        **PLOTLY_BASE,
        xaxis=dict(showgrid=False, tickangle=-30, side="bottom"),
        yaxis=dict(showgrid=False),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée.")