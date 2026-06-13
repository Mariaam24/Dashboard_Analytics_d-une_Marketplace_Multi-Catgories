"""
pages/seasonality.py — Page 3 : Saisonnalité.
"""

import streamlit as st
import pandas as pd
from components.charts import heatmap, bar_grouped, line_chart, area_chart
from config import COLOR_PRIMARY, COLOR_SEQ


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Saisonnalité & Temporalité</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Analyse des cycles de vente et des tendances temporelles</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Heatmap CA — Mois × Jour de semaine</div>',
            unsafe_allow_html=True
        )
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heat = df.groupby(['month', 'day_of_week'])['revenue_prod'].sum().reset_index()
        pivot = heat.pivot(index='day_of_week', columns='month', values='revenue_prod').fillna(0)
        pivot = pivot.reindex([d for d in days_order if d in pivot.index])
        fig = heatmap(pivot, color_scale='Blues')
        fig.update_layout(xaxis_title="Mois", yaxis_title="Jour")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(
            '<div class="section-title">CA par trimestre</div>',
            unsafe_allow_html=True
        )
        quarterly = df.groupby(['year', 'quarter'])['revenue_prod'].sum().reset_index()
        quarterly['Période'] = 'Q' + quarterly['quarter'].astype(str) + ' ' + quarterly['year'].astype(str)
        quarterly['Année'] = quarterly['year'].astype(str)
        quarterly.rename(columns={'revenue_prod': 'CA (R$)'}, inplace=True)
        st.plotly_chart(
            bar_grouped(quarterly, x='Période', y='CA (R$)', color='Année', color_seq=COLOR_SEQ),
            use_container_width=True
        )

    st.markdown(
        '<div class="section-title">Tendance mensuelle par famille de catégorie</div>',
        unsafe_allow_html=True
    )
    trend = df.groupby(['year_month', 'category_group'])['revenue_prod'].sum().reset_index()
    trend.columns = ['Mois', 'Famille', 'CA (R$)']
    st.plotly_chart(
        line_chart(trend, x='Mois', y='CA (R$)', color='Famille', color_seq=COLOR_SEQ),
        use_container_width=True
    )

    st.markdown(
        '<div class="section-title">CA cumulé sur la période</div>',
        unsafe_allow_html=True
    )
    cumul = df.groupby('year_month')['revenue_prod'].sum().cumsum().reset_index()
    cumul.columns = ['Mois', 'CA Cumulé (R$)']
    st.plotly_chart(
        area_chart(cumul, x='Mois', y='CA Cumulé (R$)', color=COLOR_PRIMARY),
        use_container_width=True
    )