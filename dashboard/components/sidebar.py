"""
components/sidebar.py — Filtres et navigation.
"""

import streamlit as st
import pandas as pd

def render_sidebar(df: pd.DataFrame) -> dict:
    st.sidebar.markdown(
        '<div class="sidebar-brand">Olist Analytics</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        '<div class="sidebar-brand-sub">Marketplace brésilienne · 2016–2018</div>',
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")

    st.sidebar.markdown(
        '<div class="filter-label">Navigation</div>',
        unsafe_allow_html=True
    )
    page = st.sidebar.radio(
        "",
        ["Vue Exécutive", "Produits & Catégories", "Saisonnalité", "Géographie"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div class="filter-label">Filtres globaux</div>',
        unsafe_allow_html=True
    )

    all_years    = sorted(df['year'].dropna().unique().tolist())
    all_regions  = sorted(df['region'].dropna().unique().tolist())
    all_groups   = sorted(df['category_group'].dropna().unique().tolist())
    all_payments = sorted(df['payment_method'].dropna().unique().tolist())

    sel_years = st.sidebar.multiselect(
        "Année", all_years, default=all_years
    )
    sel_regions = st.sidebar.multiselect(
        "Région", all_regions, default=all_regions
    )
    sel_groups = st.sidebar.multiselect(
        "Famille de produit", all_groups, default=all_groups
    )
    sel_payments = st.sidebar.multiselect(
        "Mode de paiement", all_payments, default=all_payments
    )

    return {
        "page":     page,
        "years":    sel_years    if sel_years    else all_years,
        "regions":  sel_regions  if sel_regions  else all_regions,
        "groups":   sel_groups   if sel_groups   else all_groups,
        "payments": sel_payments if sel_payments else all_payments,
    }

