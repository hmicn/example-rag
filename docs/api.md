# Contrat API FastAPI

## Repository

- Dépôt GitHub : [equipe10](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10)
- Branche V2 : [feature/taste-fragrance-rag](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/tree/feature/taste-fragrance-rag)

## Description

L'API expose un système de recherche augmentée par génération, appelé RAG.

Le fonctionnement général est le suivant :

```text
Question utilisateur
        |
        v
API FastAPI
        |
        v
Embedding de la question
        |
        v
Recherche vectorielle ChromaDB
        |
        v
Documents pertinents
        |
        v
Construction du contexte
        |
        v
Génération de la réponse
        |
        v
Réponse avec sources
```

## URLs

### Base URL locale

```text
http://127.0.0.1:8000
```

### Documentation Swagger locale

```text
http://127.0.0.1:8000/docs
```

### Spécification OpenAPI locale

```text
http://127.0.0.1:8000/openapi.json
```

### Base URL publique

À compléter lorsque l'API sera exposée publiquement :

```text
https://URL_PUBLIQUE
```

### Swagger public

```text
https://URL_PUBLIQUE/docs
```

### OpenAPI public

```text
https://URL_PUBLIQUE/openapi.json
```

---

## `GET /health`

Vérifie que l'API est disponible.

### Requête

```http
GET /health
```

### Exemple avec curl

```bash
curl http://127.0.0.1:8000/health
```

### Réponse attendue

La réponse dépend de l'implémentation dans `api.py`.

Exemple :

```json
{
  "status": "ok"
}
```

---

## `POST /search`

Recherche les documents les plus pertinents dans la base vectorielle.

### Requête

```http
POST /search
Content-Type: application/json
```

### Corps de la requête

```json
{
  "query": "Je cherche un parfum floral au jasmin.",
  "top_k": 4
}
```

### Paramètres

| Paramètre | Type | Obligatoire | Description |
|---|---|---|---|
| `query` | `string` | Oui | Question ou recherche de l'utilisateur |
| `top_k` | `integer` | Non | Nombre de documents à récupérer |

### Exemple avec curl

```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Je cherche un parfum floral au jasmin.",
    "top_k": 4
  }'
```

### Exemple de réponse

```json
{
  "query": "Je cherche un parfum floral au jasmin.",
  "results": [
    {
      "content": "Contenu du document récupéré.",
      "metadata": {
        "title": "Jasmin éclatant",
        "domain": "fragrance_beauty"
      },
      "distance": 0.2643
    }
  ]
}
```

> La structure exacte de la réponse doit être vérifiée dans `api.py` et dans Swagger.

---

## `POST /ask`

Génère une réponse à partir des documents récupérés.

### Requête

```http
POST /ask
Content-Type: application/json
```

### Corps de la requête

```json
{
  "question": "Je cherche un parfum floral et élégant au jasmin.",
  "top_k": 4
}
```

### Paramètres

| Paramètre | Type | Obligatoire | Description |
|---|---|---|---|
| `question` | `string` | Oui | Question de l'utilisateur |
| `top_k` | `integer` | Non | Nombre de documents utilisés pour le contexte |

### Exemple avec curl

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Je cherche un parfum floral et élégant au jasmin.",
    "top_k": 4
  }'
```

### Exemple de réponse

```json
{
  "question": "Je cherche un parfum floral et élégant au jasmin.",
  "answer": "Réponse générée à partir du contexte documentaire.",
  "sources": [
    {
      "metadata": {
        "title": "Jasmin éclatant",
        "domain": "fragrance_beauty"
      },
      "distance": 0.2643
    }
  ]
}
```

> La réponse réelle doit être vérifiée dans la documentation Swagger.

---

## Démarrage de l'API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Ou :

```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

## Vérification de la syntaxe

```bash
python -m py_compile api.py
```

## Vérification des routes

```bash
grep -nE "FastAPI|/health|/search|/ask" api.py
```

## Gestion des erreurs

L'API doit gérer les situations suivantes :

- question vide ;
- corps JSON invalide ;
- document introuvable ;
- base vectorielle indisponible ;
- modèle indisponible ;
- erreur interne du serveur.

## Sécurité

Ne jamais ajouter dans le dépôt :

- un mot de passe ;
- un token GitHub ;
- un token ngrok ;
- une clé API ;
- un fichier `.env` contenant des secrets.
