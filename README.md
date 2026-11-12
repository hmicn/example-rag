# Givaudan AI Recommendation

**Projet Hackathon HETIC x Givaudan**

Une solution d'intelligence artificielle combinant un système de recherche documentaire (RAG) et un moteur de recommandation de produits pour accompagner les équipes commerciales dans l'analyse des besoins clients.

## Présentation du projet

Ce projet propose une API capable de répondre à des questions sur les données documentaires de Givaudan et de recommander des produits en fonction des préférences et du brief d'un client.

La solution repose sur deux fonctionnalités principales :

### 1. Recherche documentaire intelligente (RAG)

Le système permet de retrouver des informations pertinentes dans une base documentaire à l'aide de la recherche vectorielle.

- Importation de données depuis des fichiers CSV ou TXT.
- Découpage et préparation des documents.
- Génération d'embeddings avec Ollama.
- Stockage vectoriel avec ChromaDB.
- Recherche des passages pertinents.
- Génération de réponses avec un modèle de langage local.

### 2. Moteur de recommandation de produits

Le moteur identifie les produits correspondant le mieux aux attentes d'un client.

Il prend en compte cinq critères :

- Gourmand
- Premium
- Naturel
- Audace
- Bien-être

Le moteur V2 combine les scores des préférences avec une comparaison lexicale du brief commercial pour calculer un score de correspondance.

Deux univers sont pris en charge :
- Arôme (`arome`)
- Parfum (`parfum`)

## Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Langage principal |
| FastAPI | Création de l'API REST |
| Ollama | Exécution locale des modèles IA |
| Qwen 2.5 | Génération des réponses |
| Nomic Embed Text | Génération des embeddings |
| ChromaDB | Base de données vectorielle |
| Pydantic | Validation des données |
| Uvicorn | Serveur ASGI |

## Architecture du projet

```text
givaudan-ai-recommendation/
│
├── api.py
├── config.py
├── rag.py
├── ingest.py
│
├── recommandation.py
├── recommandation_v2.py
│
├── analyse_dataset.py
├── benchmark_recommandation.py
├── benchmark_llm.pdf
├── benchmark_v1_30_tests.txt
│
├── data/
│   ├── produits_demo.csv
│   ├── projets_demo.csv
│   └── cas_reference.csv
│
├── givaudan_sales_dataset_nettoye.csv
├── requirements.txt
├── .gitignore
└── README.md
```

La base ChromaDB (`chroma_db/`) est générée localement lors de l'indexation et n'est pas versionnée sur GitHub.

## Installation

### Prérequis

- Python 3.10 ou supérieur.
- Git.
- Ollama installé.
- Les modèles Ollama nécessaires au projet.

### 1. Cloner le dépôt

```bash
git clone https://github.com/Hetic-Hackathon-Givaudan-2026-Allard/givaudan-ai-recommendation.git
```

```bash
cd givaudan-ai-recommendation
```

### 2. Créer un environnement virtuel

Sous Windows :

```powershell
python -m venv .venv
```

Activer l'environnement :

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### 4. Installer les modèles Ollama

Télécharger les modèles utilisés par défaut :

```bash
ollama pull qwen2.5:1.5b
```

```bash
ollama pull nomic-embed-text
```

Vérifier les modèles installés :

```bash
ollama list
```

Ollama doit être démarré et accessible sur `http://localhost:11434`.

## Configuration

Le fichier `config.py` centralise les paramètres du projet.

| Paramètre | Valeur par défaut | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Adresse du serveur Ollama |
| `LLM_MODEL` | `qwen2.5:1.5b` | Modèle de génération |
| `EMBED_MODEL` | `nomic-embed-text` | Modèle d'embeddings |
| `CHROMA_DIR` | `chroma_db` | Dossier de stockage vectoriel |
| `COLLECTION_NAME` | `givaudan_sales` | Nom de la collection |
| `TOP_K` | `4` | Nombre de passages récupérés par défaut |

Ces paramètres peuvent être personnalisés à l'aide de variables d'environnement.

## Importation des données dans ChromaDB

Le script `ingest.py` permet d'importer des fichiers CSV ou TXT dans la base vectorielle.

Pour indexer le dataset Givaudan :

```powershell
python ingest.py givaudan_sales_dataset_nettoye.csv
```

Le CSV doit contenir les colonnes suivantes :

- `entreprise`
- `categorie`
- `titre`
- `contenu`

Les autres colonnes éventuelles sont ignorées par le script actuel.

Le processus réalise les opérations suivantes :

1. Lecture des données.
2. Préparation des documents.
3. Génération des embeddings avec Ollama.
4. Enregistrement dans ChromaDB.

## Démarrage de l'API

Lancer le serveur depuis le dossier du projet :

```bash
uvicorn api:app --reload
```

L'API est accessible à l'adresse :

```text
http://127.0.0.1:8000
```

Documentation interactive Swagger :

```text
http://127.0.0.1:8000/docs
```

## Endpoints disponibles

### 1. Vérification de l'API

**GET `/health`**

Permet de vérifier l'état de l'API et le nombre de documents indexés.

### 2. Recherche documentaire

**POST `/search`**

Recherche les passages les plus pertinents sans générer de réponse avec le LLM.

Exemple :

```json
{
  "question": "Quelles sont les activités principales de Givaudan ?",
  "top_k": 4
}
```

### 3. Questions-réponses avec le RAG

**POST `/ask`**

Recherche les documents pertinents puis utilise Ollama pour générer une réponse fondée sur les informations retrouvées.

Exemple :

```json
{
  "question": "Quels sont les principaux domaines d'activité de Givaudan ?",
  "top_k": 4
}
```

La réponse contient :
- La question posée.
- La réponse générée.
- Le modèle utilisé.
- Les sources documentaires retrouvées.

### 4. Recommandation de produits

**POST `/recommend`**

Retourne les produits les plus proches des préférences et du brief commercial.

Exemple :

```json
{
  "univers": "arome",
  "brief": "Je recherche un arôme gourmand et naturel",
  "preferences": {
    "gourmand": 9,
    "premium": 8,
    "naturel": 5,
    "audace": 4,
    "bienetre": 6
  },
  "top_k": 3
}
```

Les notes des cinq critères doivent être comprises entre 1 et 10.

L'univers doit être `arome` ou `parfum`.

La réponse contient le statut de la recherche et la liste des recommandations avec leurs scores de correspondance.

## Tests du moteur de recommandation

Le moteur peut également être testé directement depuis Python :

```python
from recommandation_v2 import recommander

preferences = {
    "gourmand": 9,
    "premium": 8,
    "naturel": 5,
    "audace": 4,
    "bienetre": 6
}

resultats = recommander(
    univers="arome",
    preferences=preferences,
    top_k=3,
    brief="Je recherche un arôme gourmand et naturel"
)

for produit in resultats:
    print(produit)
```

## Objectif

L'objectif de cette solution est de faciliter l'exploitation des informations documentaires et d'améliorer l'accompagnement commercial grâce à une recherche intelligente et à des recommandations adaptées aux besoins des clients.

---

**Projet réalisé dans le cadre du Hackathon HETIC x Givaudan.**