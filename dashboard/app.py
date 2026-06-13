"""
app.py — Point d'entrée principal du dashboard Olist Analytics.

Lancement OBLIGATOIRE depuis la racine du projet :
    cd C:/Users/HP/Desktop/olist_project
    streamlit run dashboard/app.py
"""

import sys
import os

# ── CRITIQUE : ajouter le dossier dashboard/ au sys.path ──────
# Cela permet à tous les fichiers (config, data_loader, components, pages)
# d'être importés sans préfixe "dashboard."
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
if DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, DASHBOARD_DIR)

import streamlit as st

st.set_page_config(
    page_title="Olist Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Imports internes (fonctionnent grâce au sys.path ci-dessus) ──
from config import GLOBAL_CSS
from data_loader import load_data, filter_data
from components.sidebar import render_sidebar
from views import executive, products, seasonality, geography

# ── CSS global ────────────────────────────────────────────────
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Chargement des données ────────────────────────────────────
df = load_data()

# ── Sidebar : navigation + filtres ───────────────────────────
sidebar = render_sidebar(df)

# ── Filtrage global ───────────────────────────────────────────
filtered = filter_data(
    df,
    years    = sidebar['years'],
    regions  = sidebar['regions'],
    groups   = sidebar['groups'],
    payments = sidebar['payments']
)

# ── Garde-fou : sélection vide ────────────────────────────────
if filtered.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

# ── Routage vers la page sélectionnée ────────────────────────
page = sidebar['page']

if page == "Vue Exécutive":
    executive.render(filtered)
elif page == "Produits & Catégories":
    products.render(filtered)
elif page == "Saisonnalité":
    seasonality.render(filtered)
elif page == "Géographie":
    geography.render(filtered)