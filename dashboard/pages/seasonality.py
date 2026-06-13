import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils import run_query, apply_custom_style, get_filters, PALETTE, COLOR_SEQ, PLOTLY_BASE

st.set_page_config(page_title="Saisonnalité — Olist", page_icon="", layout="wide")
apply_custom_style()
where, dates, sel_cats, sel_regs = get_filters()

st.title(" Saisonnalité & Tendances Temporelles")
st.markdown("<p style='color:#94a3b8;margin-top:-.5rem'>Comprendre les cycles de vente et anticiper les pics</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ── Row 1 : Heatmap 12×7 + Comparaison YoY ──────────────────────────────
col_heat, col_yoy = st.columns([3, 2])

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_FR    = ["Lun",    "Mar",     "Mer",       "Jeu",      "Ven",    "Sam",      "Dim"]
MONTH_FR  = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]

with col_heat:
    st.markdown("###  Heatmap Revenue — Mois × Jour de Semaine")
    heat_df = run_query(f"""
    SELECT month, day_name, SUM(total_revenue) AS revenue
    FROM vw_dashboard
    {where}
    {"AND day_name IS NOT NULL" if where else "WHERE day_name IS NOT NULL"}
    GROUP BY 1, 2
""")
    if not heat_df.empty:
        # order rows (months) and columns (days)
        heat_df["day_idx"] = heat_df["day_name"].apply(
            lambda d: DAY_ORDER.index(d) if d in DAY_ORDER else 9
        )
        heat_df["day_fr"] = heat_df["day_name"].apply(
            lambda d: DAY_FR[DAY_ORDER.index(d)] if d in DAY_ORDER else d
        )
        heat_df["month_fr"] = heat_df["month"].apply(
            lambda m: MONTH_FR[int(m)-1] if 1 <= int(m) <= 12 else str(m)
        )
        pivot = heat_df.pivot_table(index="month_fr", columns="day_fr",
                                    values="revenue", aggfunc="sum").fillna(0)
        # Re-order columns
        pivot = pivot.reindex(columns=[d for d in DAY_FR if d in pivot.columns])
        # Re-order rows
        pivot = pivot.reindex(MONTH_FR, fill_value=0)
        pivot = pivot.loc[pivot.index.isin(heat_df["month_fr"].unique())]

        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Blues",
            hovertemplate="Mois: %{y}<br>Jour: %{x}<br>CA: R$ %{z:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_BASE, height=380,
            xaxis=dict(side="top", showgrid=False),
            yaxis=dict(showgrid=False, autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_yoy:
    st.markdown("###  Comparaison Year-over-Year")
    yoy_df = run_query(f"""
        SELECT year, month, SUM(total_revenue) AS revenue
        FROM vw_dashboard {where}
        GROUP BY 1, 2
        ORDER BY 2, 1
    """)
    if not yoy_df.empty:
        yoy_df["month_fr"] = yoy_df["month"].apply(
            lambda m: MONTH_FR[int(m)-1] if 1 <= int(m) <= 12 else str(m)
        )
        yoy_df["year"] = yoy_df["year"].astype(str)
        fig = px.bar(
            yoy_df, x="month_fr", y="revenue",
            color="year", barmode="group",
            color_discrete_sequence=[PALETTE["blue"], PALETTE["indigo"], PALETTE["green"]],
            category_orders={"month_fr": MONTH_FR},
            labels={"revenue": "CA (R$)", "month_fr": "Mois", "year": "Année"},
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor=PALETTE["border"]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ── Row 2 : Décomposition saisonnière + Croissance cumulée ───────────────
col_decomp, col_cum = st.columns([3, 2])

with col_decomp:
    st.markdown("###  Décomposition Saisonnière (Trend + Seasonality + Residual)")
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose

        ts_df = run_query(f"""
            SELECT date, SUM(total_revenue) AS revenue
            FROM vw_dashboard {where}
            GROUP BY date ORDER BY date
        """)
        ts_df["date"] = pd.to_datetime(ts_df["date"])
        ts_df = ts_df.set_index("date").asfreq("D").fillna(0)

        if len(ts_df) >= 60:
            result = seasonal_decompose(ts_df["revenue"], model="additive", period=30)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts_df.index, y=ts_df["revenue"],
                                    name="Observé", line=dict(color=PALETTE["muted"], width=1)))
            fig.add_trace(go.Scatter(x=result.trend.index, y=result.trend,
                                    name="Tendance", line=dict(color=PALETTE["blue"], width=2.5)))
            fig.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal,
                                    name="Saisonnalité", line=dict(color=PALETTE["indigo"], width=1.5,
                                                                    dash="dot")))
            fig.add_trace(go.Scatter(x=result.resid.index, y=result.resid,
                                    name="Résidu", line=dict(color=PALETTE["amber"], width=1,
                                                            dash="dash")))
            fig.update_layout(
                **PLOTLY_BASE,
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor=PALETTE["border"]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                height=360,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Pas assez de données pour la décomposition (minimum 60 jours requis).")
    except Exception as e:
        st.error(f"Erreur de décomposition : {e}")

with col_cum:
    st.markdown("###  Croissance Cumulée du CA")
    cum_df = run_query(f"""
        SELECT date, SUM(total_revenue) AS daily_rev
        FROM vw_dashboard {where}
        GROUP BY date ORDER BY date
    """)
    if not cum_df.empty:
        cum_df["date"] = pd.to_datetime(cum_df["date"])
        cum_df["cumulative"] = cum_df["daily_rev"].cumsum()

        fig = px.area(
            cum_df, x="date", y="cumulative",
            color_discrete_sequence=[PALETTE["indigo"]],
            labels={"cumulative": "CA Cumulé (R$)", "date": ""},
        )
        fig.update_traces(
            fillcolor="rgba(129,140,248,0.15)",
            line_color=PALETTE["indigo"],
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor=PALETTE["border"]),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée.")

st.markdown("---")

# ── Row 3 : Volume par jour de semaine (+ heure si disponible) ───────────
st.markdown("###  Volume de Commandes par Jour de la Semaine")

dow_df = run_query(f"""
    SELECT day_name,
        COUNT(DISTINCT order_id) AS orders,
        SUM(total_revenue) AS revenue
    FROM vw_dashboard
    {where}
    {"AND day_name IS NOT NULL" if where else "WHERE day_name IS NOT NULL"}
    GROUP BY 1
""")

if not dow_df.empty:
    dow_df["day_idx"] = dow_df["day_name"].apply(
        lambda d: DAY_ORDER.index(d) if d in DAY_ORDER else 9
    )
    dow_df["Jour"] = dow_df["day_name"].apply(
        lambda d: DAY_FR[DAY_ORDER.index(d)] if d in DAY_ORDER else d
    )
    dow_df = dow_df.sort_values("day_idx")

    c_dow, c_info = st.columns([3, 1])
    with c_dow:
        fig = px.bar(
            dow_df, x="Jour", y="orders",
            color="orders",
            color_continuous_scale=[[0, "#1e293b"], [1, PALETTE["blue"]]],
            labels={"orders": "Nb Commandes", "Jour": ""},
            custom_data=["revenue"],
        )
        fig.update_traces(
            hovertemplate="<b>%{x}</b><br>Commandes: %{y:,}<br>CA: R$ %{customdata[0]:,.0f}<extra></extra>"
        )
        fig.update_layout(
            **PLOTLY_BASE,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor=PALETTE["border"]),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_info:
        best = dow_df.loc[dow_df["orders"].idxmax()]
        worst = dow_df.loc[dow_df["orders"].idxmin()]
        st.markdown(f"""
        ** Insights**

         **Jour le + actif** :  
        `{best['Jour']}` — {best['orders']:,} commandes

         **Jour le - actif** :  
        `{worst['Jour']}` — {worst['orders']:,} commandes

        ---
        *Note : les données source ne contiennent pas l'heure de commande. L'analyse intra-journalière n'est donc pas disponible.*
        """)
else:
    st.info("Aucune donnée.")