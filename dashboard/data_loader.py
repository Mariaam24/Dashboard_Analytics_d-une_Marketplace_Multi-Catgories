"""
data_loader.py — Chargement et filtrage de silver_orders.csv.
"""

import os
import pandas as pd
import streamlit as st
from config import DATA_PATH


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.lower() for c in df.columns]
    df['date']        = pd.to_datetime(df['date'])
    df['year']        = df['date'].dt.year
    df['month']       = df['date'].dt.month
    df['month_name']  = df['date'].dt.strftime('%b')
    df['year_month']  = df['date'].dt.strftime('%Y-%m')
    df['quarter']     = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.day_name()
    df['week']        = df['date'].dt.isocalendar().week.astype(int)
    df['price_tier']  = pd.cut(
        df['unit_price'],
        bins=[0, 20, 100, float('inf')],
        labels=[
            'Entrée de gamme (< R$20)',
            'Milieu de gamme (R$20–100)',
            'Haut de gamme (> R$100)'
        ]
    )
    return df


def filter_data(df, years, regions, groups, payments) -> pd.DataFrame:
    mask = (
        (df['year'].isin(years)) &
        (df['region'].isin(regions)) &
        (df['category_group'].isin(groups)) &
        (df['payment_method'].isin(payments))
    )
    return df[mask]