"""
pages/products.py — Page 2 : Produits & Catégories.
"""

import streamlit as st
import pandas as pd
from components.charts import bar_horizontal, scatter_chart, heatmap, bar_stacked
from config import COLOR_SEQ


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Produits & Catégories</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Analyse de la performance par catégorie produit</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Top 10 catégories par CA</div>',
            unsafe_allow_html=True
        )
        top10 = df.groupby('category')['revenue_prod'].sum().reset_index()
        top10.columns = ['Catégorie', 'CA (R$)']
        top10 = top10.sort_values('CA (R$)', ascending=True).tail(10)
        st.plotly_chart(
            bar_horizontal(top10, x='CA (R$)', y='Catégorie'),
            use_container_width=True
        )

    with col2:
        st.markdown(
            '<div class="section-title">Prix moyen vs Volume par catégorie</div>',
            unsafe_allow_html=True
        )
        scatter = df.groupby('category').agg(
            CA=('revenue_prod', 'sum'),
            Prix_Moyen=('unit_price', 'mean'),
            Volume=('quantity', 'sum')
        ).reset_index()
        st.plotly_chart(
            scatter_chart(scatter, x='Prix_Moyen', y='CA', size='Volume', hover='category'),
            use_container_width=True
        )

    st.markdown(
        '<div class="section-title">Heatmap CA — Semaine × Famille de catégorie</div>',
        unsafe_allow_html=True
    )
    hm = df.groupby(['week', 'category_group'])['revenue_prod'].sum().reset_index()
    pivot = hm.pivot(index='category_group', columns='week', values='revenue_prod').fillna(0)
    fig = heatmap(pivot, color_scale='Blues')
    fig.update_layout(xaxis_title="Semaine", yaxis_title="Famille")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="section-title">CA par tranche de prix et famille de catégorie</div>',
        unsafe_allow_html=True
    )
    tier = df.groupby(['price_tier', 'category_group'], observed=True)['revenue_prod'].sum().reset_index()
    tier.columns = ['Tranche de prix', 'Famille', 'CA (R$)']
    st.plotly_chart(
        bar_stacked(tier, x='Famille', y='CA (R$)', color='Tranche de prix', color_seq=COLOR_SEQ),
        use_container_width=True
    )