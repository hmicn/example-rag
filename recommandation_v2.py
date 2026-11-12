
import csv
from pathlib import Path
import re
import unicodedata


def extraire_mots(texte):
    texte = texte.lower()

    texte = "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texte)
        if unicodedata.category(caractere) != "Mn"
    )

    return set(re.findall(r"[a-z0-9]+", texte))
MOTS_IGNORES = {
    "je", "un", "une", "le", "la", "les",
    "de", "des", "du", "et", "pour", "avec",
    "dans", "qui", "est", "au", "aux",
    "recherche", "souhaite", "veut"
}


def score_texte(brief, description):
    mots_brief = extraire_mots(brief) - MOTS_IGNORES
    mots_produit = extraire_mots(description) - MOTS_IGNORES

    if not mots_brief:
        return 0

    mots_communs = mots_brief.intersection(mots_produit)

    return round(
        100 * len(mots_communs) / len(mots_brief),
        1
    )
FICHIER = Path(__file__).parent / "data" / "produits_demo.csv"

CRITERES = [
    "gourmand",
    "premium",
    "naturel",
    "audace",
    "bienetre"
]


def charger_produits():
    with FICHIER.open(
        "r", encoding="utf-8-sig", newline=""
    ) as fichier:
        return list(csv.DictReader(fichier, delimiter=";"))


def recommander(univers, preferences, top_k=3, brief=""):
    produits = charger_produits()
    resultats = []

    for produit in produits:
        # Ne comparer que les produits du bon univers
        if produit["universe"].strip().lower() != univers.lower():
            continue

        # Comparer les 5 critères, chacun noté de 0 à 10
        ecarts = [
            abs(float(produit[c]) - float(preferences[c]))
            for c in CRITERES
        ]

        # 100 % = correspondance parfaite sur les 5 critères
        score = 100 * (1 - sum(ecarts) / (10 * len(CRITERES)))
        score_numerique = score

        texte_produit = " ".join([
            produit["name"],
            produit["family"],
            produit["pitch"]
        ])

        score_textuel = score_texte(brief, texte_produit)

        if brief.strip():
            score = 0.8 * score_numerique + 0.2 * score_textuel
        resultats.append({
            "id": produit["id"],
            "nom": produit["name"],
            "famille": produit["family"],
            "score": round(score, 1),
            "description": produit["pitch"]
        })

    resultats.sort(key=lambda p: (-p["score"], p["id"]))
    return resultats[:top_k]


if __name__ == "__main__":
    # Exemple de brief : parfum gourmand et premium
    preferences_client = {
        "gourmand": 9,
        "premium": 9,
        "naturel": 5,
        "audace": 7,
        "bienetre": 4
    }

    recommandations = recommander(
        univers="arome",
        preferences=preferences_client
    )

    print("=== RECOMMANDATIONS V1 ===")

    for rang, produit in enumerate(recommandations, start=1):
        print(f"\n{rang}. {produit['nom']}")
        print(f"Famille : {produit['famille']}")
        print(f"Score de correspondance : {produit['score']} %")
        print(f"Description : {produit['description']}")
