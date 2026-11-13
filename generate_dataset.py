"""
Générateur de dataset synthétique pour la plateforme de commande intelligente.

Le dataset ne contient aucune donnée réelle :
clients, produits, commandes, échantillons et matières premières sont fictifs.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


# ============================================================
# 1. DOSSIERS DE SORTIE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
RAG_DIR = DATA_DIR / "rag"

RAW_DIR.mkdir(parents=True, exist_ok=True)
RAG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. DONNÉES SYNTHÉTIQUES STRUCTURÉES
# ============================================================

clients = [
    {
        "client_id": "CL-001",
        "company_name": "Maison Éclat",
        "segment": "PME",
        "country": "France",
        "industry": "Cosmétiques",
        "language": "fr",
        "account_level": "standard",
    },
    {
        "client_id": "CL-002",
        "company_name": "NutriPeak Foods",
        "segment": "ETI",
        "country": "France",
        "industry": "Boissons fonctionnelles",
        "language": "fr",
        "account_level": "premium",
    },
    {
        "client_id": "CL-003",
        "company_name": "Verde Home Care",
        "segment": "PME",
        "country": "Italie",
        "industry": "Produits ménagers",
        "language": "it",
        "account_level": "standard",
    },
    {
        "client_id": "CL-004",
        "company_name": "Northstar Beverages",
        "segment": "Grand compte",
        "country": "Allemagne",
        "industry": "Boissons",
        "language": "en",
        "account_level": "strategic",
    },
    {
        "client_id": "CL-005",
        "company_name": "Atelier Botanique",
        "segment": "PME",
        "country": "Belgique",
        "industry": "Parfumerie",
        "language": "fr",
        "account_level": "standard",
    },
]

products = [
    {
        "product_id": "PR-001",
        "reference": "FRG-101",
        "name": "Velours Floral",
        "domain": "Fragrance",
        "family": "Floral",
        "profile": "rose, pivoine, musc doux",
        "application": "savon",
        "markets": "France, Belgique, Allemagne",
        "status": "approved",
    },
    {
        "product_id": "PR-002",
        "reference": "FRG-102",
        "name": "Bois Santal Clair",
        "domain": "Fragrance",
        "family": "Boisé",
        "profile": "santal, cèdre, ambre doux",
        "application": "gel douche",
        "markets": "France, Belgique, Allemagne, Italie",
        "status": "approved",
    },
    {
        "product_id": "PR-003",
        "reference": "FRG-103",
        "name": "Éclat Agrumes",
        "domain": "Fragrance",
        "family": "Frais",
        "profile": "bergamote, citron, mandarine",
        "application": "savon",
        "markets": "France, Belgique, Allemagne, Italie",
        "status": "approved",
    },
    {
        "product_id": "PR-004",
        "reference": "FRG-104",
        "name": "Amande Réconfort",
        "domain": "Fragrance",
        "family": "Gourmand",
        "profile": "amande, tonka, vanille légère",
        "application": "savon premium",
        "markets": "France, Belgique, Italie",
        "status": "approved",
    },
    {
        "product_id": "PR-005",
        "reference": "FLV-201",
        "name": "Mangue Passion",
        "domain": "Flavor",
        "family": "Fruité",
        "profile": "mangue mûre, fruit de la passion, note tropicale",
        "application": "boisson protéinée",
        "markets": "France, Allemagne, Pays-Bas",
        "status": "approved",
    },
    {
        "product_id": "PR-006",
        "reference": "FLV-202",
        "name": "Citron Gingembre",
        "domain": "Flavor",
        "family": "Frais",
        "profile": "citron, gingembre, fraîcheur persistante",
        "application": "boisson fonctionnelle",
        "markets": "France, Allemagne, Pays-Bas, Belgique",
        "status": "approved",
    },
    {
        "product_id": "PR-007",
        "reference": "FLV-203",
        "name": "Vanille Amande",
        "domain": "Flavor",
        "family": "Gourmand",
        "profile": "vanille crémeuse, amande, biscuit",
        "application": "shake protéiné",
        "markets": "France, Belgique",
        "status": "restricted",
    },
    {
        "product_id": "PR-008",
        "reference": "FLV-204",
        "name": "Fruits Rouges Vifs",
        "domain": "Flavor",
        "family": "Fruité",
        "profile": "fraise, framboise, cassis",
        "application": "boisson énergétique",
        "markets": "France, Allemagne, Pays-Bas, Belgique",
        "status": "approved",
    },
]

raw_materials = [
    {
        "raw_material_id": "RM-001",
        "reference": "RM-FL-001",
        "name": "Extrait de rose",
        "type": "Extrait naturel",
        "origin": "France",
        "profile": "floral, rosé, élégant",
        "allergen": "oui",
        "regulatory_note": "Déclaration allergènes à vérifier",
        "status": "approved",
    },
    {
        "raw_material_id": "RM-002",
        "reference": "RM-WD-001",
        "name": "Essence de cèdre",
        "type": "Extrait naturel",
        "origin": "États-Unis",
        "profile": "boisé, sec, chaleureux",
        "allergen": "non",
        "regulatory_note": "Utilisation selon le dosage autorisé",
        "status": "approved",
    },
    {
        "raw_material_id": "RM-003",
        "reference": "RM-FR-001",
        "name": "Huile de bergamote",
        "type": "Extrait naturel",
        "origin": "Italie",
        "profile": "agrumes, frais, zesté",
        "allergen": "oui",
        "regulatory_note": "Contrôle de phototoxicité requis",
        "status": "restricted",
    },
    {
        "raw_material_id": "RM-004",
        "reference": "RM-FT-001",
        "name": "Arôme mangue",
        "type": "Arôme nature-identique",
        "origin": "Brésil",
        "profile": "fruité, tropical, mûr",
        "allergen": "non",
        "regulatory_note": "Conforme au marché européen",
        "status": "approved",
    },
    {
        "raw_material_id": "RM-005",
        "reference": "RM-FT-002",
        "name": "Arôme fruit de la passion",
        "type": "Arôme nature-identique",
        "origin": "Pérou",
        "profile": "fruité, acidulé, tropical",
        "allergen": "non",
        "regulatory_note": "Conforme au marché européen",
        "status": "approved",
    },
    {
        "raw_material_id": "RM-006",
        "reference": "RM-FR-002",
        "name": "Extrait de gingembre",
        "type": "Extrait naturel",
        "origin": "Inde",
        "profile": "épicé, frais, citronné",
        "allergen": "non",
        "regulatory_note": "Stabilité à vérifier dans les boissons",
        "status": "approved",
    },
]

orders = [
    {
        "order_id": "ORD-2024-001",
        "client_id": "CL-001",
        "order_date": "2024-02-15",
        "order_type": "sample",
        "status": "delivered",
        "amount_eur": 180,
        "delivery_date": "2024-02-28",
        "product_id": "PR-001",
        "quantity_kg": 5,
        "application": "savon",
        "brief": "senteur florale premium, propre et légèrement musquée",
    },
    {
        "order_id": "ORD-2024-002",
        "client_id": "CL-002",
        "order_date": "2024-03-10",
        "order_type": "pilot",
        "status": "delivered",
        "amount_eur": 4200,
        "delivery_date": "2024-04-03",
        "product_id": "PR-005",
        "quantity_kg": 25,
        "application": "boisson protéinée",
        "brief": "mangue passion, faible acidité et compatible avec une base protéinée",
    },
    {
        "order_id": "ORD-2024-003",
        "client_id": "CL-004",
        "order_date": "2024-06-22",
        "order_type": "reorder",
        "status": "delivered",
        "amount_eur": 18500,
        "delivery_date": "2024-07-12",
        "product_id": "PR-002",
        "quantity_kg": 120,
        "application": "gel douche",
        "brief": "profil boisé élégant, plus doux que la version précédente",
    },
    {
        "order_id": "ORD-2025-001",
        "client_id": "CL-001",
        "order_date": "2025-01-17",
        "order_type": "reorder",
        "status": "delivered",
        "amount_eur": 2600,
        "delivery_date": "2025-02-08",
        "product_id": "PR-001",
        "quantity_kg": 18,
        "application": "savon",
        "brief": "même profil que la commande précédente",
    },
    {
        "order_id": "ORD-2025-002",
        "client_id": "CL-002",
        "order_date": "2025-02-11",
        "order_type": "reorder",
        "status": "delivered",
        "amount_eur": 8700,
        "delivery_date": "2025-03-04",
        "product_id": "PR-005",
        "quantity_kg": 60,
        "application": "boisson protéinée",
        "brief": "plus fruité, moins acide et stable dans une boisson protéinée",
    },
    {
        "order_id": "ORD-2025-003",
        "client_id": "CL-005",
        "order_date": "2025-05-19",
        "order_type": "sample",
        "status": "in_transit",
        "amount_eur": 240,
        "delivery_date": "2025-06-02",
        "product_id": "PR-004",
        "quantity_kg": 3,
        "application": "savon premium",
        "brief": "amande douce, chaude, naturelle et peu sucrée",
    },
    {
        "order_id": "ORD-2025-004",
        "client_id": "CL-004",
        "order_date": "2025-09-14",
        "order_type": "reorder",
        "status": "confirmed",
        "amount_eur": 22400,
        "delivery_date": "2025-10-10",
        "product_id": "PR-002",
        "quantity_kg": 180,
        "application": "gel douche",
        "brief": "same as previous order, slightly fresher",
    },
]

samples = [
    {
        "sample_id": "SMP-001",
        "client_id": "CL-001",
        "request_date": "2024-02-05",
        "product_id": "PR-001",
        "quantity_kg": 5,
        "brief": "senteur premium pour une gamme de savons artisanaux",
        "status": "delivered",
        "commercial_potential": "medium",
    },
    {
        "sample_id": "SMP-002",
        "client_id": "CL-002",
        "request_date": "2024-02-25",
        "product_id": "PR-005",
        "quantity_kg": 2,
        "brief": "mangue passion, faible acidité, compatible avec une base protéinée",
        "status": "converted",
        "commercial_potential": "high",
    },
    {
        "sample_id": "SMP-003",
        "client_id": "CL-005",
        "request_date": "2025-05-12",
        "product_id": "PR-004",
        "quantity_kg": 3,
        "brief": "profil amande chaud, naturel et non trop sucré",
        "status": "in_transit",
        "commercial_potential": "medium",
    },
]


# ============================================================
# 3. CRÉATION DES CSV
# ============================================================

def write_csv(filename: str, rows: list[dict]) -> None:
    """Crée un fichier CSV à partir d'une liste de dictionnaires."""
    file_path = RAW_DIR / filename

    with file_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


write_csv("clients.csv", clients)
write_csv("products.csv", products)
write_csv("raw_materials.csv", raw_materials)
write_csv("orders.csv", orders)
write_csv("samples.csv", samples)


# ============================================================
# 4. TRANSFORMATION DES DONNÉES EN DOCUMENTS RAG
# ============================================================

client_by_id = {client["client_id"]: client for client in clients}
product_by_id = {product["product_id"]: product for product in products}

documents = []

# Documents clients.
for client in clients:
    documents.append(
        {
            "id": f"client_{client['client_id']}",
            "text": (
                f"CLIENT | ID : {client['client_id']}. "
                f"Entreprise : {client['company_name']}. "
                f"Segment : {client['segment']}. "
                f"Pays : {client['country']}. "
                f"Secteur : {client['industry']}. "
                f"Langue préférée : {client['language']}. "
                f"Niveau de compte : {client['account_level']}."
            ),
            "metadata": {
                "type": "client",
                "client_id": client["client_id"],
            },
        }
    )

# Documents produits.
for product in products:
    documents.append(
        {
            "id": f"product_{product['product_id']}",
            "text": (
                f"PRODUIT | ID interne : {product['product_id']}. "
                f"Référence : {product['reference']}. "
                f"Nom : {product['name']}. "
                f"Domaine : {product['domain']}. "
                f"Famille sensorielle : {product['family']}. "
                f"Profil sensoriel : {product['profile']}. "
                f"Application principale : {product['application']}. "
                f"Marchés disponibles : {product['markets']}. "
                f"Statut réglementaire : {product['status']}."
            ),
            "metadata": {
                "type": "product",
                "product_id": product["product_id"],
                "domain": product["domain"],
            },
        }
    )

# Documents matières premières.
for raw_material in raw_materials:
    documents.append(
        {
            "id": f"raw_material_{raw_material['raw_material_id']}",
            "text": (
                f"MATIÈRE PREMIÈRE | ID interne : {raw_material['raw_material_id']}. "
                f"Référence : {raw_material['reference']}. "
                f"Nom : {raw_material['name']}. "
                f"Type : {raw_material['type']}. "
                f"Origine : {raw_material['origin']}. "
                f"Profil sensoriel : {raw_material['profile']}. "
                f"Allergène : {raw_material['allergen']}. "
                f"Note réglementaire : {raw_material['regulatory_note']}. "
                f"Statut : {raw_material['status']}."
            ),
            "metadata": {
                "type": "raw_material",
                "raw_material_id": raw_material["raw_material_id"],
            },
        }
    )

# Documents commandes.
for order in orders:
    client = client_by_id[order["client_id"]]
    product = product_by_id[order["product_id"]]

    documents.append(
        {
            "id": f"order_{order['order_id']}",
            "text": (
                f"COMMANDE | ID : {order['order_id']}. "
                f"Client : {client['company_name']} ({order['client_id']}). "
                f"Date de commande : {order['order_date']}. "
                f"Type : {order['order_type']}. "
                f"Statut : {order['status']}. "
                f"Montant : {order['amount_eur']} EUR. "
                f"Livraison prévue ou réalisée : {order['delivery_date']}. "
                f"Produit : {product['reference']} — {product['name']} ({order['product_id']}). "
                f"Quantité : {order['quantity_kg']} kg. "
                f"Application : {order['application']}. "
                f"Brief client : {order['brief']}."
            ),
            "metadata": {
                "type": "order",
                "order_id": order["order_id"],
                "client_id": order["client_id"],
                "product_id": order["product_id"],
            },
        }
    )

# Documents échantillons.
for sample in samples:
    client = client_by_id[sample["client_id"]]
    product = product_by_id[sample["product_id"]]

    documents.append(
        {
            "id": f"sample_{sample['sample_id']}",
            "text": (
                f"ÉCHANTILLON | ID : {sample['sample_id']}. "
                f"Client : {client['company_name']} ({sample['client_id']}). "
                f"Date de demande : {sample['request_date']}. "
                f"Produit : {product['reference']} — {product['name']} ({sample['product_id']}). "
                f"Quantité : {sample['quantity_kg']} kg. "
                f"Brief : {sample['brief']}. "
                f"Statut : {sample['status']}. "
                f"Potentiel commercial : {sample['commercial_potential']}."
            ),
            "metadata": {
                "type": "sample",
                "sample_id": sample["sample_id"],
                "client_id": sample["client_id"],
            },
        }
    )


# ============================================================
# 5. CRÉATION DES DOCUMENTS POUR LE RAG
# ============================================================

# JSONL : format structuré, utile pour une évolution future.
jsonl_path = RAG_DIR / "documents.jsonl"

with jsonl_path.open("w", encoding="utf-8") as file:
    for document in documents:
        file.write(json.dumps(document, ensure_ascii=False) + "\n")

# Texte : compatible immédiatement avec ingest.py du repository fourni.
text_path = BASE_DIR / "givaudan_data.txt"

with text_path.open("w", encoding="utf-8") as file:
    file.write("Plateforme de commande intelligente — Dataset synthétique\n\n")

    for index, document in enumerate(documents, start=1):
        file.write(f"Chapter {index}: {document['id']}\n")
        file.write(document["text"])
        file.write("\n\n")


# ============================================================
# 6. CONFIRMATION
# ============================================================

print("Dataset créé avec succès.")
print(f"Nombre de documents RAG : {len(documents)}")
print(f"CSV créés dans : {RAW_DIR}")
print(f"JSONL créé dans : {jsonl_path}")
print(f"Corpus RAG compatible avec ingest.py : {text_path}")
