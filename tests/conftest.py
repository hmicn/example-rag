"""Configuration commune des tests.

Les tests tournent sans Ollama : les embeddings sont remplacés par un
embedding de test (sac de mots haché) et le LLM par une fonction qui renvoie
le contexte reçu. Ils vérifient la mécanique (données, ingestion, API,
reclassement), pas la qualité des modèles — celle-ci est mesurée par
evaluate.py et baseline_tfidf.py.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Base ChromaDB temporaire : ne touche jamais à chroma_db/ du projet.
os.environ["CHROMA_DIR"] = tempfile.mkdtemp(prefix="chroma_tests_")
os.environ["COLLECTION_NAME"] = "tests"


def fake_embed(texts: list[str], prefix: str = "") -> list[list[float]]:
    vectors = []
    for text in texts:
        text = unicodedata.normalize("NFKD", text.lower())
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        vector = [0.0] * 256
        for word in re.findall(r"[a-z0-9-]{3,}", text):
            vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % 256] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        vectors.append([x / norm for x in vector])
    return vectors


@pytest.fixture(scope="session")
def indexed():
    """Génère le dataset, l'indexe avec l'embedding de test et renvoie le module api."""
    import generate_dataset
    import ingest
    import rag

    generate_dataset.main()
    rag.embed = fake_embed
    rag.chat = lambda messages: messages[-1]["content"]
    ingest.main()

    import api

    return api


@pytest.fixture(scope="session")
def client(indexed):
    from fastapi.testclient import TestClient

    return TestClient(indexed.app)
