# Évaluation RAG — v2_qwen3_inedits

- Modèle d'embeddings : `qwen3-embedding:4b`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 10 — date : 2026-11-12 20:49

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.944 | ≥ 0.75 | ✅ |
| answer_accuracy | 44.4 % | ≥ 80.0 % | ❌ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 16.18 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 9/9 questions ; réponses exactes : 4/9

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| U01 | recommandation | 1 | ❌ | 19.24 s |
| U02 | recommandation | 2 | ❌ | 14.88 s |
| U03 | fiche_produit | 1 | ✅ | 15.82 s |
| U04 | suivi_projet | 1 | ✅ | 20.79 s |
| U05 | suivi_projet | 1 | ❌ | 14.27 s |
| U06 | commande | 1 | ❌ | 16.43 s |
| U07 | faq | 1 | ❌ | 10.16 s |
| U08 | fiche_produit | 1 | ✅ | 13.77 s |
| U09 | suivi_projet | 1 | ✅ | 22.22 s |
| U10 | hors_perimetre | n/a | ✅ refus | 14.22 s |
