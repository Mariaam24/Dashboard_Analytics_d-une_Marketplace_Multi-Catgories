# Projet 1 — Dashboard Analytics Marketplace Olist

Pipeline ETL complet sur le dataset Olist Brazilian E-Commerce, du nettoyage des données brutes jusqu'au dashboard streamlit interactif.

---

## Contexte

Ce projet répond à trois problèmes opérationnels d'un retailer e-commerce :
- Absence de visibilité sur la saisonnalité des ventes
- Catalogue mal piloté (quels produits génèrent de la valeur ?)
- Marchés géographiques opaques (performances par région)

**Dataset :** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 9 fichiers CSV, ~99 441 commandes, période 2016-2018.

---

## Structure du projet

```
olist_project/
├── data/
│   ├── raw/                    # 9 fichiers CSV bruts (non modifiés)
│   │   ├── olist_orders_dataset.csv
│   │   ├── olist_order_items_dataset.csv
│   │   ├── olist_order_payments_dataset.csv
│   │   ├── olist_products_dataset.csv
│   │   ├── product_category_name_translation.csv
│   │   ├── olist_customers_dataset.csv
│   │   ├── olist_order_reviews_dataset.csv
│   │   ├── olist_sellers_dataset.csv
│   │   └── olist_geolocation_dataset.csv
│   ├── silver/                 # Table nettoyée produite par le pipeline
│   │   └── silver_orders.csv
│   └── gold/                   # Tables dbt (schéma en étoile)
├── dbt/                        # Modèles dbt (couche Gold)
├── notebooks/
│   └── olist_silver_orders_etl.ipynb   # Notebook EDA + transformation
├── scripts/
│   └── build_silver_orders.py          # Pipeline Python autonome
├── DECISIONS.md                # Choix techniques documentés
├── data_dictionary.md          # Dictionnaire de données
└── README.md                   # Ce fichier
```

---

## Architecture Medallion

```
BRONZE  →  9 CSV bruts (data/raw/)
SILVER  →  silver_orders.csv (96 478 lignes, 13 colonnes)
GOLD    →  fact_orders + dim_date + dim_product + dim_region + dim_payment
SERVING →  Dashboard streamlit (4 pages)
```

---

## Installation et exécution

### Prérequis

- Python 3.10+
- pip
- Git

### Lancement en 4 commandes

```bash
# 1. Aller dans le dossier du projet
cd Dashboard_Analytics_d-une_Marketplace_Multi-Catgories-main

# 2. Installer les dépendances
pip install pandas numpy streamlit plotly

# 3. Lancer le pipeline ETL (génère silver_orders.csv)
python scripts/build_silver_orders.py

# 4. Lancer le dashboard
streamlit run dashboard/app.py
```

---

## Table silver_orders — Résultat

| Colonne | Type | Description |
|---|---|---|
| Order_ID | String | Identifiant unique de la commande |
| Date | Date | Date d'achat (YYYY-MM-DD) |
| Quantity | Integer | Nombre d'articles par commande |
| Unit_Price | Float | Prix moyen unitaire en R$ |
| Revenue_Prod | Float | CA hors frais de port (R$) |
| Total_Revenue | Float | CA port inclus (R$) |
| Freight | Float | Frais de port (R$) |
| Category | String | Catégorie produit (anglais) |
| Category_Group | String | Famille de catégorie (10 groupes) |
| Region | String | Macro-région brésilienne (5 valeurs) |
| Region_State | String | Code état brésilien (27 valeurs) |
| Payment_Method | String | Mode de paiement |

**Métriques clés :**
- Lignes : 96 478 commandes livrées
- Période : 2016-09-15 → 2018-08-29
- CA produits : R$ 13 221 498
- CA total : R$ 15 170 548
- Panier moyen : R$ 137

---

## Choix techniques

Tous les choix de transformation sont documentés dans [`DECISIONS.md`](./DECISIONS.md) :

1. Filtrage sur `order_status = 'delivered'`
2. Définition de `Total_Revenue` (deux approches)
3. Calcul de `Quantity` via `COUNT(order_item_id)`
4. Imputation des catégories non traduites
5. Regroupement des 72 catégories en 10 familles
6. Macro-régions brésiliennes IBGE
7. Traitement des paiements multiples

---

## Dashboard Streamlit

4 pages analytiques :

| Page | Objectif |
|---|---|
| Page 1 — Vue Exécutive | KPIs globaux : CA, commandes, panier moyen |
| Page 2 — Produits | Top catégories, prix vs volume |
| Page 3 — Saisonnalité | Tendances mensuelles, heatmap semaine × catégorie |
| Page 4 — Géographie | Carte Brésil, performance par macro-région |

---


## Stack technique

| Couche | Outil |
|---|---|
| Langage | Python 3.10+ |
| Transformation | pandas 2.0+ |
| Notebooks | Google Colab / Jupyter |
| Modélisation | dbt-core |
| Dashboard | streamlit |
| Versionning | Git + GitHub |

---

## Dataset source

- **Nom :** Brazilian E-Commerce Public Dataset by Olist
- **Source :** [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Commande de téléchargement :**

```bash
kaggle datasets download -d olistbr/brazilian-ecommerce
```

---

*Projet réalisé par:
 -**EL KIHAL KHAOULA**
 -**EL HAJOUI MARIAM**
 -**HARBOULI HAJAR**
 -**OUARADI ASSIYA***
