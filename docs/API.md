# Contrat d'API — pour l'intégration des interfaces

API FastAPI (`api.py`). Documentation interactive : `/docs` (Swagger) ; schéma
machine : [`docs/openapi.json`](openapi.json) (régénéré par `python export_openapi.py`).

**Règle de compatibilité** : on ne renomme ni ne supprime aucun champ ; les évolutions
ne font qu'**ajouter** des champs. Une interface qui ignore les champs inconnus continue
de fonctionner.

## Appeler l'API depuis une interface web

- **CORS** : toutes les origines sont autorisées par défaut (`CORS_ORIGINS="*"`). Pour
  restreindre : `CORS_ORIGINS="https://mon-front.app,http://localhost:5173"`.
- **Via ngrok (version gratuite)** : ajouter l'en-tête `ngrok-skip-browser-warning: true`
  à chaque requête, sinon ngrok renvoie une page d'avertissement HTML au lieu du JSON.
  L'URL publique change à chaque relance du tunnel : la mettre dans une variable de
  configuration du front, pas en dur.
- Les réponses sont en JSON UTF-8 ; les textes sont en français.

```js
const API_URL = import.meta.env.VITE_API_URL; // ex. https://xxxx.ngrok-free.dev
const res = await fetch(`${API_URL}/ask`, {
  method: "POST",
  headers: { "Content-Type": "application/json", "ngrok-skip-browser-warning": "true" },
  body: JSON.stringify({ question: "Où en est le projet de Lumina Laundry ?", domain: "all" }),
});
const data = await res.json(); // { question, domain, answer, model, sources: [...] }
```

## Routes

| Méthode | Route | Usage dans l'interface |
|---|---|---|
| `GET` | `/health` | état du service (indicateur « IA disponible ») |
| `POST` | `/ask` | assistant IA : réponse rédigée + sources |
| `POST` | `/search` | catalogue intelligent / recherche : documents pertinents sans réponse rédigée |
| `GET` | `/orders/{order_id}` | suivi de commande en temps réel |
| `GET` | `/demo/ping` | test de connectivité, aucune donnée métier |

### `POST /ask` et `POST /search` — entrée

| Champ | Type | Obligatoire | Valeurs |
|---|---|---|---|
| `question` | string | oui | texte libre, au moins 1 caractère |
| `domain` | string | non (défaut `all`) | `fragrance`, `dairy_aroma` (arômes alimentaires) ou `all` |
| `top_k` | int | non (défaut 4) | 1 à 20 : nombre de sources |

Avec `domain` = `fragrance` ou `dairy_aroma`, les sources sont limitées à ce domaine plus
les contenus communs (`shared` : FAQ, clients, processus).

### `POST /ask` — sortie

Forme de la réponse (le texte de `answer` est illustratif : il dépend du modèle).

```json
{
  "question": "Quel est le statut de la commande ORD-2026-007 ?",
  "domain": "all",
  "answer": "La commande ORD-2026-007 de Northstar Beverages est expédiée depuis le 2026-11-10 ; livraison prévue le 2026-11-16.",
  "model": "qwen2.5:1.5b",
  "sources": [ { "...": "voir POST /search" } ]
}
```

Si l'information n'est pas dans les données, `answer` vaut exactement
`"Information non disponible dans les données fournies."` — l'interface peut détecter
cette phrase pour proposer de contacter un expert.

### `POST /search` — sortie (liste de sources)

Les valeurs de `score` et `rank_score` ci-dessous sont illustratives.

```json
[
  {
    "section": "Chapter 90: order_ORD-2026-007",
    "doc_id": "order_ORD-2026-007",
    "document_type": "order",
    "domain": "dairy_aroma",
    "text": "COMMANDE | ORD-2026-007 de Northstar Beverages (CL-004), issue du projet PJ-009 …",
    "score": 0.62,
    "rank_score": 1.22
  }
]
```

| Champ | Description |
|---|---|
| `doc_id` | identifiant stable du document : `product_PR-001`, `project_PJ-003`, `sample_SMP-007`, `order_ORD-2026-007`, `faq_tarifs`, `knowledge-FRG-002`… |
| `document_type` | `product`, `project`, `sample`, `order`, `client`, `raw_material`, `faq`, ou pour la base du chatbot `capability`, `process`, `policy` |
| `domain` | `fragrance`, `dairy_aroma` ou `shared` |
| `score` | similarité avec la question (0 à 1) |
| `rank_score` | valeur utilisée pour l'ordre des sources (similarité + bonus du reclassement) ; absent si `RERANK=0` |

### `GET /orders/{order_id}` — sortie

Même format pour les commandes du prototype (`CMD-2026-xxx`) et du dataset (`ORD-2026-xxx`).
Insensible à la casse. `404` si la commande n'existe pas.

```json
{
  "order_id": "ORD-2026-007",
  "customer_reference": "CL-004",
  "domain": "dairy_aroma",
  "product_or_brief": "FLV-212 Citron Yuzu Zéro Sucre - Eau pétillante yuzu sans sucre",
  "quantity": "1200",
  "unit": "kg",
  "order_status": "Expédiée",
  "status_updated_at": "2026-11-10T09:00:00",
  "estimated_delivery_date": "2026-11-16",
  "tracking_message": "La commande a été expédiée. Expédiée le 2026-11-10 par transport routier frigorifique.",
  "next_action": "Suivre la livraison",
  "owner_team": "Logistics",
  "notes": "Données fictives de démonstration - ne pas utiliser comme données client."
}
```

Tous les champs sont des chaînes ; `estimated_delivery_date` peut être vide (commande
annulée, devis en attente). Statuts possibles : `Brouillon`, `Brief soumis`, `En validation`,
`Devis envoyé`, `En attente de confirmation`, `Confirmée`, `En préparation`,
`En production`, `Expédiée`, `Livrée`, `Annulée`.

### Erreurs

| Code | Cas |
|---|---|
| `404` | commande introuvable (`/orders`), ou aucune source trouvée (`/ask`) |
| `422` | requête invalide (question vide, `domain` inconnu, `top_k` hors 1–20) |
| `502` | Ollama injoignable ou en erreur pendant la génération (`/ask`) |
| `503` | base vectorielle vide : lancer `python ingest.py` |

## Identifiants utiles pour une démo

| Type | Exemples |
|---|---|
| Commandes | `ORD-2026-007` (expédiée), `ORD-2026-005` (en production), `ORD-2026-008` (confirmée), `ORD-2026-010` (annulée), `CMD-2026-002` (devis envoyé) |
| Projets | `PJ-003` lessive Lumina Laundry (rectification, V3 en cours), `PJ-001` shake NutriPeak (livré après 3 versions), `PJ-006` boisson Kinetic (échantillon en attente de retour) |
| Produits | `FLV-201` Mangue Passion, `FRG-105` Fraîcheur Linge Pur, `FRG-110` Thé Vert Hypoallergénique |
