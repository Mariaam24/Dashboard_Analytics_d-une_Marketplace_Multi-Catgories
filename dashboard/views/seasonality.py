"""
pages/seasonality.py - Page 3 : Saisonnalite.

ADAPTATIONS OLIST :
- Donnees 2016-2018 (pas 2020-2023) - saisonnalite reste exploitable
- Volume par heure : order_purchase_timestamp contient l'heure -> colonne 'hour' a creer
- YoY : comparaison 2017 vs 2018 (2016 incomplet)
- Decomposition saisonniere : approximee par moyenne mobile (pas de statsmodels requis)

CDC Page 3 :
- Heatmap 12x7      : Revenue par mois x jour de semaine
- YoY               : Bar groupe Revenue par mois N vs N-1
- Decomposition     : Line Chart Trend + Seasonality + Residual
- Volume par heure  : Bar Chart Nb commandes par heure
- Croissance cumulee: Area Chart Revenue cumule sur l'annee
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from components.charts import heatmap, bar_grouped, area_chart
from config import COLOR_PRIMARY, COLOR_ACCENT, COLOR_SEQ, PLOTLY_LAYOUT


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Saisonnalite et Temporalite</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Cycles de vente et anticipation des pics de demande — donnees 2016-2018</div>',
        unsafe_allow_html=True
    )

    # Heatmap 12x7 + YoY
    col1, col2 = st.columns(2)

    with col1:
        # CDC : Heatmap 12x7 Revenue par mois x jour de semaine
        st.markdown(
            '<div class="section-title">Heatmap Revenue — Mois (12) x Jour de semaine (7)</div>',
            unsafe_allow_html=True
        )
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heat = df.groupby(['month', 'day_of_week'])['revenue_prod'].sum().reset_index()
        pivot = heat.pivot(index='day_of_week', columns='month', values='revenue_prod').fillna(0)
        pivot = pivot.reindex([d for d in days_order if d in pivot.index])
        # Renommer les colonnes en noms de mois
        month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                       7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        pivot.columns = [month_names.get(c, c) for c in pivot.columns]
        fig = heatmap(pivot, color_scale='Blues')
        fig.update_layout(xaxis_title="Mois", yaxis_title="Jour")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # CDC : Comparaison Year-over-Year Revenue par mois N vs N-1
        # ADAPTATION : comparaison 2017 vs 2018 (donnees Olist 2016-2018)
        st.markdown(
            '<div class="section-title">Comparaison Year-over-Year — Revenue par mois N vs N-1</div>',
            unsafe_allow_html=True
        )
        yoy = df.groupby(['year', 'month'])['revenue_prod'].sum().reset_index()
        yoy['Mois_label'] = yoy['month'].map(month_names)
        yoy['Annee'] = yoy['year'].astype(str)
        yoy.rename(columns={'revenue_prod': 'CA (R$)'}, inplace=True)
        fig = bar_grouped(yoy, x='Mois_label', y='CA (R$)', color='Annee', color_seq=COLOR_SEQ)
        fig.update_layout(xaxis=dict(
            categoryorder='array',
            categoryarray=list(month_names.values())
        ))
        st.plotly_chart(fig, use_container_width=True)

    # Decomposition saisonniere
    # CDC : Line Chart multi-couches Trend + Seasonality + Residual
    # ADAPTATION : decomposition approximee par moyenne mobile 12 mois
    st.markdown(
        '<div class="section-title">Decomposition saisonniere — Trend + Seasonality + Residual</div>',
        unsafe_allow_html=True
    )

    monthly = df.groupby('year_month')['revenue_prod'].sum().reset_index()
    monthly.columns = ['Mois', 'CA']
    monthly = monthly.sort_values('Mois')

    # Trend : moyenne mobile 3 mois
    monthly['Trend'] = monthly['CA'].rolling(window=3, center=True).mean()
    # Seasonality : ecart a la tendance
    monthly['Seasonality'] = monthly['CA'] - monthly['Trend']
    # Residual : ecart au lissage
    monthly['Residual'] = monthly['CA'] - monthly['Trend'].fillna(monthly['CA'].mean())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly['Mois'], y=monthly['CA'],
                             name='Revenue brut', line=dict(color=COLOR_SEQ[0], width=1.5)))
    fig.add_trace(go.Scatter(x=monthly['Mois'], y=monthly['Trend'],
                             name='Trend (moy. mobile 3m)', line=dict(color=COLOR_SEQ[1], width=2.5, dash='solid')))
    fig.add_trace(go.Scatter(x=monthly['Mois'], y=monthly['Seasonality'],
                             name='Saisonnalite', line=dict(color=COLOR_SEQ[2], width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=monthly['Mois'], y=monthly['Residual'],
                             name='Residuel', line=dict(color=COLOR_SEQ[3], width=1, dash='dash')))
    fig.update_layout(**PLOTLY_LAYOUT, xaxis_tickangle=-30,
                      legend=dict(orientation='h', y=-0.25, title=''))
    st.plotly_chart(fig, use_container_width=True)

    # Volume par heure
    # CDC : Bar Chart Nb commandes par heure de la journee
    # ADAPTATION : order_purchase_timestamp contient l'heure -> extraction possible
    st.markdown(
        '<div class="section-title">Volume par heure — Nb commandes par heure de la journee</div>',
        unsafe_allow_html=True
    )

    if 'hour' not in df.columns:
        # Creer la colonne hour si absente
        df = df.copy()
        df['hour'] = df['date'].dt.hour

    hourly = df.groupby('hour')['order_id'].count().reset_index()
    hourly.columns = ['Heure', 'Nb Commandes']

    fig = px.bar(
        hourly, x='Heure', y='Nb Commandes',
        color='Nb Commandes',
        color_continuous_scale='Blues',
        labels={'Heure': 'Heure de la journee', 'Nb Commandes': 'Nombre de commandes'}
    )
    fig.update_layout(**PLOTLY_LAYOUT)

    

    # Croissance cumulee
    # CDC : Area Chart Revenue cumule sur l'annee
    st.markdown(
        '<div class="section-title">Croissance cumulee — Revenue cumule sur la periode</div>',
        unsafe_allow_html=True
    )
    cumul = df.groupby('year_month')['revenue_prod'].sum().cumsum().reset_index()
    cumul.columns = ['Mois', 'CA Cumule (R$)']
    st.plotly_chart(
        area_chart(cumul, x='Mois', y='CA Cumule (R$)', color=COLOR_PRIMARY),
        use_container_width=True
    )