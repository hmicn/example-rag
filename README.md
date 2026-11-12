# Plateforme B2B intelligente d'arômes et de fragrances — RAG (équipe 10)

[![Tests](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/actions/workflows/tests.yml/badge.svg)](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/actions/workflows/tests.yml)

Prototype de RAG pour une plateforme où les entreprises conçoivent, personnalisent, testent
et commandent des arômes alimentaires et des fragrances, en suivant leurs projets jusqu'à la
livraison. L'assistant IA répond uniquement à partir de données **100 % fictives**.

## Où trouver les livrables

| Livrable | Où le trouver |
|---|---|
| 1. Données nettoyées et préparées | [`data/raw/`](data/raw) (tables CSV) et [`generate_dataset.py`](generate_dataset.py) (génération + contrôles de cohérence) |
| 2. Pipeline de traitement fonctionnel | [`ingest.py`](ingest.py) → ChromaDB → [`rerank.py`](rerank.py) → [`api.py`](api.py) ; démo complète dans [`notebooks/`](notebooks) |
| 3. Modèle V2 publié | V2 = branche `main` (V1 de mardi : tag [`v1`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/releases/tag/v1)) ; embeddings `qwen3-embedding:4b` + LLM `qwen2.5:1.5b`, choix justifié par [`results/`](results) et [`docs/etude_benchmark_embeddings.pdf`](docs/etude_benchmark_embeddings.pdf) |
| 4. Métriques et protocole sur 30 cas | section [Résultats](#résultats) ci-dessous, protocole [`docs/EVALUATION.md`](docs/EVALUATION.md), cas [`data/eval/`](data/eval), rapports [`results/`](results), tests [`tests/`](tests) |
| 5. API renvoyant les résultats réels | [`api.py`](api.py) ; contrat pour les interfaces [`docs/API.md`](docs/API.md) et [`docs/openapi.json`](docs/openapi.json) ; Swagger (`/docs`) exposé via ngrok depuis le notebook |

**Tester en 1 clic :** ouvrir [`notebooks/RAG_Givaudan_Equipe10.ipynb`](notebooks/RAG_Givaudan_Equipe10.ipynb) dans Colab puis « Exécuter tout ».

## Résultats

Mesurés sur les **30 cas de référence** et, pour vérifier que le modèle généralise, sur
**10 cas inédits** écrits avant toute mesure et jamais utilisés pour régler le système.

| Configuration | Cas | Hit@4 | MRR | Exactitude | Refus | Latence | Rapport |
|---|---|---|---|---|---|---|---|
| *Seuil de validation* | | *≥ 90 %* | *≥ 0,75* | *≥ 80 %* | *100 %* | *≤ 10 s* | |
| Baseline TF-IDF (sans IA) | 30 | 92,9 % | 0,690 ❌ | — | — | 1 ms | [rapport](results/eval_baseline_tfidf.md) |
| Baseline TF-IDF **+ reclassement** | 30 | **96,4 %** | **0,869** ✅ | — | — | 1 ms | [rapport](results/eval_baseline_tfidf_rerank.md) |
| Baseline TF-IDF (sans IA) | 10 inédits | 100 % | 0,759 | — | — | 1 ms | [rapport](results/eval_baseline_tfidf_inedits.md) |
| Baseline TF-IDF **+ reclassement** | 10 inédits | **100 %** | **1,000** | — | — | 1 ms | [rapport](results/eval_baseline_tfidf_rerank_inedits.md) |
| V2 — `nomic-embed-text` + `qwen2.5:1.5b` + reclassement | 30 | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | `results/eval_v2_nomic.md` |
| V2 — `qwen3-embedding:4b` + `qwen2.5:1.5b` + reclassement | 30 | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | *à mesurer* | `results/eval_v2_qwen3.md` |

« — » : non mesuré, la baseline ne fait que la recherche (pas de LLM pour rédiger ou refuser).

**Ce que montrent les mesures déjà faites :**

- **Une recherche par mots-clés trouve souvent le bon document, mais pas en premier**
  (MRR 0,690) : elle confond un projet avec le produit qu'il utilise, ou une commande avec une
  autre du même client. Elle échoue sur la question en anglais (Q08 : « sunscreen » ≠
  « crème solaire »).
- **Le reclassement ([`rerank.py`](rerank.py)) corrige la plupart de ces confusions** avec deux
  règles explicables : une référence citée (`ORD-2026-007`, `FRG-108`…) fait passer son document
  devant, et le type de question (« où en est », « je cherche », « retour sur l'échantillon »…)
  favorise le bon type de document. 10 cas sur 30 montent, aucun ne descend. Le gain se confirme
  sur les 10 cas inédits (MRR 0,759 → 1,000) : ce n'est pas un réglage sur mesure. Il est actif
  par défaut dans l'API (`RERANK=0` pour le couper).
- Les modèles d'embeddings doivent battre la baseline reclassée, notamment sur les questions
  en anglais ou formulées sans les mots du document : c'est ce que mesurent les lignes V2.

Les lignes V2 se remplissent en lançant le notebook (Ollama nécessaire), qui produit
`results.zip` à déposer dans [`results/`](results). Le tableau complet de toutes les
configurations est généré automatiquement dans [`results/SYNTHESE.md`](results/SYNTHESE.md) (`python report.py`).

**Tests automatiques :** `python -m pytest` — 73 tests, relancés par GitHub Actions à chaque modification (badge en haut de page) (données, cas d'évaluation, ingestion,
reclassement, API complète, contrat OpenAPI, synthèse) qui tournent sans Ollama en quelques secondes.

## Historique des versions

| Version | Date | Contenu | Où la voir |
|---|---|---|---|
| **V1** | mardi 10 novembre | Premier prototype démontré : dataset de 29 documents (clients, produits, matières premières, commandes, échantillons), ingestion ChromaDB, API FastAPI (`/health`, `/search`, `/ask`, `/demo/ping`) exposée via ngrok, `qwen3-embedding:4b` + `qwen2.5:1.5b`, étude comparative des modèles d'embeddings | tag [`v1`](https://github.com/Hetic-Hackathon-Givaudan-2026-CHARK/equipe10/releases/tag/v1), captures de la démo dans [`docs/captures-demo-v1/`](docs/captures-demo-v1) |
| **V2** | jeudi 12 novembre | Dataset complet (103 documents : catalogue de 30 produits, projets de création, échantillons V1/V2/V3, commandes, FAQ) + base de connaissances du chatbot (20 fiches) ; ingestion corrigée ; reclassement des résultats ; filtre par domaine ; suivi des commandes `GET /orders/{id}` ; évaluation sur 30 cas de référence + 10 inédits ; 73 tests automatiques ; API ouverte aux interfaces web (CORS) et contrat documenté | branche `main` |

**Ce que la V2 corrige par rapport à la V1** (visible sur les captures de la démo V1) : chaque
fiche du dataset était mal découpée — toutes les sources avaient la section « Introduction »
et le type « unknown », et chaque passage mélangeait plusieurs fiches. La V2 indexe une fiche
par document, avec son type et son domaine. Détail dans [docs/EVALUATION.md](docs/EVALUATION.md).

## Données indexées

`python ingest.py` indexe deux sources dans ChromaDB :

**1. Dataset synthétique** — généré par `generate_dataset.py` (contrôles de cohérence automatiques),
103 documents dans `givaudan_data.txt` :

| Entité | Nb | Fonctionnalité de la plateforme |
|---|---|---|
| Produits catalogue | 30 | catalogue intelligent : 16 arômes `FLV-xxx`, 14 fragrances `FRG-1xx` (profil, applications, intensité, naturalité, certifications, allergènes, dosage, prix, MOQ, délai) |
| Projets de création | 12 | création personnalisée + suivi (brief, préférences, étape, avancement %, prochaine étape) |
| Échantillons | 17 | échantillons et rectifications V1/V2/V3 avec retours et notes clients |
| Commandes | 10 | gestion des commandes `ORD-2026-xxx` (statut, livraison, montant avec remise volume) |
| FAQ | 10 | règles : commande, échantillons, rectifications, délais, tarifs, naturalité… |
| Clients / matières premières | 10 / 14 | comptes B2B, origines et notes réglementaires |

Tables CSV dans `data/raw/`, documents avec métadonnées dans `data/rag/documents.jsonl`.

**2. Base de connaissances du chatbot** — `data/rag_knowledge_base_prototype.csv` (20 fiches :
parfums `FRG-00x`, arômes laitiers `ARM-00x`, personnalisation, processus de commande, gouvernance).

Chaque document porte un **domaine** (`fragrance`, `dairy_aroma` pour les arômes alimentaires,
ou `shared`) utilisé par le filtre `domain` de l'API.

## Démarrage

```bash
pip install -r requirements.txt
ollama pull nomic-embed-text && ollama pull qwen2.5:1.5b

python generate_dataset.py
python clean.py && python ingest.py
python list.py
uvicorn api:app --reload        # Swagger : http://127.0.0.1:8000/docs
```

Sur Colab : `notebooks/RAG_Givaudan_Equipe10.ipynb` déroule tout (installation, dataset,
évaluation, API, ngrok). Le token ngrok se met dans les *Secrets* Colab (`NGROK_AUTHTOKEN`).

## API

- `GET /health` — documents indexés et modèles utilisés
- `POST /search` — documents pertinents (`doc_id`, `document_type`, `domain`, score), reclassés par `rerank.py`
- `POST /ask` — réponse rédigée à partir des documents retrouvés ; `domain` = `fragrance`, `dairy_aroma` ou `all`
- `GET /orders/{order_id}` — suivi d'une commande (`CMD-2026-xxx` du prototype ou `ORD-2026-xxx` du dataset), toujours au même format
- `GET /demo/ping` — endpoint factice pour la démo ngrok

Contrat complet pour les interfaces (champs, exemples, erreurs, appel depuis un front React via
ngrok) : [docs/API.md](docs/API.md). L'API accepte les appels depuis un navigateur (CORS ouvert par
défaut, `CORS_ORIGINS` pour restreindre). Via ngrok gratuit, ajouter l'en-tête
`ngrok-skip-browser-warning: true`.

## Évaluation du modèle

30 cas de référence et 10 cas inédits (`data/eval/`), `evaluate.py` : Hit@k, MRR,
exactitude des réponses, refus corrects, latence. `baseline_tfidf.py` mesure la même chose
sans IA, comme plancher. Deux modèles d'embeddings comparés pour la V2 :
`nomic-embed-text` et `qwen3-embedding:4b`. Protocole et seuils : [docs/EVALUATION.md](docs/EVALUATION.md).

## Critères d'acceptation minimum

- `python ingest.py` se termine sans erreur ; `python list.py` affiche les documents indexés.
- `GET /health` renvoie le nombre de documents et les modèles.
- `POST /search` renvoie des passages pertinents pour une question produit ou commande.
- `POST /ask` produit une réponse fondée sur le contexte retrouvé.
- `GET /demo/ping` est joignable en local et via ngrok.
- `python evaluate.py` produit les rapports d'évaluation dans `results/`.
- `python -m pytest` passe (73 tests).

## Organisation du dépôt

```
├── generate_dataset.py      # génère et contrôle le dataset synthétique
├── ingest.py                # indexe le dataset + la base de connaissances dans ChromaDB
├── api.py                   # API FastAPI
├── evaluate.py              # évaluation sur les 30 cas de référence
├── baseline_tfidf.py        # baseline sans IA (TF-IDF) sur les mêmes cas
├── rerank.py                # reclassement des résultats (références exactes, type de question)
├── report.py                # synthèse de toutes les évaluations -> results/SYNTHESE.md
├── export_openapi.py        # exporte le contrat d'API -> docs/openapi.json
├── rag.py, config.py        # briques communes et paramètres (surchargeables par variables d'env.)
├── list.py, clean.py        # inspecter / vider la base vectorielle
├── sample_questions.py      # questions de démo
├── givaudan_data.txt        # corpus généré, prêt à ingérer
├── data/
│   ├── raw/                 # tables CSV du dataset (clients, produits, projets, échantillons, commandes…)
│   ├── rag/documents.jsonl  # documents du dataset avec métadonnées
│   ├── eval/                # 30 cas de référence + 10 cas inédits
│   ├── rag_knowledge_base_prototype.csv   # base de connaissances du chatbot
│   ├── orders_tracking_prototype.csv      # suivi de commandes du prototype (CMD-2026-xxx)
│   └── orders_tracking_dataset.csv        # suivi des commandes du dataset, même format (ORD-2026-xxx)
├── results/                 # rapports d'évaluation (générés par evaluate.py)
├── tests/                   # tests automatiques (pytest, sans Ollama)
├── notebooks/               # notebook Colab de démonstration
└── docs/                    # contrat d'API, protocole d'évaluation, étude des modèles, captures de la démo V1
```

## Règle de sécurité

Données synthétiques uniquement. Aucune identité client réelle, formule propriétaire,
composition de matière première, identifiant ou donnée de commande interne dans GitHub,
ChromaDB ou un endpoint exposé via ngrok. Aucun token (ngrok…) en clair dans le code ou le notebook.
