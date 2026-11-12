# Protocole de validation du modèle RAG

## Ce qu'on évalue

Le « modèle » est le système RAG complet : dataset + découpage + modèle d'embeddings
(recherche) + LLM (rédaction) + prompt système.

- **V1 (mardi 10 novembre, tag `v1`)** : premier prototype démontré, 29 documents,
  `qwen3-embedding:4b` + `qwen2.5:1.5b`. Évaluée qualitativement à partir de la démo
  (`docs/captures-demo-v1/`) : voir « Limites constatées sur la V1 » plus bas.
- **V2 (jeudi 12 novembre)** : dataset complet (123 documents), ingestion corrigée,
  filtre de domaine, suivi des commandes. Évaluée sur les 30 cas de référence ci-dessous.

Pour choisir le modèle d'embeddings de la V2, on compare deux configurations sur le
**même jeu de 30 cas**, ainsi qu'une baseline sans IA servant de plancher :

| Configuration V2 | Embeddings | LLM |
|---|---|---|
| `baseline_tfidf` (plancher, `baseline_tfidf.py`) | TF-IDF lexical, sans IA | aucun (recherche seule) |
| `v2_nomic` (référence légère) | `nomic-embed-text` | `qwen2.5:1.5b` |
| `v2_qwen3` (candidate retenue par l'étude) | `qwen3-embedding:4b` | `qwen2.5:1.5b` |

## Limites constatées sur la V1

Les captures de la démo du 10 novembre (`docs/captures-demo-v1/`) montrent que :

- toutes les sources renvoyées avaient la section « Introduction » et le type « unknown » :
  le titre de chaque fiche n'était pas reconnu à l'ingestion ;
- chaque passage indexé mélangeait plusieurs fiches (un client et un produit, deux commandes…),
  ce qui brouillait la recherche et les réponses ;
- 25 passages seulement, sans projets, versions d'échantillons, retours clients ni FAQ :
  la majorité des 30 cas de référence étaient hors de portée de la V1.

Ces trois points sont corrigés dans la V2.

## Jeu de référence

`data/eval/reference_cases.json` contient 30 questions, chacune avec :

- `expected_doc_ids` : le ou les documents qui contiennent la réponse ;
- `must_include` : les informations que la réponse doit contenir (chaque groupe est une
  liste d'alternatives acceptées, ex. `["2026-11-25", "25 novembre"]`) ;
- `expect_refusal` : `true` si la question est hors périmètre et que le modèle doit
  répondre que l'information n'est pas disponible au lieu d'inventer.

| Catégorie | Nb | Exemple |
|---|---|---|
| Recommandation catalogue (assistant IA) | 8 | « Un arôme mangue naturel et vegan pour une boisson protéinée ? » |
| Fiche produit | 5 | « Prix au kilo et MOQ de FRG-108 ? » |
| Suivi de projet / échantillons / rectifications | 7 | « Où en est le projet de lessive de Lumina Laundry ? » |
| Commandes | 5 | « Statut de la commande ORD-2026-007 ? » |
| Règles de la plateforme (FAQ) | 3 | « Combien de rectifications sont incluses ? » |
| Hors périmètre (pièges) | 2 | « Donne la formule exacte de FRG-101. » |

Les cas portent sur le dataset synthétique, mais la recherche se fait dans l'index complet
(dataset + base de connaissances du chatbot, sans filtre de domaine) : le modèle doit donc
aussi éviter les documents proches mais hors sujet.

Chaque cas a été vérifié automatiquement : les documents attendus existent et contiennent
bien les informations attendues.

## Cas inédits (généralisation)

`data/eval/unseen_cases.json` contient 10 questions supplémentaires (recommandation, fiche
produit, suivi de projet, commande, FAQ, question en anglais, piège hors périmètre), écrites
**avant** toute mesure du reclassement et jamais utilisées pour régler le système. Un gain
mesuré sur les 30 cas qui ne se retrouve pas sur ces 10 cas serait un sur-apprentissage.

## Reclassement des résultats

`rerank.py` réordonne les candidats de la recherche (top_k × 5 examinés) avec deux règles :
référence citée dans la question → bonus au document dont c'est la référence principale ;
type de question (« où en est », « je cherche », « retour sur l'échantillon », « statut de la
commande »…) → petit bonus au type de document correspondant. Mesure sur la baseline TF-IDF :

| | Hit@4 (30 cas) | MRR (30 cas) | Hit@4 (10 inédits) | MRR (10 inédits) |
|---|---|---|---|---|
| sans reclassement | 92,9 % | 0,690 | 100 % | 0,759 |
| avec reclassement | 96,4 % | 0,869 | 100 % | 1,000 |

10 cas sur 30 gagnent des places, aucun n'en perd. Actif par défaut dans l'API (`RERANK=0`
pour le désactiver et comparer).

## Métriques et critères de validation

| Métrique | Définition | Seuil de validation |
|---|---|---|
| Hit@4 | Part des questions dont un document attendu est dans les 4 premiers résultats | ≥ 90 % |
| MRR | Moyenne de 1 / rang du premier document attendu | ≥ 0,75 |
| Exactitude des réponses | Part des réponses contenant toutes les informations attendues | ≥ 80 % |
| Refus corrects | Part des questions pièges où le modèle refuse au lieu d'inventer | 100 % |
| Latence moyenne | Temps moyen d'un appel `/ask` (recherche + génération) | ≤ 10 s |

Une configuration d'embeddings n'est retenue que si elle fait mieux que la baseline TF-IDF
sur Hit@4 et MRR. Une configuration est **validée** si tous les seuils sont atteints. La V2 publiée utilise
`qwen3-embedding:4b` si cette configuration est validée et fait au moins aussi bien que
`nomic-embed-text` sur Hit@4 et l'exactitude ; sinon on publie `nomic-embed-text`.

## Lancer l'évaluation

```bash
python generate_dataset.py

# Tests automatiques (aucun modèle requis)
python -m pytest -q

# Baseline sans IA (aucun modèle requis), sans puis avec reclassement, puis cas inédits
python baseline_tfidf.py
python baseline_tfidf.py --rerank --label baseline_tfidf_rerank
python baseline_tfidf.py --rerank --cases data/eval/unseen_cases.json --label baseline_tfidf_rerank_inedits

# Configuration nomic-embed-text
export EMBED_MODEL=nomic-embed-text
python clean.py && python ingest.py
python evaluate.py --label v2_nomic

# Configuration qwen3-embedding:4b (réindexer : les embeddings changent avec le modèle)
export EMBED_MODEL=qwen3-embedding:4b
python clean.py && python ingest.py
python evaluate.py --label v2_qwen3
python evaluate.py --label v2_qwen3_inedits --cases data/eval/unseen_cases.json

# Tableau comparatif de toutes les configurations -> results/SYNTHESE.md
python report.py
```

Si un appel au modèle échoue (Ollama arrêté, délai dépassé…), le cas est noté en erreur dans
le rapport et l'évaluation continue avec les cas suivants.

Les rapports sont écrits dans `results/eval_v2_nomic.md` et `results/eval_v2_qwen3.md`
(+ JSON détaillé avec les réponses du modèle). `--retrieval-only` évalue uniquement la
recherche, sans LLM.

## Limites du protocole

- L'exactitude est mesurée par présence de mots-clés : une réponse juste mais formulée
  autrement peut être comptée fausse. Relire le JSON pour les cas en échec.
- 30 cas suffisent pour comparer des configurations, pas pour une garantie statistique.
