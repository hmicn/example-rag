"""
Premier résultat Data (V1) - Hackathon Givaudan - Tendances émergentes
Source : API officielle Wikimedia Pageviews (gratuite, sans clé, usage autorisé)
Idée : un ingrédient dont les vues Wikipédia augmentent fortement = tendance émergente.
"""
import time
import requests
import pandas as pd

# Liste d'ingrédients à tester (à adapter avec Product)
TERMES = ["Yuzu", "Matcha", "Kombucha", "Cardamom", "Black_garlic",
          "Agarwood", "Vanilla", "Lavender", "Hibiscus_tea", "Saffron"]

DEBUT, FIN = "20230101", "20251031"
HEADERS = {"User-Agent": "HackathonGivaudan-HETIC/1.0 (projet etudiant)"}
URL = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
       "en.wikipedia/all-access/user/{terme}/monthly/{debut}/{fin}")

lignes = []
for terme in TERMES:
    r = requests.get(URL.format(terme=terme, debut=DEBUT, fin=FIN), headers=HEADERS)
    if r.status_code != 200:
        print(f"[!] {terme} : pas de données (code {r.status_code})")
        continue
    for item in r.json()["items"]:
        lignes.append({"terme": terme, "mois": item["timestamp"][:6], "vues": item["views"]})
    time.sleep(0.5)  # rythme raisonnable (cours "mining responsable")

df = pd.DataFrame(lignes)
df.to_csv("echantillon.csv", index=False)
print(f"Échantillon : {len(df)} lignes, {df['terme'].nunique()} termes -> echantillon.csv")

# Score de tendance = moyenne des 12 derniers mois / moyenne des 12 mois d'avant
resultats = []
for terme, g in df.sort_values("mois").groupby("terme"):
    recent = g["vues"].tail(12).mean()
    avant = g["vues"].iloc[-24:-12].mean()
    croissance = (recent - avant) / avant * 100 if avant else 0
    resultats.append({"terme": terme, "vues_moy_recent": round(recent),
                      "croissance_%": round(croissance, 1)})

res = pd.DataFrame(resultats)
# Wikipédia perd du trafic en général : on compare chaque terme à la médiane du groupe
mediane = res["croissance_%"].median()
res["croissance_relative"] = (res["croissance_%"] - mediane).round(1)
res["statut"] = res["croissance_relative"].apply(
    lambda x: "émergent" if x > 10 else ("stable" if x > -10 else "en baisse"))
res = res.sort_values("croissance_relative", ascending=False)
res.to_csv("resultats_v1.csv", index=False)
print(res.to_string(index=False))
