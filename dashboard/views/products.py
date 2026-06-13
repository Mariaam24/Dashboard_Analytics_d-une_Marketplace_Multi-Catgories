"""
pages/products.py - Page 2 : Produits et Categories.

ADAPTATIONS OLIST (cf. document adaptation CDC) :
- Product Name ABSENT dans Olist -> Category utilisee comme proxy
- Top 10 produits -> Top 10 categories par CA (granularite disponible)
- Heatmap : utilise Category_Group (10 familles) et non les 72 categories
- Scatter : Unit Price (X) x Quantity (Y) avec category comme hover

CDC Page 2 :
- Top 10 categories par CA    : Bar Chart horizontal, Revenue DESC, volume en couleur
- Heatmap semaine x categorie : Revenue par semaine x Category_Group
- Prix vs Volume               : Scatter Unit Price (X) x Quantity (Y)
- Repartition prix             : Stacked Bar Price Tier x Categorie x Revenue
- Tendance par categorie       : Multi-line Chart Revenue mensuel par Category_Group
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from components.charts import heatmap, bar_stacked, line_chart
from config import COLOR_PRIMARY, COLOR_SEQ, PLOTLY_LAYOUT


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Produits et Categories</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">'
        'Top 10 categories par CA — Product Name absent dans Olist, Category utilise comme proxy'
        '</div>',
        unsafe_allow_html=True
    )

    # Top 10 categories par CA avec volume en couleur
    # ADAPTATION : "Top 10 produits" -> "Top 10 categories par CA"
    st.markdown(
        '<div class="section-title">Top 10 categories par CA — volume en couleur</div>',
        unsafe_allow_html=True
    )

    top10 = df.groupby('category').agg(
        CA=('revenue_prod', 'sum'),
        Volume=('quantity', 'sum')
    ).reset_index()
    top10 = top10.sort_values('CA', ascending=False).head(10)
    top10 = top10.sort_values('CA', ascending=True)

    fig = px.bar(
        top10, x='CA', y='category', orientation='h',
        color='Volume',
        color_continuous_scale='Blues',
        labels={'CA': 'CA (R$)', 'category': 'Categorie', 'Volume': 'Volume'}
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap + Scatter
    col1, col2 = st.columns(2)

    with col1:
        # ADAPTATION : Category_Group (10 familles) au lieu des 72 categories
        st.markdown(
            '<div class="section-title">Heatmap Revenue — Semaine x Category Group</div>',
            unsafe_allow_html=True
        )
        hm = df.groupby(['week', 'category_group'])['revenue_prod'].sum().reset_index()
        pivot = hm.pivot(
            index='category_group', columns='week', values='revenue_prod'
        ).fillna(0)
        fig = heatmap(pivot, color_scale='Blues')
        fig.update_layout(xaxis_title="Semaine", yaxis_title="Famille")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # CDC : Scatter Unit Price (X) x Quantity (Y)
        # ADAPTATION : category comme hover_name (proxy de Product Name)
        st.markdown(
            '<div class="section-title">Prix vs Volume — Unit Price (X) x Quantity (Y)</div>',
            unsafe_allow_html=True
        )
        scatter = df.groupby('category').agg(
            Unit_Price=('unit_price', 'mean'),
            Quantity=('quantity', 'sum'),
            CA=('revenue_prod', 'sum')
        ).reset_index()
        fig = px.scatter(
            scatter,
            x='Unit_Price',
            y='Quantity',
            size='CA',
            hover_name='category',
            color='CA',
            color_continuous_scale='Blues',
            labels={
                'Unit_Price': 'Prix unitaire moyen (R$)',
                'Quantity':   'Volume total',
                'CA':         'CA (R$)'
            }
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    # Stacked Bar : Price Tier x Category_Group x Revenue
    st.markdown(
        '<div class="section-title">Repartition CA — Price Tier x Famille de categorie</div>',
        unsafe_allow_html=True
    )
    tier = df.groupby(
        ['price_tier', 'category_group'], observed=True
    )['revenue_prod'].sum().reset_index()
    tier.columns = ['Tranche de prix', 'Famille', 'CA (R$)']
    st.plotly_chart(
        bar_stacked(tier, x='Famille', y='CA (R$)',
                    color='Tranche de prix', color_seq=COLOR_SEQ),
        use_container_width=True
    )

    # Multi-line : Tendance mensuelle par Category_Group
    # ADAPTATION : Category_Group (10 lignes) pour legende lisible
    st.markdown(
        '<div class="section-title">Tendance mensuelle par famille de categorie</div>',
        unsafe_allow_html=True
    )
    trend = df.groupby(
        ['year_month', 'category_group']
    )['revenue_prod'].sum().reset_index()
    trend.columns = ['Mois', 'Famille', 'CA (R$)']
    st.plotly_chart(
        line_chart(trend, x='Mois', y='CA (R$)',
                   color='Famille', color_seq=COLOR_SEQ),
        use_container_width=True
    )