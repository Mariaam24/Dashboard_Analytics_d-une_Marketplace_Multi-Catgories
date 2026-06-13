"""
pages/executive.py — Page 1 : Vue Exécutive.
"""

import streamlit as st
import pandas as pd
from components.kpis import render_kpis
from components.charts import line_chart, bar_horizontal, pie_chart
from config import COLOR_PRIMARY, COLOR_ACCENT, COLOR_SEQ


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Vue Exécutive</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Synthèse des indicateurs clés de performance</div>',
        unsafe_allow_html=True
    )

    render_kpis(df)
    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            '<div class="section-title">Évolution du CA mensuel</div>',
            unsafe_allow_html=True
        )
        ca_month = df.groupby('year_month')['revenue_prod'].sum().reset_index()
        ca_month.columns = ['Mois', 'CA (R$)']
        st.plotly_chart(
            line_chart(ca_month, x='Mois', y='CA (R$)'),
            use_container_width=True
        )

    with col2:
        st.markdown(
            '<div class="section-title">CA par famille de catégorie</div>',
            unsafe_allow_html=True
        )
        ca_cat = df.groupby('category_group')['revenue_prod'].sum().reset_index()
        ca_cat.columns = ['Catégorie', 'CA (R$)']
        ca_cat = ca_cat.sort_values('CA (R$)', ascending=True)
        st.plotly_chart(
            bar_horizontal(ca_cat, x='CA (R$)', y='Catégorie'),
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Répartition des modes de paiement</div>',
            unsafe_allow_html=True
        )
        pay = df['payment_method'].value_counts().reset_index()
        pay.columns = ['Mode', 'Nombre']
        st.plotly_chart(
            pie_chart(pay, values='Nombre', names='Mode', color_seq=COLOR_SEQ),
            use_container_width=True
        )

    with col2:
        st.markdown(
            '<div class="section-title">CA par macro-région</div>',
            unsafe_allow_html=True
        )
        ca_reg = df.groupby('region')['revenue_prod'].sum().reset_index()
        ca_reg.columns = ['Région', 'CA (R$)']
        ca_reg = ca_reg.sort_values('CA (R$)', ascending=True)
        st.plotly_chart(
            bar_horizontal(ca_reg, x='CA (R$)', y='Région', color=COLOR_ACCENT),
            use_container_width=True
        )