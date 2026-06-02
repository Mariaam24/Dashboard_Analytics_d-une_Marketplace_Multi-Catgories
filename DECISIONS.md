# DECISIONS.md — Projet 1 Olist
> Ce fichier documente tous les choix techniques et métier effectués durant la construction de `silver_orders`.
> Chaque décision explique le problème rencontré, les options disponibles, le choix retenu et son impact.

---

## DÉCISION 1 — Filtrage sur `order_status = 'delivered'`

### Problème
La table `olist_orders` contient 99 441 commandes avec 8 statuts différents :

| Statut | Nombre |
|---|---|
| delivered | 96 478 |
| shipped | 1 107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

### Options disponibles
- **Option A** : Garder toutes les commandes (99 441 lignes)
- **Option B** : Garder uniquement `delivered` (96 478 lignes)

### Choix retenu
**Option B — uniquement `delivered`**

### Justification
- Seules les commandes livrées génèrent un **chiffre d'affaires réel encaissé**
- Les commandes `canceled` ou `unavailable` ne doivent pas être comptabilisées dans les KPIs CA
- Les commandes `shipped` ou `processing` sont en cours — leur montant n'est pas encore confirmé

### Impact en volume
- Commandes conservées : **96 478** (97,0% du total)
- Commandes exclues : **2 963** (3,0% du total)

### Cas d'usage des statuts exclus
Les commandes annulées peuvent être utiles pour une analyse séparée (taux d'annulation par région, par catégorie), hors scope du Projet 1.

---

## DÉCISION 2 — Définition de `Total_Revenue`

### Problème
Il existe deux façons de calculer le chiffre d'affaires dans Olist :

| Approche | Formule | Frais de port | Source |
|---|---|---|---|
| Option A — Revenue Produits | `SUM(price)` par order_id | ❌ Exclus | `olist_order_items` |
| Option B — Revenue Total | `SUM(payment_value)` par order_id | ✅ Inclus | `olist_order_payments` |

### Choix retenu
**Les deux colonnes ont été créées :**
- `Revenue_Prod` = `SUM(price)` — CA marchandises hors port
- `Total_Revenue` = `SUM(payment_value)` — flux d'argent réel port inclus

### Justification
- `Revenue_Prod` est cohérent avec `Unit_Price × Quantity` — utile pour les analyses produits
- `Total_Revenue` représente ce que le client a réellement payé — utile pour les KPIs financiers globaux
- Conserver les deux permet d'analyser la **part des frais de port** dans le CA total

### Valeurs observées sur le dataset
- CA produits total : R$ ~13,5M
- CA total (port inclus) : R$ ~15,4M
- Frais de port représentent environ **12-14%** du CA total

### Précaution appliquée
Pour éviter le double comptage des paiements multiples, `Total_Revenue` est calculé uniquement sur `payment_sequential = 1` (voir Décision 5).

---

## DÉCISION 3 — Calcul de `Quantity`

### Problème
La colonne `order_item_id` dans `olist_order_items` est un **rang séquentiel** (1, 2, 3...) et non une quantité.

Exemple concret :
```
order_id       | order_item_id | product_id | price
abc123...      |      1        | prod_A     | 29.90
abc123...      |      2        | prod_B     | 45.00
abc123...      |      3        | prod_B     | 45.00
```
→ Cette commande contient 3 articles, pas "order_item_id = 3 articles du même produit"

### Erreur classique (à ne pas faire)
```python
# FAUX — utiliser order_item_id directement comme quantité
df['Quantity'] = df['order_item_id']
```

### Calcul correct retenu
```python
# CORRECT — compter le nombre de lignes par commande
Quantity = COUNT(order_item_id) GROUP BY order_id
```

### Justification
Le vrai nombre d'articles par commande est le **nombre de lignes** associées à un `order_id`, pas la valeur de `order_item_id`.

### Résultat observé
- Quantité minimale : 1 article
- Quantité maximale : 21 articles
- Quantité moyenne : ~1.1 article par commande (la majorité des commandes = 1 article)

---

## DÉCISION 4 — Traitement des catégories non traduites

### Problème
La table `product_category_name_translation.csv` contient 71 traductions. Certaines catégories de `olist_products` n'ont pas d'entrée dans cette table.

### Catégories sans traduction identifiées

| Catégorie (portugais) | Traduction retenue | Justification |
|---|---|---|
| `pc_gamer` | `Gaming` | Terme anglais universel, compris sans traduction |
| `portateis_cozinha_e_preparadores_de_alimentos` | `Kitchen Appliances` | Appareils de cuisine portables et préparateurs alimentaires |
| `NULL` (610 produits) | `Uncategorized` | Données manquantes — impossible de déduire la catégorie |

### Méthode appliquée
```python
manual_map = {
    'pc_gamer': 'Gaming',
    'portateis_cozinha_e_preparadores_de_alimentos': 'Kitchen Appliances'
}
products_tr['product_category_name_english'] = (
    products_tr['product_category_name_english']
    .fillna(products_tr['product_category_name'].map(manual_map))
    .fillna('Uncategorized')
)
```

### Impact
- 610 produits classés `Uncategorized` — représentent une part minoritaire du CA
- `Uncategorized` est visible dans le dashboard comme catégorie à part entière

---

## DÉCISION 5 — Regroupement des 72 catégories en familles (`Category_Group`)

### Problème
72 catégories distinctes en anglais sont trop nombreuses pour un dashboard lisible (légende illisible, graphiques encombrés).

### Solution retenue
Création d'une colonne `Category_Group` avec **10 familles** :

| Category_Group | Catégories incluses |
|---|---|
| Health & Beauty | health_beauty, perfumaria |
| Home & Living | bed_bath_table, furniture_decor, housewares, garden_tools |
| Sports & Leisure | sports_leisure |
| Toys & Games | toys, Gaming |
| Electronics | computers_accessories, telephony, electronics, consoles_games |
| Fashion & Accessories | watches_gifts, fashion_bags_accessories, fashion_shoes, fashion_male_clothing |
| Auto & Industrial | auto, construction_tools_safety |
| Food & Drink | food_drink, drinks, Kitchen Appliances |
| Books & Media | books_general_interest, books_technical, music, dvds_blu_ray |
| Other | Toutes les autres catégories non listées ci-dessus |

### Justification
- Les familles suivent une logique **retail standard** internationale
- `Other` regroupe les catégories orphelines — à surveiller si leur part est significative
- `Category` (72 valeurs) est conservée pour les analyses drill-down

---

## DÉCISION 6 — Macro-régions brésiliennes

### Problème
`customer_state` contient les codes des **27 états brésiliens** — trop nombreux pour une visualisation géographique lisible.

### Solution retenue
Regroupement en **5 macro-régions officielles de l'IBGE** (Institut Géographique Brésilien) :

| Macro-région | États | Part du CA estimée |
|---|---|---|
| Sudeste | SP, RJ, MG, ES | ~58% |
| Sul | RS, SC, PR | ~15% |
| Nordeste | BA, PE, CE, MA, RN, AL, SE, PB, PI | ~13% |
| Norte | AM, PA, RO, AC, AP, RR, TO | ~4% |
| Centro-Oeste | DF, GO, MT, MS | ~10% |

### Colonnes produites
- `Region` → macro-région (5 valeurs) — pour les visuels agrégés
- `Region_State` → code état brut (27 valeurs) — pour le drill-down carte Power BI

### Justification
Le découpage IBGE est le standard officiel brésilien utilisé dans les analyses économiques et e-commerce. Il permet de comparer avec des benchmarks sectoriels publics.

---

## DÉCISION 7 — Paiements multiples (`payment_sequential`)

### Problème
Une même commande peut avoir plusieurs lignes dans `olist_order_payments` quand le client paie en mode mixte (ex: 80% carte + 20% voucher). Une jointure directe sur `order_id` sans filtrage entraîne une **multiplication des lignes** dans `silver_orders`.

### Exemple
```
order_id  | payment_sequential | payment_type | payment_value
xyz789... |         1          | credit_card  |   180.00
xyz789... |         2          | voucher      |    20.00
```

### Choix retenu
Garder uniquement `payment_sequential = 1` (paiement principal) pour :
- Éviter le double comptage
- Identifier le **mode de paiement dominant** de la commande
- Simplifier la jointure (1 ligne par commande)

### Limitation acceptée
Le montant `Total_Revenue` ne capture que le paiement principal pour les commandes mixtes. Dans les cas de paiement mixte (~quelques %), le montant peut être légèrement sous-estimé.

### Commandes multi-paiements observées
Environ quelques milliers de commandes ont `payment_sequential > 1` — représentent une part minoritaire du dataset.

---

## RÉSUMÉ DES DÉCISIONS

| # | Décision | Impact volume | Complexité |
|---|---|---|---|
| 1 | Filtrage `delivered` | -2 963 lignes (3%) | Faible |
| 2 | Deux colonnes Revenue | Aucun | Faible |
| 3 | Quantity = COUNT | Calcul correct vs faux | Élevée |
| 4 | Imputation 3 catégories | ~610 nulls traités | Moyenne |
| 5 | 72 → 10 Category_Group | Lisibilité dashboard | Moyenne |
| 6 | 27 états → 5 régions | Lisibilité dashboard | Faible |
| 7 | payment_sequential = 1 | Évite doublons | Moyenne |

---

*Document rédigé dans le cadre du Projet 1 — Dataset Olist Brazilian E-Commerce*
*Pipeline construit avec Python / pandas sur Google Colab*
*Table produite : `silver_orders.csv` — 96 478 lignes | 13 colonnes*
