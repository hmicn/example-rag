"""Ingestion du dataset synthétique dans ChromaDB.

Usage :
    python ingest.py
    python ingest.py givaudan_data.txt

Le fichier givaudan_data.txt est généré par generate_dataset.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import config
import rag


# Reconnaît les sections générées dans givaudan_data.txt :
# "Chapter 1: client_CL-001"
SECTION_RE = re.compile(
    r"^(?:chapter|chapitre)\s+\d+\s*[:.]",
    re.IGNORECASE,
)


def split_into_sections(text: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """Découpe le corpus en sections RAG."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    dataset_title = ""
    if paragraphs and not SECTION_RE.match(paragraphs[0]):
        dataset_title = paragraphs.pop(0)

    sections: list[tuple[str, list[str]]] = []
    current_title = "Introduction"
    current_paragraphs: list[str] = []

    for paragraph in paragraphs:
        if SECTION_RE.match(paragraph) and len(paragraph) < 150:
            if current_paragraphs:
                sections.append((current_title, current_paragraphs))

            current_title = paragraph
            current_paragraphs = []
        else:
            current_paragraphs.append(paragraph)

    if current_paragraphs:
        sections.append((current_title, current_paragraphs))

    return dataset_title, sections


def chunk_paragraphs(paragraphs: list[str]) -> list[str]:
    """Regroupe les paragraphes dans des chunks de taille contrôlée."""
    chunks: list[str] = []
    current: list[str] = []
    current_size = 0

    for paragraph in paragraphs:
        if current and current_size + len(paragraph) > config.CHUNK_SIZE:
            chunks.append("\n\n".join(current))

            overlap = (
                current[-config.CHUNK_OVERLAP_PARAGRAPHS:]
                if config.CHUNK_OVERLAP_PARAGRAPHS
                else []
            )
            current = list(overlap)
            current_size = sum(len(item) for item in current)

        current.append(paragraph)
        current_size += len(paragraph)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def get_document_type(section_title: str) -> str:
    """Identifie le type métier depuis le titre de section."""
    title = section_title.lower()

    if "client_" in title:
        return "client"
    if "product_" in title:
        return "product"
    if "raw_material_" in title:
        return "raw_material"
    if "order_" in title:
        return "order"
    if "sample_" in title:
        return "sample"

    return "unknown"


def main() -> None:
    """Charge le corpus, calcule les embeddings et alimente ChromaDB."""
    source_path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else config.DATASET_PATH
    )

    if not source_path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {source_path}. "
            "Lance d'abord `python generate_dataset.py`."
        )

    text = source_path.read_text(encoding="utf-8")
    dataset_title, sections = split_into_sections(text)

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for section_index, (section_title, paragraphs) in enumerate(sections):
        document_type = get_document_type(section_title)

        for chunk_index, chunk in enumerate(chunk_paragraphs(paragraphs)):
            document_id = f"{source_path.stem}-{section_index:03d}-{chunk_index:03d}"

            ids.append(document_id)
            documents.append(chunk)
            metadatas.append(
                {
                    "source": source_path.name,
                    "dataset_title": dataset_title,
                    "section": section_title,
                    "document_type": document_type,
                    "section_index": section_index,
                    "chunk_index": chunk_index,
                }
            )

    if not documents:
        raise ValueError("Aucun document n'a été détecté dans le dataset.")

    print(f"Dataset : {dataset_title or source_path.name}")
    print(f"Sections détectées : {len(sections)}")
    print(f"Documents à indexer : {len(documents)}")
    print(f"Modèle d'embeddings : {config.EMBED_MODEL}")

    # Le titre est inclus dans l'embedding pour améliorer la recherche.
    texts_to_embed = [
        f"{metadata['section']}\n{document}"
        for document, metadata in zip(documents, metadatas)
    ]

    embeddings = rag.embed_documents(texts_to_embed)

    collection = rag.get_collection()
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(
        f"Indexation terminée : {collection.count()} documents dans "
        f"la collection '{config.COLLECTION_NAME}'."
    )
    print(f"Base ChromaDB : {config.CHROMA_DIR}")


if __name__ == "__main__":
    main()
