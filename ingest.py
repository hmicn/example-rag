"""Ingestion des données dans ChromaDB.

Ce script indexe deux sources :
1. givaudan_data.txt : dataset synthétique généré par generate_dataset.py
   (catalogue, projets de création, échantillons V1/V2/V3, commandes, FAQ…).
   Le domaine de chaque document est lu dans data/rag/documents.jsonl.
2. data/rag_knowledge_base_prototype.csv : base de connaissances du chatbot
   (parfums, arômes laitiers, personnalisation, FAQ et processus de commande).

Le fichier data/orders_tracking_prototype.csv n'est volontairement pas indexé :
il est utilisé directement par l'endpoint GET /orders/{order_id}.

Usage :
    python ingest.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

import config
import rag

DOCUMENTS_JSONL = config.BASE_DIR / "data" / "rag" / "documents.jsonl"


# Reconnaît les sections générées dans givaudan_data.txt :
# "Chapter 1: client_CL-001"
SECTION_RE = re.compile(
    r"^(?:chapter|chapitre)\s+\d+\s*[:.]",
    re.IGNORECASE,
)


def split_into_sections(text: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """Découpe le corpus texte existant en sections RAG."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    dataset_title = ""
    if paragraphs and not SECTION_RE.match(paragraphs[0]):
        dataset_title = paragraphs.pop(0)

    sections: list[tuple[str, list[str]]] = []
    current_title = "Introduction"
    current_paragraphs: list[str] = []

    for paragraph in paragraphs:
        # Le titre de section peut être seul dans son paragraphe ou suivi
        # directement du texte sur la ligne suivante (format de
        # generate_dataset.py : "Chapter 1: client_CL-001\nCLIENT | ...").
        first_line, _, rest = paragraph.partition("\n")
        if SECTION_RE.match(first_line) and len(first_line) < 150:
            if current_paragraphs:
                sections.append((current_title, current_paragraphs))

            current_title = first_line.strip()
            current_paragraphs = [rest.strip()] if rest.strip() else []
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
    """Identifie le type métier depuis le titre d'une section."""
    doc_id = get_doc_id(section_title)

    for prefix, document_type in (
        ("client_", "client"),
        ("product_", "product"),
        ("raw_material_", "raw_material"),
        ("project_", "project"),
        ("sample_", "sample"),
        ("order_", "order"),
        ("faq_", "faq"),
    ):
        if doc_id.startswith(prefix):
            return document_type

    return "unknown"


def get_doc_id(section_title: str) -> str:
    """'Chapter 12: product_PR-001' -> 'product_PR-001'."""
    return section_title.split(":", 1)[-1].strip()


def load_dataset_domains() -> dict[str, str]:
    """Domaine de chaque document généré, lu dans data/rag/documents.jsonl."""
    if not DOCUMENTS_JSONL.exists():
        return {}
    domains = {}
    for line in DOCUMENTS_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            document = json.loads(line)
            domains[document["id"]] = document["metadata"].get("domain", "shared")
    return domains


def add_existing_dataset(
    source_path: Path,
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    """Ajoute le corpus synthétique existant à la liste des documents."""
    if not source_path.exists():
        print(f"Dataset existant ignoré : fichier absent ({source_path}).")
        return

    text = source_path.read_text(encoding="utf-8")
    dataset_title, sections = split_into_sections(text)
    domains = load_dataset_domains()

    for section_index, (section_title, paragraphs) in enumerate(sections):
        document_type = get_document_type(section_title)
        doc_id = get_doc_id(section_title)

        for chunk_index, chunk in enumerate(chunk_paragraphs(paragraphs)):
            document_id = (
                f"synthetic-{source_path.stem}-{section_index:03d}-{chunk_index:03d}"
            )

            ids.append(document_id)
            documents.append(chunk)
            metadatas.append(
                {
                    "source": source_path.name,
                    "dataset_title": dataset_title or source_path.name,
                    "section": section_title,
                    "title": section_title,
                    "document_type": document_type,
                    "record_type": document_type,
                    "doc_id": doc_id,
                    # fragrance / dairy_aroma selon le produit concerné ; shared
                    # pour les contenus communs (clients, FAQ…), toujours visibles.
                    "domain": domains.get(doc_id, "shared"),
                    "category": "",
                    "tags": "",
                    "section_index": section_index,
                    "chunk_index": chunk_index,
                }
            )


def value_as_string(value: object) -> str:
    """Convertit une valeur CSV en texte sans renvoyer 'nan'."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def add_knowledge_base(
    source_path: Path,
    ids: list[str],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    """Ajoute le catalogue conversationnel avec ses métadonnées de domaine."""
    if not source_path.exists():
        raise FileNotFoundError(
            f"Base de connaissances introuvable : {source_path}"
        )

    df = pd.read_csv(source_path, dtype=str).fillna("")

    required_columns = {
        "record_id",
        "domain",
        "record_type",
        "title",
        "content",
    }
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Colonnes manquantes dans {source_path.name} : {missing}"
        )

    for _, row in df.iterrows():
        record_id = value_as_string(row["record_id"])
        content = value_as_string(row["content"])
        domain = value_as_string(row["domain"])

        if not record_id or not content or not domain:
            continue

        # ChromaDB accepte les métadonnées simples : str, int, float ou bool.
        metadata = {
            "source": source_path.name,
            "dataset_title": "Givaudan conversational prototype knowledge base",
            "section": value_as_string(row.get("title", "")),
            "title": value_as_string(row.get("title", "")),
            "document_type": value_as_string(row.get("record_type", "knowledge")),
            "record_type": value_as_string(row.get("record_type", "knowledge")),
            "domain": domain,
            "category": value_as_string(row.get("category", "")),
            "sub_category": value_as_string(row.get("sub_category", "")),
            "application": value_as_string(row.get("application", "")),
            "tags": value_as_string(row.get("tags", "")),
            "doc_id": f"knowledge-{record_id}",
        }

        ids.append(f"knowledge-{record_id}")
        documents.append(content)
        metadatas.append(metadata)


def main() -> None:
    """Construit les documents, calcule les embeddings et alimente ChromaDB."""
    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    # 1. Garde le dataset synthétique déjà utilisé dans le prototype.
    add_existing_dataset(config.DATASET_PATH, ids, documents, metadatas)

    # 2. Ajoute la nouvelle base de connaissances conversationnelle.
    add_knowledge_base(config.KNOWLEDGE_BASE_PATH, ids, documents, metadatas)

    if not documents:
        raise ValueError("Aucun document n'a été détecté pour l'indexation.")

    print(f"Documents à indexer : {len(documents)}")
    print(f"Modèle d'embeddings : {config.EMBED_MODEL}")
    print(f"Base de connaissances : {config.KNOWLEDGE_BASE_PATH}")

    # Le titre est inclus dans l'embedding afin d'améliorer la recherche.
    texts_to_embed = [
        f"{metadata['title']}\n{document}"
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