
import csv
from pathlib import Path

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


def recommander(univers, preferences, top_k=3):
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
