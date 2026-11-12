import csv
import time
from pathlib import Path

from recommandation import recommander

BASE = Path(__file__).parent
FICHIER_TESTS = BASE / "data" / "cas_reference.csv"

CRITERES = [
    "gourmand", "premium", "naturel",
    "audace", "bienetre"
]

with FICHIER_TESTS.open(
    "r", encoding="utf-8-sig", newline=""
) as fichier:
    tests = list(csv.DictReader(fichier, delimiter=";"))

top1_corrects = 0
top3_corrects = 0
temps_total = 0

print("=== BENCHMARK RECOMMANDATION V1 ===")

for test in tests:
    preferences = {
        critere: float(test[critere])
        for critere in CRITERES
    }

    debut = time.perf_counter()

    resultats = recommander(
        univers=test["univers"],
        preferences=preferences,
        top_k=3
    )

    duree = time.perf_counter() - debut
    temps_total += duree

    ids = [produit["id"] for produit in resultats]
    attendu = test["produit_attendu"]

    top1_ok = bool(ids) and ids[0] == attendu
    top3_ok = attendu in ids

    top1_corrects += int(top1_ok)
    top3_corrects += int(top3_ok)

    print(
        f"{test['id']} | "
        f"Attendu : {attendu} | "
        f"Obtenus : {ids} | "
        f"Top-1 : {'OK' if top1_ok else 'NON'} | "
        f"Top-3 : {'OK' if top3_ok else 'NON'}"
    )

nombre_tests = len(tests)

if nombre_tests == 0:
    raise ValueError("Aucun cas de référence trouvé.")

print("\n=== RESULTATS ===")
print("Nombre de tests :", nombre_tests)
print(
    "Top-1 Accuracy :",
    f"{100 * top1_corrects / nombre_tests:.1f} %"
)
print(
    "Recall@3 :",
    f"{100 * top3_corrects / nombre_tests:.1f} %"
)
print(
    "Temps moyen :",
    f"{1000 * temps_total / nombre_tests:.2f} ms"
)