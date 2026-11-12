# Évaluation RAG — v2_nomic_inedits

- Modèle d'embeddings : `nomic-embed-text`
- LLM : `qwen2.5:1.5b`
- top_k : 4 — reclassement : oui — cas : 10 — date : 2026-11-12 20:23

| Métrique | Valeur | Seuil | Validé |
|---|---|---|---|
| hit_at_k | 100.0 % | ≥ 90.0 % | ✅ |
| mrr | 0.944 | ≥ 0.75 | ✅ |
| answer_accuracy | 55.6 % | ≥ 80.0 % | ❌ |
| refusal_accuracy | 100.0 % | ≥ 100.0 % | ✅ |
| latency_mean_s | 16.10 s | ≤ 10 s | ❌ |

Bon document dans le top 4 : 9/9 questions ; réponses exactes : 5/9

**Résultat global : NON VALIDÉ**

## Détail par cas

| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |
|---|---|---|---|---|
| U01 | recommandation | 1 | ❌ | 16.69 s |
| U02 | recommandation | 2 | ✅ | 16.69 s |
| U03 | fiche_produit | 1 | ✅ | 17.64 s |
| U04 | suivi_projet | 1 | ✅ | 22.89 s |
| U05 | suivi_projet | 1 | ❌ | 10.54 s |
| U06 | commande | 1 | ❌ | 16.89 s |
| U07 | faq | 1 | ❌ | 11.08 s |
| U08 | fiche_produit | 1 | ✅ | 13.15 s |
| U09 | suivi_projet | 1 | ✅ | 24.43 s |
| U10 | hors_perimetre | n/a | ✅ refus | 10.96 s |
