"""
pages/executive.py - Page 1 : Vue Executive.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from components.charts import line_chart, bar_horizontal, pie_chart
from config import COLOR_PRIMARY, COLOR_ACCENT, COLOR_SEQ, PLOTLY_LAYOUT


@st.cache_data
def get_brazil_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    return requests.get(url).json()


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Vue Executive</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">Synthese des indicateurs cles de performance</div>', unsafe_allow_html=True)

    # KPIs
    ca  = df['revenue_prod'].sum()
    nb  = len(df)
    avg = df['revenue_prod'].mean()

    ca_month = df.groupby('year_month')['revenue_prod'].sum().sort_index()
    if len(ca_month) >= 2:
        last     = ca_month.iloc[-1]
        prev     = ca_month.iloc[-2]
        mom      = ((last - prev) / prev * 100) if prev > 0 else 0
        mom_str  = f"{mom:+.1f}%"
        mom_note = "vs mois precedent"
    else:
        mom_str  = "N/A"
        mom_note = ""

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CA Total (R$)",     f"{ca:,.0f}")
    c2.metric("Nb Commandes",      f"{nb:,}")
    c3.metric("Panier Moyen (R$)", f"{avg:,.2f}")
    c4.metric(
    "Croissance MoM",
    mom_str
 )

    st.markdown("---")

    # Sparklines
    st.markdown('<div class="section-title">Tendance 30 derniers jours</div>', unsafe_allow_html=True)

    last_30 = df[df['date'] >= df['date'].max() - pd.Timedelta(days=30)]
    daily   = last_30.groupby(last_30['date'].dt.date).agg(
        CA=('revenue_prod', 'sum'),
        Commandes=('order_id', 'count'),
        Panier=('revenue_prod', 'mean')
    ).reset_index()

    sp1, sp2, sp3 = st.columns(3)

    with sp1:
        fig = go.Figure(go.Scatter(
            x=daily['date'], y=daily['CA'],
            mode='lines', fill='tozeroy',
            line=dict(color=COLOR_PRIMARY, width=1.5),
            fillcolor='rgba(37,99,235,0.08)'
        ))
        fig.update_layout(
            height=100, margin=dict(t=5, b=5, l=5, r=5),
            paper_bgcolor='white', plot_bgcolor='white',
            xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.caption("CA journalier (30j)")
        st.plotly_chart(fig, use_container_width=True)

    with sp2:
        fig = go.Figure(go.Scatter(
            x=daily['date'], y=daily['Commandes'],
            mode='lines', fill='tozeroy',
            line=dict(color=COLOR_ACCENT, width=1.5),
            fillcolor='rgba(245,158,11,0.08)'
        ))
        fig.update_layout(
            height=100, margin=dict(t=5, b=5, l=5, r=5),
            paper_bgcolor='white', plot_bgcolor='white',
            xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.caption("Commandes journalieres (30j)")
        st.plotly_chart(fig, use_container_width=True)

    with sp3:
        fig = go.Figure(go.Scatter(
            x=daily['date'], y=daily['Panier'],
            mode='lines', fill='tozeroy',
            line=dict(color='#10b981', width=1.5),
            fillcolor='rgba(16,185,129,0.08)'
        ))
        fig.update_layout(
            height=100, margin=dict(t=5, b=5, l=5, r=5),
            paper_bgcolor='white', plot_bgcolor='white',
            xaxis=dict(visible=False), yaxis=dict(visible=False)
        )
        st.caption("Panier moyen journalier (30j)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Evolution CA + Donut categories
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-title">Evolution du CA mensuel</div>', unsafe_allow_html=True)
        d = df.groupby('year_month')['revenue_prod'].sum().reset_index()
        d.columns = ['Mois', 'CA (R$)']
        st.plotly_chart(line_chart(d, x='Mois', y='CA (R$)'), use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">CA par categorie</div>', unsafe_allow_html=True)
        d = df.groupby('category_group')['revenue_prod'].sum().reset_index()
        d.columns = ['Categorie', 'CA (R$)']
        d = d.sort_values('CA (R$)', ascending=False)
        st.plotly_chart(
            pie_chart(d, values='CA (R$)', names='Categorie', color_seq=COLOR_SEQ),
            use_container_width=True
        )

    # Carte Bresil + Ranking regions
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Carte geographique — CA par etat</div>', unsafe_allow_html=True)
        try:
            geojson = get_brazil_geojson()
            ca_state = df.groupby('region_state')['revenue_prod'].sum().reset_index()
            ca_state.columns = ['Etat', 'CA (R$)']
            fig = px.choropleth(
                ca_state,
                geojson=geojson,
                locations='Etat',
                featureidkey='properties.sigla',
                color='CA (R$)',
                color_continuous_scale='Blues',
                hover_name='Etat',
                hover_data={'CA (R$)': ':,.0f'}
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='white',
                height=350,
                coloraxis_colorbar=dict(title="CA (R$)")
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Carte non disponible (connexion requise) : {e}")
            ca_reg = df.groupby('region')['revenue_prod'].sum().reset_index()
            ca_reg.columns = ['Region', 'CA (R$)']
            ca_reg = ca_reg.sort_values('CA (R$)', ascending=True)
            st.plotly_chart(
                bar_horizontal(ca_reg, x='CA (R$)', y='Region'),
                use_container_width=True
            )

    with col2:
        st.markdown('<div class="section-title">Ranking des regions</div>', unsafe_allow_html=True)
        d = df.groupby('region')['revenue_prod'].sum().reset_index()
        d.columns = ['Region', 'CA (R$)']
        d = d.sort_values('CA (R$)', ascending=True)
        st.plotly_chart(
            bar_horizontal(d, x='CA (R$)', y='Region', color=COLOR_ACCENT),
            use_container_width=True
        )