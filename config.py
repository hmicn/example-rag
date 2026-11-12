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

# STORY_PATH est conservé pour rester compatible avec l'ancien pipeline.
STORY_PATH = DATASET_PATH

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
