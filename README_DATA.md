# Brique Data : API Tendances (Hackathon Givaudan, groupe 17)

Ce fichier explique à l'équipe **Tech** comment lancer et tester l'API Data sur son ordinateur.

> ⚠️ **Version actuelle : `0.1-dummy` (factice).**
> L'API renvoie des **fausses valeurs, mais au bon format**. Vous pouvez coder l'appel dès maintenant.
> Jeudi, la V2 renverra les **vrais résultats**, sans changer le format.

---

## 1. Les fichiers de la brique Data

| Fichier | Rôle |
|---|---|
| `api.py` | L'API FastAPI (endpoints `/health` et `/tendances`) |
| `trend_score.py` | Script Data : récupère les vues Wikipédia et calcule un score de tendance |
| `echantillon.csv` | Premier échantillon de données (vues mensuelles par ingrédient) |
| `resultats_v1.csv` | Premier résultat : classement des ingrédients (émergent / stable / en baisse) |

---

## 2. Installation (une seule fois)

Prérequis : **Python 3** installé.

```bash
git clone https://github.com/malickl/groupe17.git
cd groupe17
pip install fastapi uvicorn requests pandas
```

---

## 3. Lancer l'API

```bash
python -m uvicorn api:app --port 8000
```

Vous devez voir : `Uvicorn running on http://127.0.0.1:8000`
⚠️ Laissez ce terminal ouvert : l'API tourne dedans.

---

## 4. Tester l'API

### Option A : avec le Swagger (le plus simple)

1. Ouvrir **http://localhost:8000/docs** dans le navigateur
2. Cliquer sur **POST /tendances** → **Try it out** → **Execute**
3. Vous devez obtenir un **code 200** et une liste de résultats

Le contrat OpenAPI brut est disponible ici : **http://localhost:8000/openapi.json**

### Option B : en ligne de commande

```bash
curl -X POST http://localhost:8000/tendances -H "Content-Type: application/json" -d "{\"termes\": [\"Yuzu\", \"Matcha\", \"Vanilla\"]}"
```

---

## 5. Le contrat d'interface (ce que Tech envoie / reçoit)

### `GET /health`
Vérifie que l'API est en ligne.

Réponse :
```json
{ "status": "ok" }
```

### `POST /tendances`
Envoie une liste d'ingrédients, reçoit leur tendance.

**Requête (ce que Tech envoie) :**
```json
{
  "termes": ["Yuzu", "Matcha", "Vanilla"]
}
```

**Réponse (ce que Data renvoie) :**
```json
[
  { "terme": "Yuzu",    "croissance_pct": 25.0, "statut": "émergent" },
  { "terme": "Matcha",  "croissance_pct": 25.0, "statut": "émergent" },
  { "terme": "Vanilla", "croissance_pct": 25.0, "statut": "émergent" }
]
```

| Champ | Type | Signification |
|---|---|---|
| `terme` | texte | Nom de l'ingrédient |
| `croissance_pct` | nombre | Croissance de l'intérêt (en %), comparée aux autres ingrédients |
| `statut` | texte | `"émergent"`, `"stable"` ou `"en baisse"` |

---

## 6. Appeler l'API depuis un autre ordinateur (ngrok)

Si l'API tourne sur le PC de l'équipe Data, elle est accessible via un lien **ngrok** :

```
https://XXXX.ngrok-free.app/docs
```

(Le lien exact est envoyé par l'équipe Data sur le Discord. Il change à chaque redémarrage de ngrok.)

---

## 7. (Optionnel) Regénérer les données

```bash
python trend_score.py
```

Recrée `echantillon.csv` et `resultats_v1.csv` à partir de l'API officielle Wikimedia Pageviews.

---

## Problèmes fréquents

| Problème | Solution |
|---|---|
| `No module named uvicorn` | Relancer `pip install fastapi uvicorn` |
| `python` n'est pas reconnu | Utiliser `py` à la place de `python` |
| Le port 8000 est déjà utilisé | Lancer avec `--port 8001` et ouvrir `http://localhost:8001/docs` |
| La page `/docs` ne s'ouvre pas | Vérifier que le terminal avec uvicorn est toujours ouvert |
