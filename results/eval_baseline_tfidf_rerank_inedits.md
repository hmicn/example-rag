# Évaluation RAG — baseline_tfidf_rerank_inedits — TF-IDF (recherche seule, sans IA)

- Modèle d'embeddings : `TF-IDF lexical (sans IA, scikit-learn) + reclassement`
- LLM : `aucun` (non utilisé : recherche seule)
- top_k : 4 — reclassement : oui — cas : 10 — date : 2026-11-12 20:12

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 1.000 | ≥ 0.75 | ✅ |
| latency_mean_s | 1.0 ms | ≤ 10 s | ✅ |

Bon document dans le top 4 : 9/9 questions

**Résultat global : VALIDÉ** (recherche seule : exactitude des réponses et refus non mesurés)

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| U01 | recommandation | 1 | — | 1.0 ms |
| U02 | recommandation | 1 | — | 0.8 ms |
| U03 | fiche_produit | 1 | — | 0.8 ms |
| U04 | suivi_projet | 1 | — | 0.8 ms |
| U05 | suivi_projet | 1 | — | 0.8 ms |
| U06 | commande | 1 | — | 0.8 ms |
| U07 | faq | 1 | — | 0.8 ms |
| U08 | fiche_produit | 1 | — | 0.8 ms |
| U09 | suivi_projet | 1 | — | 0.8 ms |
| U10 | hors_perimetre | n/a | — | 0.7 ms |
