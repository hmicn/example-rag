# Changelog

## Version 2.0.0 — Taste & Fragrance RAG

### Données

- Base de connaissances métier préparée.
- 45 documents indexés.
- Domaines couverts :
  - `fragrance_beauty`
  - `taste_wellbeing`
  - `shared`
- Jeu de référence de 30 cas pour l'évaluation.

### Modèle et recherche

- Modèle d'embeddings : `qwen3-embedding:4b`.
- Base vectorielle : ChromaDB.
- Collection : `taste_fragrance_rag_v2_qwen3_4b`.

### API

- API FastAPI dans `api.py`.
- Endpoint `GET /health`.
- Endpoint `POST /search`.
- Endpoint `POST /ask`.
- Documentation Swagger/OpenAPI.

### Validation

- Test réalisé sur une recherche de parfum floral au jasmin.
- Sources retrouvées :
  - Commander un parfum floral ;
  - Jasmin éclatant ;
  - Rose poudrée ;
  - Introduction.

### Documentation

- Contrat API.
- Procédure de reproduction.
- Protocole d'évaluation.
- Liens GitHub, Swagger et OpenAPI.

### Limites

- Le lien public est temporaire.
- Ollama doit être actif.
- ChromaDB est généré localement.
