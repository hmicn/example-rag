"""API de recherche et de questions-réponses sur les données Givaudan (RAG + Ollama).

Lancement :
    uvicorn api:app --reload
Swagger : http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import config
import rag

SYSTEM_PROMPT = """Tu es un assistant documentaire spécialisé dans les informations sur Givaudan et ses clients.

Règles :
- Réponds uniquement à partir des documents fournis dans le contexte.
- N'invente aucune information, aucun chiffre et aucune source.
- Si les documents ne permettent pas de répondre, indique clairement que l'information n'est pas disponible dans les sources.
- Utilise plusieurs passages pertinents lorsque cela permet de donner une réponse plus complète.
- Distingue les faits des scénarios fictifs présents dans les documents.
- Réponds en français, de manière claire, précise et professionnelle.
- Reste concis, mais donne suffisamment de détails pour répondre à la question.
"""

app = FastAPI(
   title="Givaudan RAG API",
description="API de recherche et de questions-réponses sur les données documentaires de Givaudan. "
            "Les réponses sont générées par un modèle Ollama à partir des passages retrouvés dans la base vectorielle.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["Quels sont les principaux domaines d'activité de Givaudan ?"])
    top_k: int = Field(config.TOP_K, ge=1, le=20, description="Nombre maximum de passages pertinents à récupérer dans la base documentaire Givaudan")


class Source(BaseModel):
    chapter: str
    text: str
    score: float = Field(description="Similarité cosinus (1 = identique)")


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    sources: list[Source]


def retrieve(question: str, top_k: int) -> list[Source]:
    collection = rag.get_collection()
    if collection.count() == 0:
        raise HTTPException(503, "La base est vide : lance d'abord `python ingest.py`.")
    result = collection.query(
        query_embeddings=[rag.embed_query(question)],
        n_results=min(top_k, collection.count()),
    )
    return [
        Source(
    chapter=meta.get("chapter", meta.get("categorie", "Non renseigné")),
    text=doc,
    score=round(1 - dist, 4)
)
        for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])
    ]


@app.get("/health", tags=["système"])
def health():
    """Vérifie que la base est chargée et indique les modèles utilisés."""
    return {
        "status": "ok",
        "chunks": rag.get_collection().count(),
        "llm_model": config.LLM_MODEL,
        "embed_model": config.EMBED_MODEL,
    }


@app.post("/search", response_model=list[Source], tags=["Givaudan RAG"])
def search(req: AskRequest):
    """Retourne seulement les passages pertinents (sans appeler le LLM)."""
    return retrieve(req.question, req.top_k)


@app.post("/ask", response_model=AskResponse, tags=["Givaudan RAG"])
def ask(req: AskRequest):
    """Génère une réponse à une question sur Givaudan à partir des documents pertinents retrouvés dans la base vectorielle."""
    sources = retrieve(req.question, req.top_k)
    context = "\n\n---\n\n".join(f"[{s.chapter}]\n{s.text}" for s in sources)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Informations issues des documents sur Givaudan :\n\n{context}\n\nQuestion : {req.question}"},
    ]
    try:
        answer = rag.chat(messages)
    except Exception as exc:  # Ollama injoignable, modèle absent...
        raise HTTPException(502, f"Erreur Ollama : {exc}") from exc
    return AskResponse(question=req.question, answer=answer.strip(), model=config.LLM_MODEL, sources=sources)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)