"""Configuration partagée de la plateforme de commande intelligente.

Les paramètres peuvent être surchargés par des variables d'environnement.
Exemple :
    EMBED_MODEL=qwen3-embedding:4b
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# -------------------------------------------------------------------
# Ollama
# -------------------------------------------------------------------

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Modèle qui rédige la réponse RAG.
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:1.5b")

# Baseline initiale. Plus tard, le benchmark comparera notamment :
# - nomic-embed-text
# - qwen3-embedding:0.6b
# - qwen3-embedding:4b
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")


# -------------------------------------------------------------------
# ChromaDB
# -------------------------------------------------------------------

CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db")))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "intelligent_ordering_rag")


# -------------------------------------------------------------------
# Dataset et découpage
# -------------------------------------------------------------------

# Corpus synthétique généré par generate_dataset.py.
DATASET_PATH = Path(
    os.getenv("DATASET_PATH", str(BASE_DIR / "givaudan_data.txt"))
)

# Taille maximale d'un morceau de texte indexé.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))

# Nombre de paragraphes conservés entre deux morceaux.
CHUNK_OVERLAP_PARAGRAPHS = int(
    os.getenv("CHUNK_OVERLAP_PARAGRAPHS", "1")
)


# -------------------------------------------------------------------
# Recherche
# -------------------------------------------------------------------

TOP_K = int(os.getenv("TOP_K", "4"))

# Reclassement des résultats (rerank.py) : références exactes et type de
# question. RERANK=0 pour le désactiver et comparer.
RERANK = os.getenv("RERANK", "1") != "0"

# Origines web autorisées à appeler l'API (CORS), séparées par des virgules.
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
# -------------------------------------------------------------------
# Fichiers du prototype conversationnel
# -------------------------------------------------------------------

# Base de connaissances RAG : produits, suggestions, personnalisation,
# FAQ et processus de commande.
KNOWLEDGE_BASE_PATH = Path(
    os.getenv(
        "KNOWLEDGE_BASE_PATH",
        str(BASE_DIR / "data" / "rag_knowledge_base_prototype.csv"),
    )
)

# Données fictives de suivi de commandes. Elles ne doivent pas être
# indexées dans ChromaDB : elles sont consultées directement par l'API.
ORDERS_TRACKING_PATH = Path(
    os.getenv(
        "ORDERS_TRACKING_PATH",
        str(BASE_DIR / "data" / "orders_tracking_prototype.csv"),
    )
)

# Commandes du dataset synthétique (ORD-2026-xxx), générées par
# generate_dataset.py au même format que ORDERS_TRACKING_PATH.
# Également consultées par GET /orders/{order_id}.
DATASET_ORDERS_PATH = Path(
    os.getenv(
        "DATASET_ORDERS_PATH",
        str(BASE_DIR / "data" / "orders_tracking_dataset.csv"),
    )
)

