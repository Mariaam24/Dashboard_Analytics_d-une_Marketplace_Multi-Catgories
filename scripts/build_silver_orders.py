

import pandas as pd
import os

# ─────────────────────────────────────────────
# 0. CHARGEMENT DES FICHIERS
# ─────────────────────────────────────────────
DATA_DIR = "data/raw/"

print("=" * 55)
print("CHARGEMENT DES 9 FICHIERS CSV...")
print("=" * 55)

orders    = pd.read_csv(os.path.join(DATA_DIR, "olist_orders_dataset.csv"))
items     = pd.read_csv(os.path.join(DATA_DIR, "olist_order_items_dataset.csv"))
payments  = pd.read_csv(os.path.join(DATA_DIR, "olist_order_payments_dataset.csv"))
products  = pd.read_csv(os.path.join(DATA_DIR, "olist_products_dataset.csv"))
transl    = pd.read_csv(os.path.join(DATA_DIR, "product_category_name_translation.csv"))
customers = pd.read_csv(os.path.join(DATA_DIR, "olist_customers_dataset.csv"))

print(f"  orders    : {orders.shape[0]:>7} lignes")
print(f"  items     : {items.shape[0]:>7} lignes")
print(f"  payments  : {payments.shape[0]:>7} lignes")
print(f"  products  : {products.shape[0]:>7} lignes")
print(f"  customers : {customers.shape[0]:>7} lignes")


# ─────────────────────────────────────────────
# EXPLORATION RAPIDE (diagnostics)
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("EXPLORATION — DIAGNOSTICS")
print("=" * 55)

print(f"\n[orders] Statuts disponibles :")
print(orders['order_status'].value_counts().to_string())

print(f"\n[orders] Nulls par colonne :")
print(orders.isnull().sum()[orders.isnull().sum() > 0].to_string())

print(f"\n[items] order_item_id — exemple (ce n'est PAS une quantité) :")
print(items[items['order_id'] == items['order_id'].iloc[0]][['order_id','order_item_id','price']].to_string(index=False))

print(f"\n[payments] Types de paiement :")
print(payments['payment_type'].value_counts().to_string())

print(f"\n[products] Nulls sur product_category_name : {products['product_category_name'].isnull().sum()}")

print(f"\n[payments] Commandes avec plusieurs paiements :")
multi = payments.groupby('order_id')['payment_sequential'].max()
print(f"  Max payment_sequential = {multi.max()} | Commandes multi-paiements = {(multi > 1).sum()}")


# ─────────────────────────────────────────────
# ÉTAPE 1 — TABLE ANCRE : orders
# Filtrer sur 'delivered' + créer colonne Date
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("ÉTAPE 1 — TABLE ANCRE (orders livrées)")
print("=" * 55)

silver = orders[orders['order_status'] == 'delivered'].copy()
silver['Date'] = pd.to_datetime(silver['order_purchase_timestamp']).dt.date
silver = silver[['order_id', 'customer_id', 'Date']].rename(columns={'order_id': 'Order_ID'})

print(f"  Commandes totales      : {len(orders)}")
print(f"  Commandes 'delivered'  : {len(silver)} (filtrées)")
print(f"  Exclues                : {len(orders) - len(silver)}")


# ─────────────────────────────────────────────
# ÉTAPE 2 — JOINTURE ITEMS
# Quantity (COUNT), Unit_Price (AVG), Revenue_Prod (SUM)
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("ÉTAPE 2 — JOINTURE ITEMS (Quantity, Prix, CA)")
print("=" * 55)

# ATTENTION : order_item_id = rang, PAS une quantité → COUNT()
items_agg = items.groupby('order_id').agg(
    Quantity      = ('order_item_id', 'count'),   # vrai nombre d'articles
    Unit_Price    = ('price', 'mean'),             # prix moyen par article
    Revenue_Prod  = ('price', 'sum'),              # CA hors frais de port
    Freight       = ('freight_value', 'sum')       # frais de port (optionnel)
).reset_index()

silver = silver.merge(items_agg, left_on='Order_ID', right_on='order_id', how='left')
silver.drop(columns='order_id', inplace=True)

print(f"  Lignes après jointure items : {len(silver)}")
print(f"  Nulls Quantity              : {silver['Quantity'].isnull().sum()}")
print(f"  Quantité moyenne par cmd    : {silver['Quantity'].mean():.2f}")


# ─────────────────────────────────────────────
# ÉTAPE 3 — JOINTURE PRODUCTS + TRADUCTION
# Category en anglais, imputée, groupée
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("ÉTAPE 3 — JOINTURE PRODUCTS + TRADUCTION")
print("=" * 55)

# Jointure products avec table de traduction
products_tr = products.merge(transl, on='product_category_name', how='left')

# Imputation manuelle des 3 catégories sans traduction
manual_map = {
    'pc_gamer': 'Gaming',
    'portateis_cozinha_e_preparadores_de_alimentos': 'Kitchen Appliances'
}
products_tr['product_category_name_english'] = (
    products_tr['product_category_name_english']
    .fillna(products_tr['product_category_name'].map(manual_map))
    .fillna('Uncategorized')
)

print(f"  Catégories distinctes (anglais) : {products_tr['product_category_name_english'].nunique()}")
print(f"  Dont 'Uncategorized'            : {(products_tr['product_category_name_english'] == 'Uncategorized').sum()}")

# Récupérer la catégorie du premier item de chaque commande
items_cat = items[['order_id', 'product_id']].drop_duplicates(subset='order_id')
items_cat = items_cat.merge(
    products_tr[['product_id', 'product_category_name_english']],
    on='product_id', how='left'
).rename(columns={'product_category_name_english': 'Category'})

silver = silver.merge(items_cat[['order_id', 'Category']], left_on='Order_ID', right_on='order_id', how='left')
silver.drop(columns='order_id', inplace=True)

# Regroupement en ~10 familles (Category_Group)
CATEGORY_GROUPS = {
    'health_beauty'              : 'Health & Beauty',
    'perfumaria'                 : 'Health & Beauty',
    'bed_bath_table'             : 'Home & Living',
    'furniture_decor'            : 'Home & Living',
    'housewares'                 : 'Home & Living',
    'garden_tools'               : 'Home & Living',
    'sports_leisure'             : 'Sports & Leisure',
    'toys'                       : 'Toys & Games',
    'Gaming'                     : 'Toys & Games',
    'computers_accessories'      : 'Electronics',
    'telephony'                  : 'Electronics',
    'electronics'                : 'Electronics',
    'consoles_games'             : 'Electronics',
    'watches_gifts'              : 'Fashion & Accessories',
    'fashion_bags_accessories'   : 'Fashion & Accessories',
    'fashion_shoes'              : 'Fashion & Accessories',
    'fashion_male_clothing'      : 'Fashion & Accessories',
    'auto'                       : 'Auto & Industrial',
    'construction_tools_safety'  : 'Auto & Industrial',
    'food_drink'                 : 'Food & Drink',
    'drinks'                     : 'Food & Drink',
    'Kitchen Appliances'         : 'Food & Drink',
    'books_general_interest'     : 'Books & Media',
    'books_technical'            : 'Books & Media',
    'music'                      : 'Books & Media',
    'dvds_blu_ray'               : 'Books & Media',
}
silver['Category_Group'] = silver['Category'].map(CATEGORY_GROUPS).fillna('Other')

print(f"  Groupes Category_Group : {silver['Category_Group'].nunique()}")
print(silver['Category_Group'].value_counts().head(5).to_string())


# ─────────────────────────────────────────────
# ÉTAPE 4 — JOINTURE CUSTOMERS : Region
# 27 états → 5 macro-régions officielles IBGE
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("ÉTAPE 4 — JOINTURE CUSTOMERS (Region)")
print("=" * 55)

MACRO_REGIOES = {
    'SP':'Sudeste','RJ':'Sudeste','MG':'Sudeste','ES':'Sudeste',
    'RS':'Sul',    'SC':'Sul',    'PR':'Sul',
    'BA':'Nordeste','PE':'Nordeste','CE':'Nordeste','MA':'Nordeste',
    'RN':'Nordeste','AL':'Nordeste','SE':'Nordeste','PB':'Nordeste','PI':'Nordeste',
    'AM':'Norte',  'PA':'Norte',  'RO':'Norte',  'AC':'Norte',
    'AP':'Norte',  'RR':'Norte',  'TO':'Norte',
    'DF':'Centro-Oeste','GO':'Centro-Oeste','MT':'Centro-Oeste','MS':'Centro-Oeste'
}

customers['Region']       = customers['customer_state'].map(MACRO_REGIOES)
customers['Region_State'] = customers['customer_state']

silver = silver.merge(
    customers[['customer_id', 'Region', 'Region_State']],
    on='customer_id', how='left'
)

print(f"  Répartition par macro-région :")
print(silver['Region'].value_counts().to_string())


# ─────────────────────────────────────────────
# ÉTAPE 5 — JOINTURE PAYMENTS
# Payment_Method (traduit) + Total_Revenue
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("ÉTAPE 5 — JOINTURE PAYMENTS")
print("=" * 55)

# Garder uniquement le paiement principal (évite le double comptage)
pay_main = payments[payments['payment_sequential'] == 1].copy()

pay_main['Payment_Method'] = pay_main['payment_type'].map({
    'credit_card' : 'Credit Card',
    'boleto'      : 'Bank Transfer',
    'voucher'     : 'Voucher',
    'debit_card'  : 'Debit Card'
}).fillna('Other')

pay_agg = pay_main.groupby('order_id').agg(
    Payment_Method = ('Payment_Method', 'first'),
    Total_Revenue  = ('payment_value', 'sum')
).reset_index()

silver = silver.merge(pay_agg, left_on='Order_ID', right_on='order_id', how='left')
silver.drop(columns='order_id', inplace=True)

print(f"  Répartition Payment_Method :")
print(silver['Payment_Method'].value_counts().to_string())


# ─────────────────────────────────────────────
# VÉRIFICATIONS FINALES (tests qualité)
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("VÉRIFICATIONS QUALITÉ")
print("=" * 55)

errors = []

if silver['Quantity'].isnull().sum() > 0:
    errors.append(f"   Nulls sur Quantity : {silver['Quantity'].isnull().sum()}")
else:
    print("   Quantity — aucun null")

if (silver['Quantity'] <= 0).sum() > 0:
    errors.append(f"   Quantity <= 0 : {(silver['Quantity'] <= 0).sum()} lignes")
else:
    print("   Quantity — toutes > 0")

if (silver['Revenue_Prod'] <= 0).sum() > 0:
    errors.append(f"   Revenue_Prod <= 0 : {(silver['Revenue_Prod'] <= 0).sum()} lignes")
else:
    print("   Revenue_Prod — toutes > 0")

valid_regions = {'Sudeste', 'Sul', 'Nordeste', 'Norte', 'Centro-Oeste'}
invalid = silver[~silver['Region'].isin(valid_regions)]['Region'].unique()
if len(invalid) > 0:
    errors.append(f"   Régions invalides : {invalid}")
else:
    print("   Region — toutes valides")

valid_payments = {'Credit Card', 'Bank Transfer', 'Voucher', 'Debit Card', 'Other'}
invalid_pay = silver[~silver['Payment_Method'].isin(valid_payments)]['Payment_Method'].unique()
if len(invalid_pay) > 0:
    errors.append(f"   Payment_Method invalides : {invalid_pay}")
else:
    print("   Payment_Method — toutes valides")

if errors:
    print("\n  ERREURS DÉTECTÉES :")
    for e in errors:
        print(e)
else:
    print("\n  Tous les tests passent !")


# ─────────────────────────────────────────────
# RÉSUMÉ FINAL
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("SILVER_ORDERS — RÉSUMÉ FINAL")
print("=" * 55)
print(f"  Lignes totales    : {len(silver)}")
print(f"  Colonnes          : {len(silver.columns)}")
print(f"\n  Colonnes produites :")
for col in silver.columns:
    nulls = silver[col].isnull().sum()
    print(f"    {col:<20} nulls={nulls}")

print(f"\n  CA total (Revenue_Prod)  : R$ {silver['Revenue_Prod'].sum():>15,.2f}")
print(f"  CA total (Total_Revenue) : R$ {silver['Total_Revenue'].sum():>15,.2f}")
print(f"  Période                  : {silver['Date'].min()} → {silver['Date'].max()}")


# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("EXPORT")
print("=" * 55)

silver.to_csv("silver_orders.csv", index=False)
print("   silver_orders.csv exporté !")

try:
    silver.to_parquet("silver_orders.parquet", index=False)
    print("   silver_orders.parquet exporté !")
except Exception:
    print("    Parquet non disponible (pip install pyarrow)")

print("\n" + "=" * 55)

print("=" * 55)