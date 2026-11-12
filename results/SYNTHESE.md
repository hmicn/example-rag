# Synthèse des évaluations

Générée par `python report.py` le 2026-11-12 20:49 à partir de 8 rapport(s). Protocole et seuils : [docs/EVALUATION.md](../docs/EVALUATION.md).

| Configuration | Cas | Embeddings | LLM | Reclassement | Bon document dans le top 4 | MRR | Réponses exactes | Refus corrects | Latence moy. | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `baseline_tfidf` | 30 | TF-IDF lexical (sans IA, scikit-learn) | aucun | non | 26/28 (92,9 %) ✅ | 0,690 ❌ | — | — | 1.0 ms | recherche non validée |
| `baseline_tfidf_inedits` | 10 | TF-IDF lexical (sans IA, scikit-learn) | aucun | non | 9/9 (100,0 %) ✅ | 0,759 ✅ | — | — | 1.0 ms | recherche validée |
| `baseline_tfidf_rerank` | 30 | TF-IDF lexical (sans IA, scikit-learn) + reclassement | aucun | oui | 27/28 (96,4 %) ✅ | 0,869 ✅ | — | — | 1.0 ms | recherche validée |
| `baseline_tfidf_rerank_inedits` | 10 | TF-IDF lexical (sans IA, scikit-learn) + reclassement | aucun | oui | 9/9 (100,0 %) ✅ | 1,000 ✅ | — | — | 1.0 ms | recherche validée |
| `v2_nomic` | 30 | nomic-embed-text | qwen2.5:1.5b | oui | 27/28 (96,4 %) ✅ | 0,929 ✅ | 16/28 (57,1 %) ❌ | 100,0 % ✅ | 15.81 s | non validé |
| `v2_nomic_inedits` | 10 | nomic-embed-text | qwen2.5:1.5b | oui | 9/9 (100,0 %) ✅ | 0,944 ✅ | 5/9 (55,6 %) ❌ | 100,0 % ✅ | 16.10 s | non validé |
| `v2_qwen3` | 30 | qwen3-embedding:4b | qwen2.5:1.5b | oui | 28/28 (100,0 %) ✅ | 0,964 ✅ | 15/28 (53,6 %) ❌ | 0,0 % ❌ | 16.78 s | non validé |
| `v2_qwen3_inedits` | 10 | qwen3-embedding:4b | qwen2.5:1.5b | oui | 9/9 (100,0 %) ✅ | 0,944 ✅ | 4/9 (44,4 %) ❌ | 100,0 % ✅ | 16.18 s | non validé |

Seuils : top 4 ≥ 90 %, MRR ≥ 0,75, réponses exactes ≥ 80 %, refus corrects 100 %, latence ≤ 10 s. « — » : non mesuré (configuration sans LLM). Le détail par cas, avec les réponses du modèle, est dans chaque `eval_<configuration>.md` / `.json`.
