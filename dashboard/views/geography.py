"""
pages/geography.py — Page 4 : Géographie.
"""

import streamlit as st
import pandas as pd
from components.charts import bar_horizontal, bar_with_vline, bar_stacked, heatmap
from config import COLOR_PRIMARY, COLOR_ACCENT, COLOR_SEQ


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Performance Géographique</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Analyse des marchés par macro-région brésilienne</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Classement des macro-régions</div>',
            unsafe_allow_html=True
        )
        ca_reg = df.groupby('region').agg(
            CA=('revenue_prod', 'sum'),
            Commandes=('order_id', 'count')
        ).reset_index().sort_values('CA', ascending=True)
        ca_reg.rename(columns={'region': 'Région', 'CA': 'CA (R$)'}, inplace=True)
        st.plotly_chart(
            bar_horizontal(ca_reg, x='CA (R$)', y='Région', color=COLOR_PRIMARY),
            use_container_width=True
        )

    with col2:
        st.markdown(
            '<div class="section-title">Panier moyen par région vs moyenne globale</div>',
            unsafe_allow_html=True
        )
        avg_reg = df.groupby('region')['revenue_prod'].mean().reset_index()
        avg_reg.columns = ['Région', 'Panier Moyen (R$)']
        global_avg = df['revenue_prod'].mean()
        st.plotly_chart(
            bar_with_vline(
                avg_reg, x='Panier Moyen (R$)', y='Région',
                vline_value=global_avg,
                vline_label=f"Moy. : R${global_avg:.0f}",
                color=COLOR_ACCENT
            ),
            use_container_width=True
        )

    st.markdown(
        '<div class="section-title">Mix catégories par région</div>',
        unsafe_allow_html=True
    )
    mix = df.groupby(['region', 'category_group'])['revenue_prod'].sum().reset_index()
    mix.columns = ['Région', 'Famille', 'CA (R$)']
    st.plotly_chart(
        bar_stacked(mix, x='Région', y='CA (R$)', color='Famille', color_seq=COLOR_SEQ),
        use_container_width=True
    )

    st.markdown(
        '<div class="section-title">Heatmap Région × Catégorie</div>',
        unsafe_allow_html=True
    )
    heat_reg = df.groupby(['region', 'category_group'])['revenue_prod'].sum().reset_index()
    pivot = heat_reg.pivot(index='region', columns='category_group', values='revenue_prod').fillna(0)
    fig = heatmap(pivot, color_scale='Blues')
    fig.update_layout(xaxis_title="Catégorie", yaxis_title="Région")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        '<div class="section-title">Détail par état brésilien</div>',
        unsafe_allow_html=True
    )
    state_detail = df.groupby('region_state').agg(
        CA=('revenue_prod', 'sum'),
        Commandes=('order_id', 'count'),
        Panier_Moyen=('revenue_prod', 'mean')
    ).reset_index().sort_values('CA', ascending=False)
    state_detail['CA'] = state_detail['CA'].round(0).astype(int)
    state_detail['Panier_Moyen'] = state_detail['Panier_Moyen'].round(2)
    state_detail.columns = ['État', 'CA (R$)', 'Commandes', 'Panier Moyen (R$)']
    st.dataframe(state_detail, use_container_width=True, hide_index=True)