# Évaluation RAG — baseline_tfidf — TF-IDF (recherche seule, sans IA)

- Modèle d'embeddings : `TF-IDF lexical (sans IA, scikit-learn)`
- LLM : `aucun` (non utilisé : recherche seule)
- top_k : 4 — reclassement : non — cas : 30 — date : 2026-11-12 20:12

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 92.9 % | ≥ 90.0 % | ✅ |
| mrr | 0.690 | ≥ 0.75 | ❌ |
| latency_mean_s | 1.0 ms | ≤ 10 s | ✅ |

Bon document dans le top 4 : 26/28 questions

**Résultat global : NON VALIDÉ** (recherche seule : exactitude des réponses et refus non mesurés)

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 2 | — | 1.0 ms |
| Q02 | recommandation | 1 | — | 0.8 ms |
| Q03 | recommandation | 2 | — | 0.7 ms |
| Q04 | recommandation | 2 | — | 0.7 ms |
| Q05 | recommandation | 1 | — | 0.7 ms |
| Q06 | recommandation | 2 | — | 0.7 ms |
| Q07 | recommandation | 1 | — | 0.7 ms |
| Q08 | recommandation | absent | — | 0.7 ms |
| Q09 | fiche_produit | 2 | — | 0.7 ms |
| Q10 | fiche_produit | 1 | — | 0.6 ms |
| Q11 | fiche_produit | 2 | — | 0.7 ms |
| Q12 | fiche_produit | 1 | — | 0.7 ms |
| Q13 | fiche_produit | 1 | — | 0.7 ms |
| Q14 | suivi_projet | 2 | — | 0.7 ms |
| Q15 | suivi_projet | absent | — | 0.7 ms |
| Q16 | suivi_projet | 3 | — | 0.7 ms |
| Q17 | suivi_projet | 2 | — | 0.6 ms |
| Q18 | suivi_projet | 2 | — | 0.7 ms |
| Q19 | suivi_projet | 1 | — | 0.7 ms |
| Q20 | suivi_projet | 1 | — | 0.7 ms |
| Q21 | commande | 2 | — | 0.7 ms |
| Q22 | commande | 1 | — | 0.7 ms |
| Q23 | commande | 1 | — | 0.7 ms |
| Q24 | commande | 1 | — | 0.7 ms |
| Q25 | commande | 2 | — | 0.7 ms |
| Q26 | faq | 1 | — | 0.6 ms |
| Q27 | faq | 1 | — | 0.7 ms |
| Q28 | faq | 2 | — | 0.7 ms |
| Q29 | hors_perimetre | n/a | — | 0.7 ms |
| Q30 | hors_perimetre | n/a | — | 0.7 ms |
