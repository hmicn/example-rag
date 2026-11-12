
import csv
from pathlib import Path
from collections import Counter

fichier = Path("data/produits_demo.csv")

with fichier.open("r", encoding="utf-8-sig", newline="") as f:
    lecteur = csv.DictReader(f, delimiter=";")
    produits = list(lecteur)
    colonnes = lecteur.fieldnames or []

print("=== ANALYSE DU DATASET GIVAUDAN ===")
print("Nombre de produits :", len(produits))
print("Nombre de colonnes :", len(colonnes))

print("\nRépartition par univers :")
for univers, nombre in Counter(
    p.get("universe", "") for p in produits
).items():
    print(f"- {univers} : {nombre}")

ids = [p.get("id", "") for p in produits]
print("\nIdentifiants en doublon :", len(ids) - len(set(ids)))

valeurs_manquantes = sum(
    not str(p.get(col, "")).strip()
    for p in produits
    for col in colonnes
)
print("Valeurs manquantes :", valeurs_manquantes)

print("\nColonnes disponibles :")
print(", ".join(colonnes))

print("\n=== CONTROLE DES SCORES ===")

criteres = [
    "gourmand",
    "premium",
    "naturel",
    "audace",
    "bienetre"
]

erreurs = 0

for produit in produits:
    for critere in criteres:
        try:
            score = float(produit[critere])

            if not 0 <= score <= 10:
                print(
                    f"Score hors limites : "
                    f"{produit['name']} - {critere} = {score}"
                )
                erreurs += 1

        except (ValueError, TypeError):
            print(
                f"Score invalide : "
                f"{produit['name']} - {critere}"
            )
            erreurs += 1

print("Nombre d'erreurs de scores :", erreurs)

print("\n=== CONTROLE DES PROJETS ===")

fichier_projets = Path("data/projets_demo.csv")

with fichier_projets.open(
    "r", encoding="utf-8-sig", newline=""
) as f:
    projets = list(csv.DictReader(f, delimiter=";"))

ids_produits = {p["id"] for p in produits}
univers_produits = {
    p["id"]: p["universe"] for p in produits
}

references_invalides = 0
univers_incoherents = 0

for projet in projets:
    produit_id = projet["product_id"]

    if produit_id not in ids_produits:
        references_invalides += 1
    elif projet["universe"] != univers_produits[produit_id]:
        univers_incoherents += 1

print("Nombre de projets :", len(projets))
print("Références produits invalides :", references_invalides)
print("Univers incohérents :", univers_incoherents)

print("\nRépartition des résultats :")
for resultat, nombre in Counter(
    p["outcome"] for p in projets
).items():
    print(f"- {resultat} : {nombre}")
