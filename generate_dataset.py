"""
Générateur de dataset synthétique pour la plateforme B2B de création et de
commande d'arômes et de fragrances.

Le dataset couvre le parcours complet de la plateforme :
  1. clients professionnels ;
  2. catalogue intelligent (arômes alimentaires et fragrances) ;
  3. matières premières ;
  4. projets de création personnalisée (brief, préférences, suivi d'avancement) ;
  5. échantillons et rectifications (V1, V2, V3…) avec retours clients ;
  6. commandes finales et suivi de livraison ;
  7. FAQ / règles de fonctionnement de la plateforme.

Toutes les données sont FICTIVES : aucun client, aucune formule ni aucune
commande réelle de Givaudan.

Usage :
    python generate_dataset.py

Sorties :
    data/raw/*.csv              tables structurées (une par entité)
    data/rag/documents.jsonl    documents RAG avec métadonnées
    givaudan_data.txt           corpus texte compatible avec ingest.py
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path


# ============================================================
# 1. DOSSIERS DE SORTIE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
RAG_DIR = DATA_DIR / "rag"

# Date de référence du dataset (« aujourd'hui » pour la démo).
REFERENCE_DATE = "2026-11-12"


def rows(columns: list[str], values: list[tuple]) -> list[dict]:
    """Transforme une liste de tuples en liste de dictionnaires."""
    result = []
    for value in values:
        if len(value) != len(columns):
            raise ValueError(f"Ligne mal formée ({len(value)} champs) : {value}")
        result.append(dict(zip(columns, value)))
    return result


# ============================================================
# 2. CLIENTS
# ============================================================

clients = rows(
    ["client_id", "company_name", "segment", "country", "industry", "language", "account_level"],
    [
        ("CL-001", "Maison Éclat", "PME", "France", "Cosmétiques", "fr", "standard"),
        ("CL-002", "NutriPeak Foods", "ETI", "France", "Boissons fonctionnelles", "fr", "premium"),
        ("CL-003", "Verde Home Care", "PME", "Italie", "Produits ménagers", "it", "standard"),
        ("CL-004", "Northstar Beverages", "Grand compte", "Allemagne", "Boissons", "en", "strategic"),
        ("CL-005", "Atelier Botanique", "PME", "Belgique", "Parfumerie", "fr", "standard"),
        ("CL-006", "Laiterie des Alpes", "ETI", "France", "Produits laitiers", "fr", "premium"),
        ("CL-007", "Lumina Laundry", "Grand compte", "Espagne", "Détergents", "es", "strategic"),
        ("CL-008", "Biscuiterie Ondine", "PME", "France", "Biscuiterie", "fr", "standard"),
        ("CL-009", "Kinetic Sports Nutrition", "ETI", "Pays-Bas", "Nutrition sportive", "en", "premium"),
        ("CL-010", "Casa Aurora Cosmetics", "PME", "Espagne", "Cosmétiques", "es", "standard"),
    ],
)


# ============================================================
# 3. CATALOGUE : ARÔMES (FLV) ET FRAGRANCES (FRG)
# ============================================================
# intensity      : faible / moyenne / forte
# naturalness    : 100 % naturel / naturel / nature-identique / % d'origine naturelle
# allergens      : allergènes alimentaires (arômes) ou allergènes parfumants
#                  à déclarer (fragrances) ; « aucun » si rien à déclarer
# price_eur_kg   : prix catalogue indicatif hors transport
# moq_kg         : quantité minimale de commande
# lead_time_days : délai de fabrication en jours ouvrés (hors transport)

PRODUCT_COLUMNS = [
    "product_id", "reference", "name", "domain", "family", "profile",
    "applications", "intensity", "naturalness", "certifications", "allergens",
    "stability", "dosage", "price_eur_kg", "moq_kg", "lead_time_days",
    "markets", "status",
]

products = rows(
    PRODUCT_COLUMNS,
    [
        # ---------------- Arômes alimentaires ----------------
        ("PR-001", "FLV-201", "Mangue Passion", "Arôme", "Fruité",
         "mangue mûre, fruit de la passion, note tropicale",
         "boisson protéinée, smoothie, yaourt", "moyenne", "naturel",
         "vegan, halal", "aucun", "stable de pH 3 à 7, résiste à la pasteurisation",
         "0,10 à 0,20 %", 48, 5, 15, "France, Allemagne, Pays-Bas", "disponible"),
        ("PR-002", "FLV-202", "Citron Gingembre", "Arôme", "Agrume",
         "zeste de citron, gingembre frais, piquant léger",
         "boisson fonctionnelle, eau aromatisée, kombucha", "forte", "100 % naturel",
         "vegan, halal, bio", "aucun", "stable de pH 2,5 à 6",
         "0,05 à 0,15 %", 62, 5, 15, "France, Allemagne, Pays-Bas, Belgique", "disponible"),
        ("PR-003", "FLV-203", "Vanille Bourbon Crème", "Arôme", "Gourmand",
         "vanille de Madagascar, crème fraîche, légère note boisée",
         "yaourt, crème dessert, glace", "moyenne", "100 % naturel",
         "halal, casher", "lait (support lacté)", "résiste à la chaleur jusqu'à 90 °C",
         "0,20 à 0,40 %", 95, 10, 20, "France, Belgique, Allemagne", "disponible"),
        ("PR-004", "FLV-204", "Fraise des Bois", "Arôme", "Fruité",
         "fraise mûre, sous-bois, légère acidité",
         "yaourt, boisson lactée, confiserie", "moyenne", "naturel",
         "vegan, halal", "aucun", "stable de pH 3,5 à 7, compatible UHT",
         "0,15 à 0,30 %", 41, 5, 15, "France, Belgique, Espagne, Italie", "disponible"),
        ("PR-005", "FLV-205", "Fruits Rouges Vifs", "Arôme", "Fruité",
         "fraise, framboise, cassis",
         "boisson énergétique, soda, boisson sans sucre", "forte", "nature-identique",
         "vegan, halal", "aucun", "stable de pH 2,5 à 5, compatible édulcorants (sucralose, stévia)",
         "0,08 à 0,15 %", 28, 10, 10, "France, Allemagne, Pays-Bas, Belgique", "disponible"),
        ("PR-006", "FLV-206", "Chocolat Noisette", "Arôme", "Gourmand",
         "cacao torréfié, noisette grillée, praliné",
         "shake protéiné, biscuit, barre céréalière", "forte", "naturel",
         "halal", "fruits à coque (noisette)", "résiste à la cuisson jusqu'à 180 °C",
         "0,30 à 0,50 %", 37, 10, 20, "France, Belgique, Pays-Bas", "disponible"),
        ("PR-007", "FLV-207", "Vanille Amande", "Arôme", "Gourmand",
         "vanille crémeuse, amande, biscuit",
         "shake protéiné", "moyenne", "nature-identique",
         "vegan", "fruits à coque (amande)", "stable de pH 4 à 7",
         "0,20 à 0,30 %", 33, 10, 20, "France, Belgique",
         "restreint (vente limitée à la France et à la Belgique, revue réglementaire en cours pour les autres pays)"),
        ("PR-008", "FLV-208", "Pêche Abricot", "Arôme", "Fruité",
         "pêche blanche, abricot sec, miel léger",
         "yaourt, thé glacé, compote", "faible", "100 % naturel",
         "vegan, halal, bio", "aucun", "stable de pH 3 à 6",
         "0,10 à 0,20 %", 54, 5, 15, "France, Italie, Espagne", "disponible"),
        ("PR-009", "FLV-209", "Caramel Beurre Salé", "Arôme", "Gourmand",
         "caramel cuit, beurre, fleur de sel",
         "biscuit, crème dessert, café prêt-à-boire", "forte", "naturel",
         "halal", "lait", "version standard : perte d'intensité au-delà de 180 °C",
         "0,20 à 0,40 %", 44, 10, 20, "France, Belgique", "disponible"),
        ("PR-010", "FLV-210", "Menthe Glaciale", "Arôme", "Frais",
         "menthe poivrée, effet froid, eucalyptus discret",
         "chewing-gum, confiserie, boisson", "forte", "naturel",
         "vegan, halal, casher", "aucun", "très stable (chaleur et pH)",
         "0,05 à 0,10 %", 39, 5, 10, "France, Allemagne, Espagne, Italie, Pays-Bas", "disponible"),
        ("PR-011", "FLV-211", "Coco Ananas", "Arôme", "Tropical",
         "noix de coco, ananas rôti",
         "smoothie, boisson végétale, glace", "moyenne", "nature-identique",
         "vegan", "aucun", "stable de pH 3,5 à 7",
         "0,15 à 0,25 %", 31, 10, 15, "France, Espagne, Pays-Bas", "disponible"),
        ("PR-012", "FLV-212", "Citron Yuzu Zéro Sucre", "Arôme", "Agrume",
         "yuzu, citron vert, amertume douce",
         "boisson sans sucre, eau pétillante", "moyenne", "100 % naturel",
         "vegan, halal, bio", "aucun", "stable de pH 2,5 à 5, compatible stévia et sucralose",
         "0,08 à 0,12 %", 88, 5, 25, "France, Allemagne, Pays-Bas", "disponible"),
        ("PR-013", "FLV-213", "Cerise Amarena", "Arôme", "Fruité",
         "cerise noire, légère amande amère",
         "yaourt, glace, soda, boisson lactée", "moyenne", "naturel",
         "halal", "aucun", "stable de pH 3,5 à 7",
         "0,15 à 0,25 %", 46, 5, 15, "France, Italie, Allemagne", "disponible"),
        ("PR-014", "FLV-214", "Masquant Protéine", "Arôme", "Fonctionnel",
         "neutralise les notes amères et métalliques des protéines",
         "shake protéiné, barre protéinée, boisson protéinée", "faible", "naturel",
         "vegan, halal", "aucun", "stable à la chaleur et à la pasteurisation",
         "0,05 à 0,10 %", 72, 5, 20, "France, Allemagne, Pays-Bas, Belgique", "disponible"),
        ("PR-015", "FLV-215", "Matcha Lait d'Avoine", "Arôme", "Végétal",
         "thé matcha, céréale douce, note lactée végétale",
         "boisson végétale, latte prêt-à-boire", "faible", "100 % naturel",
         "vegan, bio", "avoine (traces de gluten possibles)", "compatible UHT",
         "0,20 à 0,30 %", 76, 10, 30, "France, Allemagne",
         "en développement (échantillons uniquement, pas encore commandable)"),
        ("PR-016", "FLV-216", "Fumé Barbecue", "Arôme", "Salé",
         "fumée de hêtre, paprika, note grillée",
         "sauce, chips, plat préparé", "forte", "naturel",
         "vegan, halal", "aucun", "résiste à la cuisson et à la friture",
         "0,10 à 0,30 %", 35, 10, 15, "France, Belgique, Espagne", "disponible"),
        # ---------------- Fragrances ----------------
        ("PR-017", "FRG-101", "Velours Floral", "Fragrance", "Floral",
         "rose, pivoine, musc doux",
         "savon, gel douche, crème corps", "moyenne", "15 % d'origine naturelle",
         "vegan", "linalol, citronellol, géraniol", "stable de pH 5 à 10",
         "0,5 à 1,5 %", 58, 5, 20, "France, Belgique, Allemagne", "disponible"),
        ("PR-018", "FRG-102", "Bois Santal Clair", "Fragrance", "Boisé",
         "santal, cèdre, ambre doux",
         "gel douche, parfum d'ambiance, bougie", "moyenne", "30 % d'origine naturelle",
         "vegan", "coumarine", "stable de pH 4 à 9",
         "0,5 à 1,5 %", 64, 5, 20, "France, Belgique, Allemagne, Italie", "disponible"),
        ("PR-019", "FRG-103", "Éclat Agrumes", "Fragrance", "Hespéridé",
         "bergamote, citron, mandarine",
         "savon, shampooing, déodorant", "forte", "60 % d'origine naturelle",
         "vegan", "limonène, citral", "stable de pH 4 à 9",
         "0,5 à 1,0 %", 49, 5, 15, "France, Belgique, Allemagne, Italie", "disponible"),
        ("PR-020", "FRG-104", "Amande Réconfort", "Fragrance", "Gourmand",
         "amande, fève tonka, vanille légère",
         "savon premium, lait corps", "faible", "25 % d'origine naturelle",
         "vegan", "coumarine", "stable de pH 5 à 9",
         "0,5 à 1,0 %", 52, 5, 20, "France, Belgique, Italie", "disponible"),
        ("PR-021", "FRG-105", "Fraîcheur Linge Pur", "Fragrance", "Propre",
         "coton propre, aldéhydes, muguet, musc blanc",
         "lessive liquide, adoucissant", "forte", "5 % d'origine naturelle",
         "aucune", "hexyl cinnamal, linalol", "stable de pH 7 à 11, stable en milieu tensioactif",
         "0,3 à 0,8 %", 22, 50, 25, "France, Espagne, Italie, Allemagne", "disponible"),
        ("PR-022", "FRG-106", "Brise Marine", "Fragrance", "Aquatique",
         "notes marines, sel, algue, bois flotté",
         "lessive, nettoyant multi-surfaces, gel douche", "moyenne", "10 % d'origine naturelle",
         "vegan", "limonène", "stable de pH 6 à 11",
         "0,3 à 0,8 %", 26, 25, 20, "France, Espagne, Italie", "disponible"),
        ("PR-023", "FRG-107", "Lavande de Provence", "Fragrance", "Aromatique",
         "lavande vraie, romarin, herbes sèches",
         "nettoyant ménager écologique, savon, bougie", "moyenne", "85 % d'origine naturelle",
         "vegan, compatible Ecolabel et cosmétique bio", "linalol, limonène, coumarine",
         "stable de pH 4 à 10", "0,4 à 1,0 %", 68, 10, 20, "France, Italie, Belgique", "disponible"),
        ("PR-024", "FRG-108", "Fleur d'Oranger Lumineuse", "Fragrance", "Floral",
         "néroli, fleur d'oranger, miel",
         "parfum fin, brume corps", "forte", "40 % d'origine naturelle",
         "vegan", "linalol, géraniol", "adaptée aux eaux de parfum (concentration 10 à 15 %)",
         "10 à 15 % en parfum fin", 145, 2, 25, "France, Belgique, Espagne", "disponible"),
        ("PR-025", "FRG-109", "Vétiver Fumé", "Fragrance", "Boisé",
         "vétiver, encens, cuir léger",
         "parfum fin masculin, bougie", "forte", "50 % d'origine naturelle",
         "vegan", "eugénol", "adaptée aux eaux de parfum",
         "10 à 15 % en parfum fin", 160, 2, 30, "France, Belgique",
         "restreint (mise à jour IFRA en cours, approvisionnement en vétiver tendu)"),
        ("PR-026", "FRG-110", "Thé Vert Hypoallergénique", "Fragrance", "Frais",
         "thé vert, concombre, musc propre",
         "crème visage, lingettes bébé, soins peaux sensibles", "faible", "20 % d'origine naturelle",
         "vegan", "aucun allergène parfumant à déclarer", "stable de pH 4 à 8",
         "0,1 à 0,3 %", 74, 5, 20, "France, Belgique, Allemagne, Italie, Espagne", "disponible"),
        ("PR-027", "FRG-111", "Citron Vert Dégraissant", "Fragrance", "Hespéridé",
         "citron vert, pamplemousse, menthe",
         "liquide vaisselle, nettoyant cuisine", "forte", "30 % d'origine naturelle",
         "vegan", "limonène, citral", "stable de pH 3 à 11",
         "0,3 à 0,6 %", 24, 50, 15, "France, Italie, Espagne", "disponible"),
        ("PR-028", "FRG-112", "Coco Monoï", "Fragrance", "Solaire",
         "noix de coco, fleur de tiaré, vanille",
         "crème solaire, huile corps, gel douche", "moyenne", "35 % d'origine naturelle",
         "vegan", "benzyl salicylate, coumarine", "stable de pH 5 à 8",
         "0,3 à 0,8 %", 55, 5, 20, "France, Espagne", "disponible"),
        ("PR-029", "FRG-113", "Ambre Cachemire", "Fragrance", "Oriental",
         "ambre, bois cachemire, vanille, patchouli",
         "parfum fin, bougie, parfum d'ambiance", "forte", "30 % d'origine naturelle",
         "vegan", "coumarine, linalol", "adaptée aux eaux de parfum et aux bougies",
         "10 à 15 % en parfum fin", 132, 2, 25, "France, Belgique, Allemagne", "disponible"),
        ("PR-030", "FRG-114", "Pomme Verte Croquante", "Fragrance", "Fruité",
         "pomme verte, poire, feuilles vertes",
         "shampooing, gel douche, lessive", "moyenne", "10 % d'origine naturelle",
         "vegan", "hexyl cinnamal", "stable de pH 4 à 10",
         "0,3 à 0,8 %", 29, 25, 15, "France, Allemagne, Espagne, Italie, Pays-Bas", "disponible"),
    ],
)


# ============================================================
# 4. MATIÈRES PREMIÈRES
# ============================================================

raw_materials = rows(
    ["raw_material_id", "reference", "name", "type", "origin", "profile",
     "allergen", "regulatory_note", "used_in", "status"],
    [
        ("RM-001", "RM-FL-001", "Extrait de rose", "Extrait naturel", "Bulgarie",
         "floral, rosé, élégant", "citronellol, géraniol", "Déclaration des allergènes requise",
         "PR-017", "disponible"),
        ("RM-002", "RM-WD-001", "Essence de cèdre", "Huile essentielle", "États-Unis",
         "boisé, sec, chaleureux", "aucun", "Aucune restriction particulière",
         "PR-018", "disponible"),
        ("RM-003", "RM-CT-001", "Huile essentielle de bergamote", "Huile essentielle", "Italie",
         "hespéridé, pétillant, légèrement amer", "limonène", "Qualité sans furocoumarines (FCF) obligatoire",
         "PR-019", "disponible"),
        ("RM-004", "RM-GM-001", "Absolue de fève tonka", "Absolue", "Venezuela",
         "gourmand, amandé, chaud", "coumarine", "Dosage encadré par les normes IFRA",
         "PR-018, PR-020", "disponible"),
        ("RM-005", "RM-GM-002", "Extrait de vanille Bourbon", "Extrait naturel", "Madagascar",
         "vanillé, crémeux, boisé", "aucun", "Origine et traçabilité certifiées",
         "PR-003, PR-007", "disponible (prix volatil)"),
        ("RM-006", "RM-SP-001", "Extrait CO2 de gingembre", "Extrait naturel", "Inde",
         "piquant, frais, citronné", "aucun", "Aucune restriction particulière",
         "PR-002", "disponible"),
        ("RM-007", "RM-FR-001", "Jus concentré de mangue", "Concentré de fruit", "Inde",
         "fruité, tropical, sucré", "aucun", "Contrôle pesticides à chaque lot",
         "PR-001", "disponible"),
        ("RM-008", "RM-AR-001", "Huile essentielle de lavande vraie", "Huile essentielle", "France",
         "aromatique, herbacé, frais", "linalol, limonène", "Certifiée bio, compatible Ecolabel",
         "PR-023", "disponible"),
        ("RM-009", "RM-SY-001", "Musc blanc", "Molécule de synthèse", "Synthèse",
         "musqué, propre, poudré", "aucun", "Biodégradabilité validée",
         "PR-017, PR-021, PR-026", "disponible"),
        ("RM-010", "RM-VG-001", "Extrait de thé matcha", "Extrait naturel", "Japon",
         "végétal, herbacé, umami", "aucun", "Contrôle de la caféine résiduelle",
         "PR-015", "disponible en petites quantités"),
        ("RM-011", "RM-FR-002", "Huile essentielle de menthe poivrée", "Huile essentielle", "Inde",
         "mentholé, froid, vif", "aucun", "Teneur en pulégone limitée par la réglementation arômes",
         "PR-010", "disponible"),
        ("RM-012", "RM-FL-002", "Huile essentielle de néroli", "Huile essentielle", "Tunisie",
         "floral, lumineux, hespéridé", "linalol", "Déclaration des allergènes requise",
         "PR-024", "disponible"),
        ("RM-013", "RM-WD-002", "Huile essentielle de vétiver", "Huile essentielle", "Haïti",
         "boisé, terreux, fumé", "aucun", "Approvisionnement tendu : délai supplémentaire de 15 jours",
         "PR-025", "tension d'approvisionnement"),
        ("RM-014", "RM-GM-003", "Extrait de cacao torréfié", "Extrait naturel", "Côte d'Ivoire",
         "cacaoté, torréfié, amer", "aucun", "Filière cacao durable certifiée",
         "PR-006", "disponible"),
    ],
)


# ============================================================
# 5. PROJETS DE CRÉATION PERSONNALISÉE
# ============================================================
# Étapes du tableau de bord (suivi en temps réel) et avancement associé.

PROJECT_STAGES = {
    "Brief reçu": 10,
    "Formulation": 25,
    "Échantillon envoyé": 40,
    "Retour client": 50,
    "Rectification": 60,
    "Validé": 75,
    "Production": 85,
    "Expédition": 95,
    "Livré": 100,
    "Annulé": 0,
}

projects = rows(
    ["project_id", "client_id", "title", "product_type", "domain", "brief",
     "flavor_or_scent", "intensity", "naturalness", "constraints",
     "base_product_id", "created_date", "current_version", "stage",
     "next_step", "next_step_date", "project_manager"],
    [
        ("PJ-001", "CL-002", "Shake protéiné Mangue Passion", "boisson protéinée", "Arôme",
         "Boisson protéinée prête à boire au goût mangue-passion, peu acide, sans arrière-goût de protéine.",
         "mangue, fruit de la passion", "moyenne", "naturel", "vegan, faible acidité, stable à la pasteurisation",
         "PR-001", "2026-05-20", "V3", "Livré",
         "Projet terminé ; réassort en cours avec la commande ORD-2026-004", "2026-11-20", "Camille Roux"),
        ("PJ-002", "CL-006", "Yaourt brassé vanille naturelle", "yaourt", "Arôme",
         "Yaourt brassé premium à la vanille, goût crémeux et rond, étiquetage arôme naturel.",
         "vanille", "moyenne", "100 % naturel", "étiquette « arôme naturel », halal",
         "PR-003", "2026-08-05", "V2", "Production",
         "Fin de production de la commande ORD-2026-005", "2026-11-25", "Hugo Martin"),
        ("PJ-003", "CL-007", "Lessive liquide fraîcheur longue durée", "lessive", "Fragrance",
         "Lessive liquide avec une odeur de linge propre fleuri qui reste perceptible sur le linge sec.",
         "linge propre, fleuri, musc léger", "forte", "pas d'exigence", "pH 9, coût fragrance inférieur à 25 €/kg, rémanence sur linge sec",
         "PR-021", "2026-08-18", "V3 (en formulation)", "Rectification",
         "Envoi de l'échantillon V3 (note musquée réduite, rémanence conservée)", "2026-11-20", "Inès Garcia"),
        ("PJ-004", "CL-001", "Savon artisanal floral premium", "savon", "Fragrance",
         "Savon saponifié à froid haut de gamme, senteur florale élégante et légèrement musquée.",
         "rose, pivoine, musc", "moyenne", "pas d'exigence", "vegan, compatible saponification à froid",
         "PR-017", "2026-04-28", "V1", "Livré",
         "Réassort en cours avec la commande ORD-2026-008", "2026-12-01", "Camille Roux"),
        ("PJ-005", "CL-008", "Biscuit sablé caramel beurre salé", "biscuit", "Arôme",
         "Sablé pur beurre au caramel beurre salé ; l'arôme doit rester intense après cuisson.",
         "caramel, beurre salé", "forte", "naturel", "cuisson à 190 °C, halal",
         "PR-009", "2026-09-30", "V1", "Retour client",
         "Formulation d'une V2 thermostable (encapsulation) puis envoi de l'échantillon V2", "2026-11-21", "Hugo Martin"),
        ("PJ-006", "CL-009", "Boisson énergétique fruits rouges zéro sucre", "boisson énergétique", "Arôme",
         "Boisson énergétique sans sucre au goût fruits rouges intense, compatible sucralose.",
         "fraise, framboise, cassis", "forte", "pas d'exigence", "zéro sucre, compatible sucralose, halal",
         "PR-005", "2026-10-15", "V1", "Échantillon envoyé",
         "Attente du retour client sur l'échantillon V1", "2026-11-19", "Lucas Bernard"),
        ("PJ-007", "CL-005", "Eau de parfum fleur d'oranger", "parfum", "Fragrance",
         "Eau de parfum florale lumineuse autour de la fleur d'oranger, pas trop sucrée.",
         "fleur d'oranger, néroli", "forte", "au moins 30 % d'origine naturelle", "vegan, concentration 12 %",
         "PR-024", "2026-06-10", "V2", "Livré",
         "Projet terminé", "2026-08-29", "Inès Garcia"),
        ("PJ-008", "CL-003", "Nettoyant multi-surfaces écologique lavande", "nettoyant ménager", "Fragrance",
         "Nettoyant multi-surfaces écologique avec une lavande authentique.",
         "lavande", "moyenne", "au moins 80 % d'origine naturelle", "compatible Ecolabel",
         "PR-023", "2026-09-01", "V1", "Production",
         "Préparation de la commande ORD-2026-006", "2026-11-28", "Lucas Bernard"),
        ("PJ-009", "CL-004", "Eau pétillante yuzu sans sucre", "boisson", "Arôme",
         "Eau pétillante aromatisée sans sucre au yuzu, fraîche et peu amère.",
         "yuzu, citron vert", "moyenne", "100 % naturel", "zéro sucre, bio, vegan",
         "PR-012", "2026-07-20", "V2", "Expédition",
         "Livraison de la commande ORD-2026-007", "2026-11-16", "Camille Roux"),
        ("PJ-010", "CL-010", "Crème visage peaux sensibles", "crème cosmétique", "Fragrance",
         "Crème visage pour peaux sensibles, parfum frais et léger sans allergène à déclarer.",
         "thé vert, frais", "faible", "pas d'exigence", "aucun allergène parfumant à déclarer, hypoallergénique",
         "PR-026", "2026-10-01", "V2 (en formulation)", "Rectification",
         "Envoi de l'échantillon V2 avec un dosage plus perceptible", "2026-11-19", "Inès Garcia"),
        ("PJ-011", "CL-006", "Boisson végétale matcha avoine", "boisson végétale", "Arôme",
         "Boisson végétale à l'avoine au goût matcha doux, positionnement bio.",
         "matcha, avoine", "faible", "100 % naturel", "bio, vegan, compatible UHT",
         "PR-015", "2026-10-30", "aucune (formulation V1 en cours)", "Formulation",
         "Envoi de l'échantillon V1", "2026-11-24", "Hugo Martin"),
        ("PJ-012", "CL-004", "Soda cerise", "soda", "Arôme",
         "Soda à la cerise noire pour une nouvelle gamme.",
         "cerise noire", "moyenne", "naturel", "halal",
         "PR-013", "2026-03-25", "V1", "Annulé",
         "Aucune : projet annulé par le client (abandon de la gamme soda)", "2026-05-05", "Lucas Bernard"),
    ],
)


# ============================================================
# 6. ÉCHANTILLONS ET RECTIFICATIONS (V1, V2, V3…)
# ============================================================

samples = rows(
    ["sample_id", "project_id", "version", "sent_date", "quantity_kg",
     "changes", "client_feedback", "score_10", "decision"],
    [
        ("SMP-001", "PJ-001", "V1", "2026-06-10", 2,
         "Formulation initiale : FLV-201 à 0,15 % et masquant FLV-214 à 0,05 %.",
         "Trop acide en bouche et arrière-goût de protéine encore perceptible.", 5, "À modifier"),
        ("SMP-002", "PJ-001", "V2", "2026-07-02", 2,
         "Acidité réduite (pH ajusté à 6,2) et masquant FLV-214 porté à 0,08 %.",
         "Acidité correcte et plus d'arrière-goût, mais la mangue manque d'intensité.", 7, "À modifier"),
        ("SMP-003", "PJ-001", "V3", "2026-07-24", 2,
         "Intensité de la note mangue augmentée de 20 %.",
         "Parfait, conforme au brief.", 9, "Validé"),
        ("SMP-004", "PJ-002", "V1", "2026-08-20", 1,
         "FLV-203 dosé à 0,30 %.",
         "Trop boisé, manque de rondeur crémeuse.", 6, "À modifier"),
        ("SMP-005", "PJ-002", "V2", "2026-09-10", 1,
         "Note boisée réduite, note crème renforcée.",
         "Très bon équilibre, validé par le panel interne du client.", 9, "Validé"),
        ("SMP-006", "PJ-003", "V1", "2026-09-01", 2,
         "FRG-105 dosé à 0,5 %.",
         "Bonne odeur à l'ouverture du flacon, mais presque plus rien sur le linge sec.", 5, "À modifier"),
        ("SMP-007", "PJ-003", "V2", "2026-09-29", 2,
         "Ajout de fixateurs musqués, dosage porté à 0,6 %.",
         "Rémanence nettement meilleure, mais la note musquée est trop dominante.", 7, "À modifier"),
        ("SMP-008", "PJ-004", "V1", "2026-05-12", 1,
         "FRG-101 version standard.",
         "Exactement le profil recherché.", 9, "Validé"),
        ("SMP-009", "PJ-005", "V1", "2026-10-14", 1,
         "FLV-209 dosé à 0,30 %.",
         "Bon goût dans la pâte crue, mais l'arôme s'affaiblit nettement après la cuisson à 190 °C.", 6, "À modifier"),
        ("SMP-010", "PJ-006", "V1", "2026-11-05", 2,
         "FLV-205 en version sans sucre, compatible sucralose.",
         "Pas encore de retour : en attente de l'avis du client.", None, "En attente du retour client"),
        ("SMP-011", "PJ-007", "V1", "2026-07-01", 0.5,
         "FRG-108 en concentration 12 %.",
         "Trop sucré : la note miel écrase le néroli.", 6, "À modifier"),
        ("SMP-012", "PJ-007", "V2", "2026-07-22", 0.5,
         "Note miel réduite, néroli renforcé.",
         "Lumineux et élégant, validé.", 9, "Validé"),
        ("SMP-013", "PJ-008", "V1", "2026-09-15", 1,
         "FRG-107, formule à 85 % d'origine naturelle.",
         "Conforme : odeur de lavande authentique.", 8, "Validé"),
        ("SMP-014", "PJ-009", "V1", "2026-08-05", 2,
         "FLV-212 dosé à 0,10 %.",
         "Le yuzu est trop amer.", 6, "À modifier"),
        ("SMP-015", "PJ-009", "V2", "2026-08-26", 2,
         "Amertume réduite, citron vert renforcé.",
         "Validé pour le lancement.", 9, "Validé"),
        ("SMP-016", "PJ-010", "V1", "2026-10-20", 0.5,
         "FRG-110 dosé à 0,15 %.",
         "Parfum trop discret, presque imperceptible après application.", 5, "À modifier"),
        ("SMP-017", "PJ-012", "V1", "2026-04-10", 2,
         "FLV-213 dosé à 0,20 %.",
         "Profil apprécié, mais le client a abandonné sa gamme soda.", 8, "Projet annulé"),
    ],
)


# ============================================================
# 7. COMMANDES FINALES
# ============================================================
# Le montant est calculé : prix catalogue × quantité, moins la remise volume
# (voir FAQ tarifs) : 5 % à partir de 500 kg, 10 % à partir de 1 000 kg.

ORDER_STATUSES = ["Confirmée", "En préparation", "En production", "Expédiée", "Livrée", "Annulée"]

# Date du dernier changement de statut de chaque commande (suivi en temps réel).
ORDER_STATUS_DATES = {
    "ORD-2026-001": "2026-09-15", "ORD-2026-002": "2026-06-30", "ORD-2026-003": "2026-08-29",
    "ORD-2026-004": "2026-11-02", "ORD-2026-005": "2026-11-03", "ORD-2026-006": "2026-11-05",
    "ORD-2026-007": "2026-11-10", "ORD-2026-008": "2026-11-03", "ORD-2026-009": "2026-09-22",
    "ORD-2026-010": "2026-07-24",
}

orders = rows(
    ["order_id", "client_id", "project_id", "product_id", "order_date",
     "quantity_kg", "status", "delivery_date", "comment"],
    [
        ("ORD-2026-001", "CL-002", "PJ-001", "PR-001", "2026-08-01", 500, "Livrée", "2026-09-15",
         "Première commande après validation de la V3."),
        ("ORD-2026-002", "CL-001", "PJ-004", "PR-017", "2026-06-02", 80, "Livrée", "2026-06-30",
         "Première commande après validation de la V1."),
        ("ORD-2026-003", "CL-005", "PJ-007", "PR-024", "2026-08-05", 10, "Livrée", "2026-08-29",
         "Commande pour le lancement de l'eau de parfum."),
        ("ORD-2026-004", "CL-002", "PJ-001", "PR-001", "2026-10-15", 800, "En production", "2026-11-20",
         "Réassort suite au succès du lancement."),
        ("ORD-2026-005", "CL-006", "PJ-002", "PR-003", "2026-10-01", 300, "En production", "2026-11-25",
         "Commande de lancement du yaourt vanille."),
        ("ORD-2026-006", "CL-003", "PJ-008", "PR-023", "2026-10-22", 200, "En préparation", "2026-11-28",
         "Commande de lancement du nettoyant lavande."),
        ("ORD-2026-007", "CL-004", "PJ-009", "PR-012", "2026-09-20", 1200, "Expédiée", "2026-11-16",
         "Expédiée le 2026-11-10 par transport routier frigorifique."),
        ("ORD-2026-008", "CL-001", "PJ-004", "PR-017", "2026-11-02", 120, "Confirmée", "2026-12-01",
         "Réassort du savon floral."),
        ("ORD-2026-009", "CL-009", "", "PR-014", "2026-09-01", 50, "Livrée", "2026-09-22",
         "Commande directe sur catalogue, sans projet de création."),
        ("ORD-2026-010", "CL-007", "", "PR-030", "2026-07-10", 500, "Annulée", "",
         "Annulée par le client : lancement de sa gamme shampooing reporté à 2027."),
    ],
)


# ============================================================
# 8. FAQ / RÈGLES DE LA PLATEFORME
# ============================================================

faqs = [
    ("faq_commande", "Comment passer une commande",
     "Une commande peut être passée de deux façons : à partir d'un projet de création dont un échantillon a été "
     "validé, ou directement sur une référence du catalogue au statut « disponible ». Informations nécessaires : "
     "la référence produit, la quantité en kg (au moins la quantité minimale de commande du produit), l'adresse de "
     "livraison, la date de livraison souhaitée et l'application visée. La commande est confirmée sous 48 heures "
     "ouvrées. Les produits « en développement » ne sont pas commandables, seuls des échantillons sont possibles."),
    ("faq_echantillons", "Demander un échantillon",
     "Le client peut demander un échantillon depuis le catalogue ou depuis un projet de création. Les échantillons "
     "sont gratuits jusqu'à 2 kg par version ; au-delà, ils sont facturés au prix catalogue. L'échantillon est envoyé "
     "sous 10 jours ouvrés après la fin de la formulation. Le client donne ensuite son avis sur la plateforme avec une "
     "note sur 10 et des commentaires."),
    ("faq_rectifications", "Rectifications et versions",
     "Après le test d'un échantillon, le client peut demander des modifications : chaque modification produit une "
     "nouvelle version (V1, V2, V3…). Trois versions sont incluses gratuitement (V1, V2 et V3). À partir de la V4, "
     "chaque nouvelle version est facturée 350 €. Une rectification prend en moyenne 3 semaines entre le retour du "
     "client et l'envoi de la nouvelle version. Une version notée « Validé » permet de passer commande."),
    ("faq_suivi_projet", "Étapes du suivi de projet",
     "Le tableau de bord suit chaque projet de création à travers les étapes suivantes, avec leur avancement : "
     + ", ".join(f"{stage} ({pct} %)" for stage, pct in PROJECT_STAGES.items() if stage != "Annulé")
     + ". Un projet peut aussi être « Annulé » à la demande du client."),
    ("faq_statuts_commande", "Statuts de commande",
     "Une commande passe par les statuts suivants : Confirmée (commande enregistrée), En préparation (planification "
     "et réservation des matières premières), En production (fabrication du lot), Expédiée (en cours de transport), "
     "Livrée (reçue par le client). Une commande peut être Annulée tant qu'elle n'est pas en production."),
    ("faq_delais", "Délais de livraison",
     "Le délai total d'une commande est le délai de fabrication du produit (indiqué sur sa fiche catalogue, en jours "
     "ouvrés) plus le transport : 3 à 5 jours ouvrés en Europe. Les facteurs qui allongent les délais sont la "
     "disponibilité des matières premières (par exemple le vétiver, en tension d'approvisionnement), une validation "
     "réglementaire en cours, les très grandes quantités et les périodes de forte demande en fin d'année."),
    ("faq_tarifs", "Tarifs et remises",
     "Les prix catalogue sont indiqués en euros par kg, hors transport. Une remise volume s'applique automatiquement : "
     "5 % à partir de 500 kg et 10 % à partir de 1 000 kg. Les échantillons sont gratuits jusqu'à 2 kg par version."),
    ("faq_naturalite", "Niveaux de naturalité",
     "Pour les arômes : « 100 % naturel » signifie que tous les composants aromatisants sont d'origine naturelle et "
     "issus de la source nommée ; « naturel » signifie des composants naturels pouvant provenir d'autres sources ; "
     "« nature-identique » désigne des molécules identiques à celles de la nature mais obtenues par synthèse. Pour les "
     "fragrances, la naturalité est exprimée en pourcentage d'ingrédients d'origine naturelle."),
    ("faq_intensite", "Niveaux d'intensité",
     "L'intensité décrit la puissance perçue du produit au dosage recommandé : faible (note discrète, adaptée aux "
     "produits délicats ou peaux sensibles), moyenne (usage polyvalent), forte (produits à fort impact ou à longue "
     "tenue comme les lessives). Le dosage recommandé figure sur chaque fiche catalogue."),
    ("faq_allergenes", "Allergènes et réglementation",
     "Pour les arômes alimentaires, la fiche indique les allergènes alimentaires réglementaires (lait, fruits à coque, "
     "gluten…). Pour les fragrances, la fiche indique les allergènes parfumants à déclarer sur l'étiquette selon la "
     "réglementation cosmétique européenne (linalol, limonène, coumarine…). Les fiches techniques et certificats "
     "(vegan, halal, casher, bio) sont disponibles sur demande. La composition détaillée des formules n'est jamais "
     "communiquée : elle reste confidentielle."),
]


# ============================================================
# 9. CONTRÔLES DE COHÉRENCE (données « nettoyées »)
# ============================================================

client_by_id = {c["client_id"]: c for c in clients}
product_by_id = {p["product_id"]: p for p in products}
project_by_id = {p["project_id"]: p for p in projects}


def order_amount(order: dict) -> tuple[float, int, float]:
    """Retourne (montant brut, remise en %, montant net)."""
    product = product_by_id[order["product_id"]]
    gross = product["price_eur_kg"] * order["quantity_kg"]
    discount = 10 if order["quantity_kg"] >= 1000 else 5 if order["quantity_kg"] >= 500 else 0
    return gross, discount, round(gross * (1 - discount / 100), 2)


def validate() -> None:
    errors: list[str] = []

    def unique(name: str, items: list[dict], key: str) -> None:
        ids = [item[key] for item in items]
        duplicates = {i for i in ids if ids.count(i) > 1}
        if duplicates:
            errors.append(f"{name} : identifiants en double {duplicates}")

    unique("clients", clients, "client_id")
    unique("produits", products, "product_id")
    unique("produits (référence)", products, "reference")
    unique("matières premières", raw_materials, "raw_material_id")
    unique("projets", projects, "project_id")
    unique("échantillons", samples, "sample_id")
    unique("commandes", orders, "order_id")

    for p in products:
        if p["price_eur_kg"] <= 0 or p["moq_kg"] <= 0 or p["lead_time_days"] <= 0:
            errors.append(f"{p['product_id']} : prix, MOQ ou délai invalide")
        if p["intensity"] not in {"faible", "moyenne", "forte"}:
            errors.append(f"{p['product_id']} : intensité inconnue")
        prefix = "FLV-" if p["domain"] == "Arôme" else "FRG-"
        if not p["reference"].startswith(prefix):
            errors.append(f"{p['product_id']} : référence incohérente avec le domaine")

    for rm in raw_materials:
        for pid in rm["used_in"].split(", "):
            if pid not in product_by_id:
                errors.append(f"{rm['raw_material_id']} : produit inconnu {pid}")

    for pj in projects:
        if pj["client_id"] not in client_by_id:
            errors.append(f"{pj['project_id']} : client inconnu")
        if pj["base_product_id"] not in product_by_id:
            errors.append(f"{pj['project_id']} : produit inconnu")
        elif product_by_id[pj["base_product_id"]]["domain"] != pj["domain"]:
            errors.append(f"{pj['project_id']} : domaine différent du produit de base")
        if pj["stage"] not in PROJECT_STAGES:
            errors.append(f"{pj['project_id']} : étape inconnue {pj['stage']}")

    for s in samples:
        pj = project_by_id.get(s["project_id"])
        if pj is None:
            errors.append(f"{s['sample_id']} : projet inconnu")
            continue
        if s["sent_date"] < pj["created_date"]:
            errors.append(f"{s['sample_id']} : envoyé avant la création du projet")
    for pid in project_by_id:
        versions = [s["version"] for s in samples if s["project_id"] == pid]
        if versions != [f"V{i}" for i in range(1, len(versions) + 1)]:
            errors.append(f"{pid} : versions d'échantillon non séquentielles {versions}")

    for o in orders:
        if o["client_id"] not in client_by_id or o["product_id"] not in product_by_id:
            errors.append(f"{o['order_id']} : client ou produit inconnu")
            continue
        product = product_by_id[o["product_id"]]
        if o["quantity_kg"] < product["moq_kg"]:
            errors.append(f"{o['order_id']} : quantité inférieure à la MOQ")
        if o["status"] not in ORDER_STATUSES:
            errors.append(f"{o['order_id']} : statut inconnu")
        if o["status"] != "Annulée" and o["delivery_date"] < o["order_date"]:
            errors.append(f"{o['order_id']} : livraison avant la commande")
        status_date = ORDER_STATUS_DATES.get(o["order_id"])
        if status_date is None or not (o["order_date"] <= status_date <= REFERENCE_DATE):
            errors.append(f"{o['order_id']} : date de statut absente ou incohérente")
        if o["status"] == "Livrée" and status_date != o["delivery_date"]:
            errors.append(f"{o['order_id']} : livrée à une autre date que la livraison")
        if o["status"] in {"Confirmée", "En préparation", "En production", "Expédiée"} \
                and o["delivery_date"] <= REFERENCE_DATE:
            errors.append(f"{o['order_id']} : en cours mais livraison prévue dans le passé")
        if o["project_id"]:
            pj = project_by_id.get(o["project_id"])
            if pj is None or pj["client_id"] != o["client_id"] or pj["base_product_id"] != o["product_id"]:
                errors.append(f"{o['order_id']} : incohérente avec son projet")
            elif not any(s["project_id"] == pj["project_id"] and s["decision"] == "Validé" for s in samples):
                errors.append(f"{o['order_id']} : commande sans échantillon validé")
        if product["status"].startswith("en développement"):
            errors.append(f"{o['order_id']} : produit non commandable")

    if errors:
        raise SystemExit("Dataset incohérent :\n- " + "\n- ".join(errors))


# ============================================================
# 10. TRANSFORMATION EN DOCUMENTS RAG
# ============================================================

def fmt_number(value: float) -> str:
    """12345.5 -> '12 345,50' ; 12345 -> '12 345'."""
    if float(value).is_integer():
        return f"{int(value):,}".replace(",", " ")
    return f"{value:,.2f}".replace(",", " ").replace(".", ",")


raw_material_by_id = {rm["raw_material_id"]: rm for rm in raw_materials}


def app_domain(product: dict) -> str:
    """Domaine de l'application : 'fragrance' ou 'dairy_aroma' (arômes alimentaires)."""
    return "fragrance" if product["domain"] == "Fragrance" else "dairy_aroma"


def build_documents() -> list[dict]:
    documents: list[dict] = []

    def add(doc_id: str, text: str, metadata: dict) -> None:
        documents.append({"id": doc_id, "text": text, "metadata": metadata})

    for c in clients:
        client_projects = [p["project_id"] for p in projects if p["client_id"] == c["client_id"]]
        client_orders = [o["order_id"] for o in orders if o["client_id"] == c["client_id"]]
        add(f"client_{c['client_id']}",
            f"CLIENT | {c['company_name']} (ID {c['client_id']}). Segment : {c['segment']}. "
            f"Pays : {c['country']}. Secteur : {c['industry']}. Langue préférée : {c['language']}. "
            f"Niveau de compte : {c['account_level']}. "
            f"Projets de création : {', '.join(client_projects) or 'aucun'}. "
            f"Commandes : {', '.join(client_orders) or 'aucune'}.",
            {"type": "client", "client_id": c["client_id"]})

    for p in products:
        kind = "Arôme alimentaire" if p["domain"] == "Arôme" else "Fragrance"
        add(f"product_{p['product_id']}",
            f"PRODUIT CATALOGUE | {p['reference']} — {p['name']} ({kind}, ID {p['product_id']}). "
            f"Famille : {p['family']}. Profil sensoriel : {p['profile']}. "
            f"Applications recommandées : {p['applications']}. Intensité : {p['intensity']}. "
            f"Naturalité : {p['naturalness']}. Certifications : {p['certifications']}. "
            f"Allergènes : {p['allergens']}. Stabilité : {p['stability']}. "
            f"Dosage recommandé : {p['dosage']}. Prix indicatif : {p['price_eur_kg']} €/kg. "
            f"Quantité minimale de commande : {p['moq_kg']} kg. "
            f"Délai de fabrication : {p['lead_time_days']} jours ouvrés. "
            f"Marchés : {p['markets']}. Statut : {p['status']}.",
            {"type": "product", "product_id": p["product_id"]})

    for rm in raw_materials:
        used = ", ".join(
            f"{product_by_id[pid]['reference']} {product_by_id[pid]['name']}"
            for pid in rm["used_in"].split(", ")
        )
        add(f"raw_material_{rm['raw_material_id']}",
            f"MATIÈRE PREMIÈRE | {rm['name']} (réf. {rm['reference']}, ID {rm['raw_material_id']}). "
            f"Type : {rm['type']}. Origine : {rm['origin']}. Profil : {rm['profile']}. "
            f"Allergènes : {rm['allergen']}. Note réglementaire : {rm['regulatory_note']}. "
            f"Utilisée dans : {used}. Statut : {rm['status']}.",
            {"type": "raw_material", "raw_material_id": rm["raw_material_id"]})

    for pj in projects:
        client = client_by_id[pj["client_id"]]
        product = product_by_id[pj["base_product_id"]]
        history = [
            f"{s['version']} envoyée le {s['sent_date']} ({s['decision']}"
            + (f", note {s['score_10']}/10" if s["score_10"] is not None else "") + ")"
            for s in samples if s["project_id"] == pj["project_id"]
        ]
        project_orders = [o["order_id"] for o in orders if o["project_id"] == pj["project_id"]]
        add(f"project_{pj['project_id']}",
            f"PROJET DE CRÉATION | {pj['project_id']} — {pj['title']} pour {client['company_name']} "
            f"({pj['client_id']}). Type de produit : {pj['product_type']}. Domaine : {pj['domain']}. "
            f"Brief : {pj['brief']} Préférences : saveur ou odeur « {pj['flavor_or_scent']} », "
            f"intensité {pj['intensity']}, naturalité {pj['naturalness']}. Contraintes : {pj['constraints']}. "
            f"Référence de départ : {product['reference']} {product['name']}. Créé le {pj['created_date']}. "
            f"Étape actuelle : {pj['stage']} (avancement {PROJECT_STAGES[pj['stage']]} %). "
            f"Version actuelle : {pj['current_version']}. "
            f"Historique des échantillons : {'; '.join(history) or 'aucun échantillon envoyé'}. "
            f"Prochaine étape : {pj['next_step']} (date prévue : {pj['next_step_date']}). "
            f"Commandes liées : {', '.join(project_orders) or 'aucune'}. "
            f"Chef de projet : {pj['project_manager']}.",
            {"type": "project", "project_id": pj["project_id"], "client_id": pj["client_id"]})

    for s in samples:
        pj = project_by_id[s["project_id"]]
        client = client_by_id[pj["client_id"]]
        score = f"{s['score_10']}/10" if s["score_10"] is not None else "pas encore notée"
        add(f"sample_{s['sample_id']}",
            f"ÉCHANTILLON | {s['sample_id']} — version {s['version']} du projet {pj['project_id']} "
            f"« {pj['title']} » pour {client['company_name']} ({pj['client_id']}). "
            f"Envoyé le {s['sent_date']}, quantité {fmt_number(s['quantity_kg'])} kg. "
            f"Modifications apportées : {s['changes']} Retour du client : {s['client_feedback']} "
            f"Note : {score}. Décision : {s['decision']}.",
            {"type": "sample", "sample_id": s["sample_id"], "project_id": pj["project_id"],
             "client_id": pj["client_id"]})

    for o in orders:
        client = client_by_id[o["client_id"]]
        product = product_by_id[o["product_id"]]
        gross, discount, net = order_amount(o)
        origin = (f"issue du projet {o['project_id']} « {project_by_id[o['project_id']]['title']} »"
                  if o["project_id"] else "commande directe sur catalogue")
        delivery = (f"Livraison prévue ou réalisée : {o['delivery_date']}."
                    if o["delivery_date"] else "Pas de livraison (commande annulée).")
        add(f"order_{o['order_id']}",
            f"COMMANDE | {o['order_id']} de {client['company_name']} ({o['client_id']}), {origin}. "
            f"Produit : {product['reference']} {product['name']}. Quantité : {fmt_number(o['quantity_kg'])} kg. "
            f"Date de commande : {o['order_date']}. Statut : {o['status']} "
            f"(mis à jour le {ORDER_STATUS_DATES[o['order_id']]}). {delivery} "
            f"Prix unitaire : {product['price_eur_kg']} €/kg. Remise volume : {discount} %. "
            f"Montant total : {fmt_number(net)} € HT (brut {fmt_number(gross)} €). "
            f"Commentaire : {o['comment']}",
            {"type": "order", "order_id": o["order_id"], "client_id": o["client_id"],
             "product_id": o["product_id"]})

    for faq_id, title, text in faqs:
        add(faq_id, f"FAQ PLATEFORME | {title}. {text}", {"type": "faq"})

    # Domaine applicatif utilisé par le filtre de l'API (POST /ask, champ "domain") :
    # "fragrance", "dairy_aroma" (arômes alimentaires) ou "shared" (commun aux deux).
    for document in documents:
        metadata = document["metadata"]
        product_id = metadata.get("product_id")
        if product_id is None and "project_id" in metadata:
            product_id = project_by_id[metadata["project_id"]]["base_product_id"]
        if product_id is None and metadata["type"] == "raw_material":
            used = {app_domain(product_by_id[pid]) for pid in raw_material_by_id[
                metadata["raw_material_id"]]["used_in"].split(", ")}
            metadata["domain"] = used.pop() if len(used) == 1 else "shared"
            continue
        metadata["domain"] = app_domain(product_by_id[product_id]) if product_id else "shared"

    return documents


# ============================================================
# 11. ÉCRITURE DES FICHIERS
# ============================================================

TRACKING_COLUMNS = [
    "order_id", "customer_reference", "domain", "product_or_brief", "quantity", "unit",
    "order_status", "status_updated_at", "estimated_delivery_date", "tracking_message",
    "next_action", "owner_team", "notes",
]

TRACKING_BY_STATUS = {
    # statut : (message de suivi, prochaine action)
    "Confirmée": ("La commande est confirmée et en attente de planification.", "Planifier la production"),
    "En préparation": ("Les matières premières sont réservées et la production est planifiée.", "Lancer la production"),
    "En production": ("Le lot est en cours de fabrication.", "Préparer l'expédition"),
    "Expédiée": ("La commande a été expédiée.", "Suivre la livraison"),
    "Livrée": ("La commande a été livrée.", "Aucune"),
    "Annulée": ("La commande a été annulée.", "Aucune"),
}


def order_tracking_row(order: dict) -> dict:
    """Commande du dataset au format de data/orders_tracking_prototype.csv."""
    product = product_by_id[order["product_id"]]
    domain = app_domain(product)
    product_or_brief = f"{product['reference']} {product['name']}"
    if order["project_id"]:
        product_or_brief += f" - {project_by_id[order['project_id']]['title']}"
    message, next_action = TRACKING_BY_STATUS[order["status"]]
    if order["status"] in {"Expédiée", "Livrée"}:
        owner_team = "Logistics"
    elif order["status"] == "Annulée":
        owner_team = "Sales"
    else:
        owner_team = "Operations fragrance" if domain == "fragrance" else "Operations aromas"
    updated = ORDER_STATUS_DATES[order["order_id"]]
    return {
        "order_id": order["order_id"],
        "customer_reference": order["client_id"],
        "domain": domain,
        "product_or_brief": product_or_brief,
        "quantity": order["quantity_kg"],
        "unit": "kg",
        "order_status": order["status"],
        "status_updated_at": f"{updated}T09:00:00",
        "estimated_delivery_date": order["delivery_date"],
        "tracking_message": f"{message} {order['comment']}",
        "next_action": next_action,
        "owner_team": owner_team,
        "notes": "Données fictives de démonstration - ne pas utiliser comme données client.",
    }


def write_csv(filename: str, data: list[dict]) -> None:
    path = RAW_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    validate()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RAG_DIR.mkdir(parents=True, exist_ok=True)

    write_csv("clients.csv", clients)
    write_csv("products.csv", products)
    write_csv("raw_materials.csv", raw_materials)
    write_csv("projects.csv", [{**p, "progress_pct": PROJECT_STAGES[p["stage"]]} for p in projects])
    write_csv("samples.csv", samples)
    write_csv("orders.csv", [
        {**o, "unit_price_eur_kg": product_by_id[o["product_id"]]["price_eur_kg"],
         "discount_pct": order_amount(o)[1], "amount_eur": order_amount(o)[2]}
        for o in orders
    ])
    write_csv("faq.csv", [{"faq_id": f, "title": t, "text": x} for f, t, x in faqs])

    # Suivi des commandes au même format que data/orders_tracking_prototype.csv,
    # pour que GET /orders/{order_id} renvoie un seul format aux interfaces.
    tracking_path = DATA_DIR / "orders_tracking_dataset.csv"
    with tracking_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=TRACKING_COLUMNS)
        writer.writeheader()
        writer.writerows(order_tracking_row(o) for o in orders)

    documents = build_documents()

    jsonl_path = RAG_DIR / "documents.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as file:
        for document in documents:
            file.write(json.dumps(document, ensure_ascii=False) + "\n")

    # Corpus texte compatible avec ingest.py : une section « Chapter N: <id> » par document.
    text_path = BASE_DIR / "givaudan_data.txt"
    with text_path.open("w", encoding="utf-8") as file:
        file.write(
            "Plateforme B2B de création et de commande d'arômes et de fragrances — "
            f"dataset synthétique (date de référence {REFERENCE_DATE})\n\n"
        )
        for index, document in enumerate(documents, start=1):
            file.write(f"Chapter {index}: {document['id']}\n")
            file.write(document["text"])
            file.write("\n\n")

    counts: dict[str, int] = {}
    for document in documents:
        counts[document["metadata"]["type"]] = counts.get(document["metadata"]["type"], 0) + 1

    print("Dataset créé avec succès (contrôles de cohérence OK).")
    print(f"Documents RAG : {len(documents)} -> " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
    print(f"CSV : {RAW_DIR}")
    print(f"JSONL : {jsonl_path}")
    print(f"Corpus pour ingest.py : {text_path}")


if __name__ == "__main__":
    date.fromisoformat(REFERENCE_DATE)
    main()
