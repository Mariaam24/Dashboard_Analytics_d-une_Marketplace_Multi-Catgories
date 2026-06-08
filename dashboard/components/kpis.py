"""
components/kpis.py — Cartes KPI.
"""

import streamlit as st
import pandas as pd


def render_kpis(df: pd.DataFrame) -> None:
    total_ca      = df['revenue_prod'].sum()
    nb_orders     = len(df)
    avg_basket    = df['revenue_prod'].mean() if nb_orders > 0 else 0
    total_freight = df['freight'].sum()
    freight_pct   = (
        total_freight / (total_ca + total_freight) * 100
        if (total_ca + total_freight) > 0 else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CA Produits (R$)",   f"{total_ca:,.0f}")
    c2.metric("Commandes livrées",  f"{nb_orders:,}")
    c3.metric("Panier moyen (R$)",  f"{avg_basket:,.2f}")
    c4.metric(
        "Frais de port (R$)",
        f"{total_freight:,.0f}",
        delta=f"{freight_pct:.1f}% du CA total"
    )