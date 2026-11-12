# Évaluation RAG — v2_qwen3

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 30 — date : 2026-11-12 20:46

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.964 | ≥ 0.75 | ✅ |
| answer_accuracy | 53.6 % | ≥ 80.0 % | ❌ |
| refusal_accuracy | 0.0 % | ≥ 100.0 % | ❌ |
| latency_mean_s | 16.78 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 28/28 questions ; réponses exactes : 15/28

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 1 | ✅ | 29.58 s |
| Q02 | recommandation | 1 | ❌ | 24.46 s |
| Q03 | recommandation | 2 | ❌ | 22.14 s |
| Q04 | recommandation | 2 | ❌ | 19.10 s |
| Q05 | recommandation | 1 | ❌ | 14.40 s |
| Q06 | recommandation | 1 | ❌ | 20.59 s |
| Q07 | recommandation | 1 | ❌ | 18.43 s |
| Q08 | recommandation | 1 | ❌ | 16.18 s |
| Q09 | fiche_produit | 1 | ✅ | 19.34 s |
| Q10 | fiche_produit | 1 | ✅ | 11.80 s |
| Q11 | fiche_produit | 1 | ❌ | 17.33 s |
| Q12 | fiche_produit | 1 | ✅ | 15.94 s |
| Q13 | fiche_produit | 1 | ✅ | 14.19 s |
| Q14 | suivi_projet | 1 | ✅ | 13.62 s |
| Q15 | suivi_projet | 1 | ❌ | 15.42 s |
| Q16 | suivi_projet | 1 | ✅ | 17.33 s |
| Q17 | suivi_projet | 1 | ✅ | 16.45 s |
| Q18 | suivi_projet | 1 | ✅ | 12.84 s |
| Q19 | suivi_projet | 1 | ❌ | 13.50 s |
| Q20 | suivi_projet | 1 | ✅ | 14.59 s |
| Q21 | commande | 1 | ✅ | 17.54 s |
| Q22 | commande | 1 | ✅ | 16.77 s |
| Q23 | commande | 1 | ✅ | 16.71 s |
| Q24 | commande | 1 | ✅ | 17.93 s |
| Q25 | commande | 1 | ❌ | 15.75 s |
| Q26 | faq | 1 | ❌ | 9.13 s |
| Q27 | faq | 1 | ✅ | 24.08 s |
| Q28 | faq | 1 | ❌ | 11.97 s |
| Q29 | hors_perimetre | n/a | ❌ pas de refus | 19.00 s |
| Q30 | hors_perimetre | n/a | ❌ pas de refus | 7.19 s |
