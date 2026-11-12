# Évaluation RAG — v2_nomic

- Modèle d'embeddings : `nomic-embed-text`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 30 — date : 2026-11-12 20:20

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 96.4 % | ≥ 90.0 % | ✅ |
| mrr | 0.929 | ≥ 0.75 | ✅ |
| answer_accuracy | 57.1 % | ≥ 80.0 % | ❌ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 15.81 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 27/28 questions ; réponses exactes : 16/28

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| Q01 | recommandation | 1 | ✅ | 25.48 s |
| Q02 | recommandation | 1 | ✅ | 21.82 s |
| Q03 | recommandation | 2 | ❌ | 17.89 s |
| Q04 | recommandation | 1 | ❌ | 16.05 s |
| Q05 | recommandation | 1 | ❌ | 16.07 s |
| Q06 | recommandation | 1 | ❌ | 17.62 s |
| Q07 | recommandation | 1 | ❌ | 17.51 s |
| Q08 | recommandation | 1 | ❌ | 17.13 s |
| Q09 | fiche_produit | absent | ❌ | 14.36 s |
| Q10 | fiche_produit | 1 | ✅ | 13.44 s |
| Q11 | fiche_produit | 1 | ❌ | 14.25 s |
| Q12 | fiche_produit | 1 | ✅ | 14.60 s |
| Q13 | fiche_produit | 1 | ✅ | 13.90 s |
| Q14 | suivi_projet | 1 | ✅ | 14.94 s |
| Q15 | suivi_projet | 1 | ✅ | 14.93 s |
| Q16 | suivi_projet | 1 | ✅ | 19.20 s |
| Q17 | suivi_projet | 1 | ✅ | 13.75 s |
| Q18 | suivi_projet | 1 | ✅ | 12.90 s |
| Q19 | suivi_projet | 1 | ❌ | 11.46 s |
| Q20 | suivi_projet | 1 | ✅ | 14.89 s |
| Q21 | commande | 1 | ✅ | 16.39 s |
| Q22 | commande | 1 | ✅ | 18.15 s |
| Q23 | commande | 1 | ✅ | 15.16 s |
| Q24 | commande | 1 | ✅ | 17.96 s |
| Q25 | commande | 2 | ❌ | 17.69 s |
| Q26 | faq | 1 | ❌ | 10.07 s |
| Q27 | faq | 1 | ✅ | 19.56 s |
| Q28 | faq | 1 | ❌ | 10.94 s |
| Q29 | hors_perimetre | n/a | ✅ refus | 12.05 s |
| Q30 | hors_perimetre | n/a | ✅ refus | 14.03 s |
