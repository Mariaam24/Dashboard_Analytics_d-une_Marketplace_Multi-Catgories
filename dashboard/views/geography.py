"""
pages/geography.py — Page 4 : Géographie.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from components.charts import bar_horizontal, bar_with_vline, heatmap
from config import COLOR_PRIMARY, COLOR_ACCENT, COLOR_SEQ, PLOTLY_LAYOUT


def render(df: pd.DataFrame) -> None:

    st.markdown('<div class="main-header">Performance Géographique</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="main-subtitle">Identification des marchés prioritaires et zones sous-performantes</div>',
        unsafe_allow_html=True
    )

    # Layout sans margin pour la carte
    layout_map = {k: v for k, v in PLOTLY_LAYOUT.items() if k != 'margin'}

    # ─────────────────────────────────────────
    # Carte choroplèthe — Revenue par état
    # ─────────────────────────────────────────
    st.markdown(
        '<div class="section-title">Carte — Revenue total par région</div>',
        unsafe_allow_html=True
    )
    ca_state = df.groupby('region_state')['revenue_prod'].sum().reset_index()
    ca_state.columns = ['État', 'CA (R$)']
    fig_map = px.choropleth(
        ca_state,
        locations='État',
        locationmode='geojson-id',
        geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
        featureidkey='properties.sigla',
        color='CA (R$)',
        color_continuous_scale='Blues',
        labels={'CA (R$)': 'Revenue (R$)'}
    )
    fig_map.update_geos(fitbounds='locations', visible=False)
    fig_map.update_layout(**layout_map, margin=dict(t=10, b=10, l=0, r=0))
    st.plotly_chart(fig_map, use_container_width=True)

    # ─────────────────────────────────────────
    # Ranking + AOV
    # ─────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Classement des régions par revenue</div>',
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
            '<div class="section-title">Panier moyen par région vs moyenne globale (AOV)</div>',
            unsafe_allow_html=True
        )
        avg_reg = df.groupby('region')['revenue_prod'].mean().reset_index()
        avg_reg.columns = ['Région', 'Panier Moyen (R$)']
        global_avg = df['revenue_prod'].mean()
        st.plotly_chart(
            bar_with_vline(
                avg_reg, x='Panier Moyen (R$)', y='Région',
                vline_value=global_avg,
                vline_label=f"Moy. globale : R${global_avg:.0f}",
                color=COLOR_ACCENT
            ),
            use_container_width=True
        )

    # ─────────────────────────────────────────
    # Mix catégories — Stacked Bar 100%
    # ─────────────────────────────────────────
    st.markdown(
        '<div class="section-title">Mix catégories par région — répartition 100%</div>',
        unsafe_allow_html=True
    )
    mix = df.groupby(['region', 'category_group'])['revenue_prod'].sum().reset_index()
    mix.columns = ['Région', 'Famille', 'CA (R$)']
    total_par_region = mix.groupby('Région')['CA (R$)'].transform('sum')
    mix['Pct (%)'] = (mix['CA (R$)'] / total_par_region * 100).round(1)
    fig_stack = px.bar(
        mix, x='Région', y='Pct (%)', color='Famille',
        barmode='stack', color_discrete_sequence=COLOR_SEQ,
        text=mix['Pct (%)'].apply(lambda x: f'{x:.0f}%' if x >= 5 else '')
    )
    fig_stack.update_traces(textposition='inside')
    fig_stack.update_layout(**PLOTLY_LAYOUT)
    fig_stack.update_yaxes(title='Part (%)', range=[0, 100], showgrid=True, gridcolor='#f3f4f6')
    fig_stack.update_layout(legend=dict(orientation='h', y=-0.2, title=''))
    st.plotly_chart(fig_stack, use_container_width=True)

    # ─────────────────────────────────────────
    # Heatmap Région × Catégorie
    # ─────────────────────────────────────────
    st.markdown(
        '<div class="section-title">Heatmap — Région × Catégorie</div>',
        unsafe_allow_html=True
    )
    heat_reg = df.groupby(['region', 'category_group'])['revenue_prod'].sum().reset_index()
    pivot = heat_reg.pivot(
        index='region',
        columns='category_group',
        values='revenue_prod'
    ).fillna(0)
    fig_heat = heatmap(pivot, color_scale='Blues')
    fig_heat.update_layout(xaxis_title="Catégorie", yaxis_title="Région")
    st.plotly_chart(fig_heat, use_container_width=True)

    # ─────────────────────────────────────────
    # Tableau détail par état
    # ─────────────────────────────────────────
    st.markdown(
        '<div class="section-title">Détail par état brésilien</div>',
        unsafe_allow_html=True
    )
    state_detail = df.groupby(['region_state', 'region']).agg(
        CA=('revenue_prod', 'sum'),
        Commandes=('order_id', 'count'),
        Panier_Moyen=('revenue_prod', 'mean')
    ).reset_index().sort_values('CA', ascending=False)
    state_detail['CA'] = state_detail['CA'].round(0).astype(int)
    state_detail['Panier_Moyen'] = state_detail['Panier_Moyen'].round(2)
    state_detail['Part (%)'] = (
        state_detail['CA'] / state_detail['CA'].sum() * 100
    ).round(1)
    state_detail.columns = ['État', 'Région', 'CA (R$)', 'Commandes', 'Panier Moyen (R$)', 'Part (%)']
    st.dataframe(state_detail, use_container_width=True, hide_index=True)