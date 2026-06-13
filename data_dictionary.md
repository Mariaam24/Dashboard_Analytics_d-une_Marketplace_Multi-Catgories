# Dictionnaire de Données — silver_orders

**Projet 1 — Dashboard Analytics Marketplace Olist**  
**Table :** `silver_orders`  
**Source :** 9 fichiers CSV Olist (Kaggle — olistbr/brazilian-ecommerce)  
**Lignes :** 96 478 commandes livrées  
**Colonnes :** 12  
**Période :** 2016 — 2018  

---

## 1. Description de la table

`silver_orders` est la table analytique centrale construite par le pipeline ETL Python.
Elle consolide en une seule table plate toutes les colonnes nécessaires pour les 4 pages du dashboard,
issues de 5 jointures successives depuis les CSV sources:
 ##### olist_orders_dataset.csv
  ##### olist_order_items_dataset.csv
  ##### olist_products_dataset.csv
  ##### olist_customers_dataset.csv
  ##### olist_order_payments_dataset.csv

**Périmètre :** uniquement les commandes avec `order_status = 'delivered'`  
**Taille fichier :** ~11 MB  

---

## 2. Dictionnaire des colonnes

### order_id

| Attribut | Valeur |
|---|---|
| **Type** | String (VARCHAR) |
| **Nulls** | 0 |
| **Valeurs uniques** | 96 478 (clé primaire) |
| **Source** | `olist_orders_dataset.csv` → colonne `order_id` |

**Description :** Identifiant unique de chaque commande. UUID hexadécimal de 32 caractères.  
Exemple : `e481f51cbdc54678b7cc49136f2d6af7`

**Note :** Clé primaire de la table — aucun doublon toléré.

---

### date

| Attribut | Valeur |
|---|---|
| **Type** | String → Date (YYYY-MM-DD) |
| **Nulls** | 0 |
| **Min** | 2016-09-15 |
| **Max** | 2018-08-29 |
| **Source** | `olist_orders_dataset.csv` → colonne `order_purchase_timestamp` tronquée |


**Description :** Date d'achat de la commande au format (YYYY-MM-DD).  
Dérivée de `order_purchase_timestamp` en supprimant l'heure (pas d'analyse intra-journalière).

---

### quantity

| Attribut | Valeur |
|---|---|
| **Type** | Integer (int64) |
| **Nulls** | 0 |
| **Valeurs uniques** | 17 valeurs distinctes (1 à 21) |
| **Min** | 1 |
| **Max** | 21 |
| **Moyenne** | 1.14 |
| **Source** | `olist_order_items_dataset.csv` → `COUNT(order_item_id) GROUP BY order_id` |

**Description :** Nombre total d'articles dans la commande.

**Piège classique :** `order_item_id` dans olist_order_items est un **rang séquentiel**
(1, 2, 3...), pas une quantité. La valeur correcte est obtenue par `COUNT(order_item_id)`.  
80% des étudiants font l'erreur d'utiliser `order_item_id` directement.

**Décision DECISIONS.md :** Quantity = COUNT(order_item_id) GROUP BY order_id.

---

### unit_price

| Attribut | Valeur |
|---|---|
| **Type** | Float (float64) |
| **Nulls** | 0 |
| **Valeurs uniques** | 6 957 |
| **Min** | R$ 0.85 |
| **Max** | R$ 6 735.00 |
| **Moyenne** | R$ 125.23 |
| **Source** | `olist_order_items_dataset.csv` → `AVG(price) GROUP BY order_id` |
| **Unité** | BRL (Real brésilien — R$) |

**Description :** Prix unitaire moyen des articles de la commande en R$.  
Pour les commandes avec un seul article, `unit_price = price`.
Pour les commandes multi-articles, c'est la moyenne des prix.

---

### revenue_prod

| Attribut | Valeur |
|---|---|
| **Type** | Float (float64) |
| **Nulls** | 0 |
| **Min** | R$ 0.85 |
| **Max** | R$ 13 440.00 |
| **Moyenne** | R$ 137.04 |
| **Total** | R$ 13 221 498 |
| **Source** | `olist_order_items_dataset.csv` → `SUM(price) GROUP BY order_id` |
| **Unité** | BRL (Real brésilien — R$) |

**Description :** Chiffre d'affaires produits de la commande, **hors frais de port**.  
Correspond à `Unit_Price × Quantity` pour les commandes mono-article.

**Décision DECISIONS.md :** Deux définitions de Total_Revenue coexistent.
`revenue_prod` = Option A (SUM price, hors port) — utilisée pour les KPIs CA marchandises.

---

### freight

| Attribut | Valeur |
|---|---|
| **Type** | Float (float64) |
| **Nulls** | 0 |
| **Min** | R$ 0.00 |
| **Max** | R$ 1 794.96 |
| **Moyenne** | R$ 22.79 |
| **Total** | R$ 2 198 276 |
| **Source** | `olist_order_items_dataset.csv` → `SUM(freight_value) GROUP BY order_id` |
| **Unité** | BRL (Real brésilien — R$) |

**Description :** Total des frais de port de la commande (revenue_prod + freight).

---

### category

| Attribut | Valeur |
|---|---|
| **Type** | String (VARCHAR) |
| **Nulls** | 0 |
| **Valeurs uniques** | 74 catégories |
| **Source** | `olist_products_dataset.csv` + `product_category_name_translation.csv` |

**Description :** Catégorie produit en anglais après traduction depuis le portugais.  
Granularité fine — utilisée comme proxy de "Product Name" (absent dans Olist).

**Valeurs spéciales :**
- `Uncategorized` : ~610 produits avec `product_category_name = NULL`
- `Gaming` : imputation manuelle pour `pc_gamer`
- `Kitchen Appliances` : imputation manuelle pour `portateis_cozinha_e_preparadores_de_alimentos`


---

### category_group

| Attribut | Valeur |
|---|---|
| **Type** | String (VARCHAR) |
| **Nulls** | 0 |
| **Valeurs uniques** | 10 familles |
| **Source** | Dérivée de `category` par regroupement manuel |

**Description :** Regroupement des 72 catégories en 10 familles pour la lisibilité du dashboard.
Créée car 72 valeurs distinctes rendent les légendes illisibles.

**Valeurs possibles :**

| Famille | Catégories incluses |
|---|---|
| Home & Living | bed_bath_table, furniture_decor, housewares, garden_tools |
| Electronics | computers_accessories, telephony, electronics, consoles_games |
| Fashion & Accessories | watches_gifts, fashion_bags_accessories, fashion_shoes |
| Health & Beauty | health_beauty, perfumary |
| Sports & Leisure | sports_leisure |
| Auto & Industrial | auto, construction_tools_safety |
| Toys & Games | toys, Gaming |
| Books & Media | books_general_interest, books_technical, music, dvds_blu_ray |
| Food & Drink | food_drink, drinks, Kitchen Appliances |
| Other | Toutes les autres catégories non classifiées  |

---

### region

| Attribut | Valeur |
|---|---|
| **Type** | String (VARCHAR) |
| **Nulls** | 0 |
| **Valeurs uniques** | 5 macro-régions |
| **Source** | `olist_customers_dataset.csv` → `customer_state` → mapping MACRO_REGIOES |

**Description :** Macro-région officielle IBGE (Institut Géographique Brésilien) déduite de l'état client.

**Valeurs possibles :**

| Valeur | États inclus | CA réel | Part |
|---|---|---|---|
| Sudeste | SP, RJ, MG, ES | R$ 8 648 410 | 65.4% |
| Sul | RS, SC, PR | R$ 1 901 973 | 14.4% |
| Nordeste | BA, PE, CE, MA, RN, AL, SE, PB, PI | R$ 1 497 084 | 11.3% |
| Centro-Oeste | DF, GO, MT, MS | R$ 846 957 | 6.4% |
| Norte | AM, PA, RO, AC, AP, RR, TO | R$ 327 075 | 2.5% |

**Décision DECISIONS.md :** Regroupement selon le découpage officiel IBGE.

---

### region_state

| Attribut | Valeur |
|---|---|
| **Type** | String (VARCHAR) |
| **Nulls** | 0 |
| **Valeurs uniques** | 27 états brésiliens |
| **Source** | `olist_customers_dataset.csv` → colonne `customer_state` |

**Description :** Code à 2 lettres de l'état brésilien du client.
Utilisée pour le drill-down géographique sur la carte du dashboard (Page 4).

**Exemples :** SP, RJ, MG, BA, RS, PR, DF, GO, AM...

---

### payment_method

| Attribut | Valeur |
|---|---|
| **Type** | String (VARCHAR) |
| **Nulls** | 0 |
| **Valeurs uniques** | 5 |
| **Source** | `olist_order_payments_dataset.csv` → `payment_type` (payment_sequential = 1) |

**Description :** Mode de paiement principal de la commande, traduit en anglais.

**Valeurs possibles :**

| Valeur | Source originale | Nb commandes | Part |
|---|---|---|---|
| Credit Card | credit_card | 74 303 | 77.0% |
| Bank Transfer | boleto | 19 191 | 19.9% |
| Voucher | voucher | 1 498 | 1.6% |
| Debit Card | debit_card | 1 485 | 1.5% |
| Unknown | Autres cas | 1 | 0.0% |

**Décision DECISIONS.md :** Seul `payment_sequential = 1` est conservé pour éviter
le double comptage des paiements mixtes (ex: 80% carte + 20% voucher).

---

### total_revenue

| Attribut | Valeur |
|---|---|
| **Type** | Float (float64) |
| **Nulls** | 0 |
| **Min** | R$ 0.01 |
| **Max** | R$ 13 664.08 |
| **Moyenne** | R$ 157.24 |
| **Total** | R$ 15 170 548 |
| **Source** | `olist_order_payments_dataset.csv` → `payment_value` (payment_sequential = 1) |
| **Unité** | BRL (Real brésilien — R$) |

**Description :** Chiffre d'affaires total de la commande, **frais de port inclus**.
Représente le flux d'argent réel encaissé.

**Décision DECISIONS.md :** Deux définitions de Total_Revenue :
- `revenue_prod` = Option A (hors port, R$ 13.2M) — pour les KPIs CA marchandises
- `total_revenue` = Option B (port inclus, R$ 15.2M) — pour le flux d'argent réel


---

## 3. Relations avec les tables Gold (dbt)

```
silver_orders
    ↓ fact_orders (clé : order_id)
        ├── dim_date    (clé : date_key)
        ├── dim_product (clé : product_key )
        ├── dim_region  (clé : region_key )
        └── dim_payment (clé : payment_key)
```
---
### fact_orders — Table de faits

| Colonne  | Colonne Silver | Type | Description |
|---|---|---|---|
| order_id | `order_id` | VARCHAR | Clé primaire |
| date_key | `date_key` | BIGINT | Clé étrangère → dim_date |
| product_key | `product_key` | BIGINT | Clé étrangère → dim_product |
| region_key | `region_key` | BIGINT | Clé étrangère → dim_region |
| — | `payment_key` | BIGINT | Clé étrangère → dim_payment |
| quantity | `quantity` | INTEGER | Nombre d'articles |
| price | `unit_price` | FLOAT | Prix unitaire moyen (R$) |
| revenue | `revenue_products` | FLOAT | CA hors port (R$) |

---

### dim_date

| Colonne | Type | Description |
|---|---|---|
| `date_key` | BIGINT | Clé primaire |
| `year` | INTEGER | Année: 2016, 2017, 2018 |
| `month` | INTEGER | Mois: 1 à 12 |
| `quarter` | INTEGER | Trimestre: 1 à 4 |
| `week` | INTEGER | Numéro de semaine  |
| `day_name` | VARCHAR | Nom du jour: Monday... Sunday |
| `is_weekend` | BOOLEAN | Samedi ou dimanche: True / False |

---

### dim_product

| Colonne | Type | Description |
|---|---|---|
| `product_key` | BIGINT | Clé primaire (HASH de category) |
| `category` | VARCHAR | Catégorie produit en anglais (74 valeurs) |
| `category_group` | VARCHAR | Famille de catégorie (10 familles) |
| `price_tier` | VARCHAR | Tranche de prix (Low / Medium / High) |

---

### dim_region

| Colonne | Type | Description |
|---|---|---|
|`region_key` | BIGINT | Clé primaire (HASH de region) |
| `region_name` | VARCHAR | Nom de la région 5 macro-régions IBGE |
| `continent` | VARCHAR | Continent |
| `zone` | VARCHAR | Zone géographique (27 états brésiliens) |

---

### dim_payment

| Colonne | Type | Description |
|---|---|---|
| `payment_key` | BIGINT | Clé primaire (HASH de payment_method) |
| `payment_method` | VARCHAR | Mode de paiement traduit |
| `payment_type` | VARCHAR | Type regroupé (Card / Transfer / Voucher) |

---
---

