"""Configuration partagée de la plateforme de commande intelligente.

Les paramètres peuvent être surchargés par des variables d'environnement.

Exemples :
    EMBED_MODEL=qwen3-embedding:4b
    COLLECTION_NAME=taste_fragrance_rag_v2_qwen3_4b
"""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


# -------------------------------------------------------------------
# Ollama
# -------------------------------------------------------------------

# URL du serveur Ollama utilisé pour les embeddings et la génération.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Modèle génératif : rédige la réponse finale à partir des sources RAG.
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:1.5b")

# Modèle d'embeddings sélectionné pour la V2.
# Il sera comparé à la baseline V1 dans le protocole d'évaluation.
EMBED_MODEL = os.getenv("EMBED_MODEL", "qwen3-embedding:4b")


# -------------------------------------------------------------------
# ChromaDB
# -------------------------------------------------------------------

# Répertoire local persistant de ChromaDB.
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db")))

# Collection dédiée à la V2.
# Elle isole l index V2 de l ancien index afin de garantir une évaluation reproductible.
COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "taste_fragrance_rag_v2_qwen3_4b",
)


# -------------------------------------------------------------------
# Dataset et découpage
# -------------------------------------------------------------------

# Corpus synthétique historique généré par generate_dataset.py.
# Ses contenus seront marqués comme "shared" dans l'ingestion.
DATASET_PATH = Path(
    os.getenv("DATASET_PATH", str(BASE_DIR / "givaudan_data.txt"))
)

# STORY_PATH est conservé pour rester compatible avec l'ancien pipeline.
STORY_PATH = DATASET_PATH

# Taille maximale d'un morceau de texte indexé.
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))

# Nombre de paragraphes conservés entre deux morceaux.
CHUNK_OVERLAP_PARAGRAPHS = int(
    os.getenv("CHUNK_OVERLAP_PARAGRAPHS", "1")
)


# -------------------------------------------------------------------
# Recherche RAG
# -------------------------------------------------------------------

# Nombre de documents récupérés par défaut.
TOP_K = int(os.getenv("TOP_K", "4"))


# -------------------------------------------------------------------
# Fichiers du prototype conversationnel
# -------------------------------------------------------------------

# Base V2 : Taste & Wellbeing, Fragrance & Beauty et contenus partagés.
KNOWLEDGE_BASE_PATH = Path(
    os.getenv(
        "KNOWLEDGE_BASE_PATH",
        str(BASE_DIR / "data" / "taste_fragrance_knowledge_base.csv"),
    )
)

# Données fictives de suivi de commandes.
# Elles ne sont pas indexées dans ChromaDB : l'API les lit directement.
ORDERS_TRACKING_PATH = Path(
    os.getenv(
        "ORDERS_TRACKING_PATH",
        str(BASE_DIR / "data" / "orders_tracking_prototype.csv"),
    )
)