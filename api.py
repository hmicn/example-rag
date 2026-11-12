"""API RAG de la plateforme de commande intelligente.

Lancement :
    uvicorn api:app --reload

Swagger :
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import config
import rag


SYSTEM_PROMPT = """Tu es un assistant B2B pour une plateforme de commande intelligente.

Tu aides à retrouver des informations dans un dataset synthétique concernant :
- les clients ;
- les produits et leurs références ;
- les matières premières ;
- les commandes ;
- les demandes d'échantillons.

Règles :
1. Réponds uniquement à partir des extraits fournis.
2. N'invente jamais de client, produit, référence, commande, statut ou prix.
3. Si l'information n'est pas présente dans les extraits, réponds exactement :
   "Information non disponible dans les données fournies."
4. Cite les références importantes lorsque c'est possible.
5. Réponds dans la langue utilisée dans la question.
6. Sois professionnel, clair et concis.
"""

app = FastAPI(
    title="Intelligent Ordering Platform RAG API",
    description=(
        "API RAG de démonstration permettant de rechercher des informations "
        "sur des clients, produits, commandes, matières premières et "
        "échantillons synthétiques."
    ),
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        examples=[
            "Quel produit NutriPeak Foods a-t-il recommandé en février 2025 ?"
        ],
    )
    top_k: int = Field(
        default=config.TOP_K,
        ge=1,
        le=20,
        description="Nombre maximal de documents pertinents à rechercher.",
    )


class Source(BaseModel):
    section: str
    document_type: str
    text: str
    score: float = Field(
        description="Score de similarité : plus il est proche de 1, plus la source est pertinente."
    )


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    sources: list[Source]


def retrieve(question: str, top_k: int) -> list[Source]:
    """Recherche les documents les plus pertinents dans ChromaDB."""
    collection = rag.get_collection()

    if collection.count() == 0:
        raise HTTPException(
            status_code=503,
            detail=(
                "La base vectorielle est vide. "
                "Lance d'abord `python ingest.py givaudan_data.txt`."
            ),
        )

    result = collection.query(
        query_embeddings=[rag.embed_query(question)],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    return [
        Source(
            section=metadata.get("section", "Section inconnue"),
            document_type=metadata.get("document_type", "unknown"),
            text=document,
            score=round(1 - distance, 4),
        )
        for document, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


@app.get("/health", tags=["Système"])
def health() -> dict:
    """État de l'API, des modèles et de l'index vectoriel."""
    collection = rag.get_collection()

    return {
        "status": "ok",
        "service": "intelligent-ordering-rag",
        "indexed_documents": collection.count(),
        "llm_model": config.LLM_MODEL,
        "embedding_model": config.EMBED_MODEL,
    }


@app.get("/demo/ping", tags=["Démonstration"])
def demo_ping() -> dict:
    """Endpoint dummy, ne retournant aucune donnée métier."""
    return {
        "status": "ok",
        "service": "intelligent-ordering-rag",
        "message": "Demo endpoint is reachable.",
    }


@app.post("/search", response_model=list[Source], tags=["Recherche"])
def search(request: AskRequest) -> list[Source]:
    """Retourne les sources pertinentes sans appeler le LLM."""
    return retrieve(request.question, request.top_k)


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
def ask(request: AskRequest) -> AskResponse:
    """Répond à une question à partir des documents récupérés."""
    sources = retrieve(request.question, request.top_k)

    context = "\n\n---\n\n".join(
        f"[{source.section} | type={source.document_type}]\n{source.text}"
        for source in sources
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Contexte récupéré :\n\n{context}\n\n"
                f"Question utilisateur : {request.question}"
            ),
        },
    ]

    try:
        answer = rag.chat(messages)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Erreur lors de l'appel à Ollama : {exc}",
        ) from exc

    return AskResponse(
        question=request.question,
        answer=answer.strip(),
        model=config.LLM_MODEL,
        sources=sources,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
