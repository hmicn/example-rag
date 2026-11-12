
"""Charge un fichier TXT ou CSV dans la base vectorielle ChromaDB.

Usage :
    python ingest.py
    python ingest.py autre_histoire.txt
    python ingest.py givaudan_sales_dataset_nettoye.csv
"""

import re
import sys
import csv
from pathlib import Path

import config
import rag


# Détection des titres de chapitres dans les fichiers TXT
CHAPTER_RE = re.compile(
    r"^(?:[IVXLC]+\.\s+\S|chapitre\s+\w+\b)",
    re.IGNORECASE
)


def split_into_sections(text: str) -> tuple[str, list[tuple[str, list[str]]]]:
    """Sépare une histoire en chapitres et paragraphes."""

    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    title = ""

    if paragraphs and not CHAPTER_RE.match(paragraphs[0]):
        title = paragraphs.pop(0)

    sections = []
    current_title = "Introduction"
    current = []

    for p in paragraphs:
        if CHAPTER_RE.match(p) and len(p) < 120:
            if current:
                sections.append((current_title, current))

            current_title = p
            current = []
        else:
            current.append(p)

    if current:
        sections.append((current_title, current))

    return title, sections


def chunk_paragraphs(paragraphs: list[str]) -> list[str]:
    """Découpe les paragraphes en morceaux pour le RAG."""

    chunks = []
    current = []
    size = 0

    for p in paragraphs:
        if current and size + len(p) > config.CHUNK_SIZE:
            chunks.append("\n\n".join(current))

            overlap = (
                current[-config.CHUNK_OVERLAP_PARAGRAPHS:]
                if config.CHUNK_OVERLAP_PARAGRAPHS
                else []
            )

            current = list(overlap)
            size = sum(len(x) for x in current)

        current.append(p)
        size += len(p)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def load_csv(path: Path):
    """Lit le dataset CSV et prépare les documents pour le RAG."""

    documents = []
    metadatas = []
    ids = []

    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for index, row in enumerate(reader):
            entreprise = (row.get("entreprise") or "").strip()
            categorie = (row.get("categorie") or "").strip()
            titre = (row.get("titre") or "").strip()
            contenu = (row.get("contenu") or "").strip()

            if not contenu:
                continue

            texte = (
                f"Entreprise : {entreprise}\n"
                f"Catégorie : {categorie}\n"
                f"Titre : {titre}\n"
                f"Contenu : {contenu}"
            )

            documents.append(texte)

            ids.append(f"{path.stem}-{index:04d}")

            metadatas.append({
                "source": path.name,
                "entreprise": entreprise,
                "categorie": categorie,
                "titre": titre
            })

    return ids, documents, metadatas


def main() -> None:

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else config.STORY_PATH

    # ==========================================
    # PARTIE 1 : IMPORTATION DES FICHIERS CSV
    # ==========================================

    if path.suffix.lower() == ".csv":

        ids, documents, metadatas = load_csv(path)

        if not documents:
            print("Erreur : aucune donnée à indexer.")
            return

        print(f"{len(documents)} documents CSV à indexer")
        print(f"Calcul des embeddings avec '{config.EMBED_MODEL}'...")

        embeddings = []

        # Traitement des documents par groupes de 5
        for i in range(0, len(documents), 5):

            batch = documents[i:i + 5]

            print(
                f"Traitement des documents "
                f"{i + 1} à {i + len(batch)}..."
            )

            batch_embeddings = rag.embed_documents(batch)

            # Ajouter les embeddings du groupe
            embeddings.extend(batch_embeddings)

        # Vérifier que tous les embeddings ont été calculés
        if len(embeddings) != len(documents):
            print(
                f"Erreur : {len(embeddings)} embeddings "
                f"pour {len(documents)} documents."
            )
            return

        # Enregistrement dans ChromaDB
        collection = rag.get_collection()

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        print(
            f"OK : {collection.count()} documents "
            f"dans ChromaDB"
        )

        return

    # ==========================================
    # PARTIE 2 : IMPORTATION DES FICHIERS TXT
    # ==========================================

    text = path.read_text(encoding="utf-8")

    story_title, sections = split_into_sections(text)

    ids = []
    documents = []
    metadatas = []

    for chap_idx, (chapter, paragraphs) in enumerate(sections):

        for chunk_idx, chunk in enumerate(chunk_paragraphs(paragraphs)):

            ids.append(
                f"{path.stem}-{chap_idx:02d}-{chunk_idx:03d}"
            )

            documents.append(chunk)

            metadatas.append({
                "source": path.name,
                "story_title": story_title,
                "chapter": chapter,
                "chapter_index": chap_idx,
                "chunk_index": chunk_idx,
            })

    print(f"Histoire : {story_title or path.name}")

    print(
        f"{len(sections)} chapitres, "
        f"{len(documents)} morceaux à indexer"
    )

    print(f"Calcul des embeddings avec '{config.EMBED_MODEL}'...")

    to_embed = [
        f"{m['chapter']}\n{d}"
        for d, m in zip(documents, metadatas)
    ]

    embeddings = rag.embed_documents(to_embed)

    collection = rag.get_collection()

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(
        f"OK : {collection.count()} morceaux dans "
        f"la collection '{config.COLLECTION_NAME}' "
        f"({config.CHROMA_DIR})"
    )


if __name__ == "__main__":
    main()