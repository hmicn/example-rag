"""API RAG de la plateforme de commande intelligente.

Lancement :
    uvicorn api:app --reload

Swagger :
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
import rag
import rerank


SYSTEM_PROMPT = """Tu es l'assistant B2B d'une plateforme qui permet aux entreprises de
concevoir, personnaliser, tester et commander des fragrances et des arômes alimentaires.

Tu renseignes sur le catalogue, les projets de création et leur avancement, les
échantillons et leurs versions (V1, V2, V3…) avec les retours clients, les
commandes et leur livraison, ainsi que les règles de la plateforme.

Règles impératives :
1. Réponds uniquement à partir des extraits fournis dans le contexte.
2. N'invente jamais de produit, disponibilité, délai, prix, date de livraison,
   statut de commande ou information technique.
3. Si l'information n'est pas présente dans les extraits, réponds exactement :
   "Information non disponible dans les données fournies."
4. Réponds dans la langue utilisée dans la question.
5. Sois professionnel, clair et concis.
6. Si l'utilisateur souhaite commander ou personnaliser un produit, indique les
   informations à préciser : produit ou profil recherché, application, quantité,
   format, date souhaitée, préférences et contraintes.
7. Pour une recommandation, propose uniquement les produits réellement présents
   dans le contexte et explique brièvement pourquoi ils correspondent au besoin.
"""


app = FastAPI(
    title="Intelligent Ordering Platform RAG API",
    description=(
        "API RAG de démonstration pour les fragrances et les arômes alimentaires : "
        "catalogue, projets de création, échantillons et rectifications, commandes "
        "et suivi. Données 100 % fictives. Contrat détaillé : docs/API.md."
    ),
    version="2.0.0",
)

# Autorise les interfaces web (React, Streamlit…) servies depuis une autre
# origine à appeler l'API depuis le navigateur. CORS_ORIGINS="*" par défaut ;
# mettre une liste séparée par des virgules pour restreindre.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        examples=[
            "Je veux commander un parfum floral. Comment puis-je le personnaliser ?"
        ],
    )
    domain: Literal["fragrance", "dairy_aroma", "all"] = Field(
        default="all",
        description=(
            "Domaine choisi dans l'application : fragrance, dairy_aroma, "
            "ou all pour une recherche globale."
        ),
        examples=["fragrance"],
    )
    top_k: int = Field(
        default=config.TOP_K,
        ge=1,
        le=20,
        description="Nombre maximal de documents pertinents à rechercher.",
    )


class Source(BaseModel):
    section: str
    doc_id: str = Field(
        default="",
        description="Identifiant du document source (ex. product_PR-001, knowledge-FRG-002).",
    )
    document_type: str
    domain: str
    text: str
    score: float = Field(
        description=(
            "Score de similarité : plus il est proche de 1, "
            "plus la source est pertinente."
        )
    )
    rank_score: float | None = Field(
        default=None,
        description=(
            "Score utilisé pour ordonner les sources : similarité + bonus du "
            "reclassement (référence citée, type de question). Absent si RERANK=0."
        ),
    )


class AskResponse(BaseModel):
    question: str
    domain: str
    answer: str
    model: str
    sources: list[Source]


def retrieve(question: str, top_k: int, domain: str = "all") -> list[Source]:
    """Recherche les documents les plus pertinents dans ChromaDB."""
    collection = rag.get_collection()

    if collection.count() == 0:
        raise HTTPException(
            status_code=503,
            detail=(
                "La base vectorielle est vide. "
                "Lance d'abord le script d'ingestion."
            ),
        )

    # Avec le reclassement, on examine plus de candidats que top_k puis on
    # garde les meilleurs après rerank.py (références exactes, type de question).
    n_candidates = top_k * rerank.CANDIDATE_FACTOR if config.RERANK else top_k

    query_arguments = {
        "query_embeddings": [rag.embed_query(question)],
        "n_results": min(n_candidates, collection.count()),
        "include": ["documents", "metadatas", "distances"],
    }

    # Les contenus généraux (shared) restent accessibles pour les deux domaines :
    # processus de commande, FAQ, règles de réponse, etc.
    if domain != "all":
        query_arguments["where"] = {
            "$or": [
                {"domain": domain},
                {"domain": "shared"},
            ]
        }

    result = collection.query(**query_arguments)

    sources = [
        Source(
            section=metadata.get("section", metadata.get("title", "Section inconnue")),
            doc_id=metadata.get("doc_id", ""),
            document_type=metadata.get(
                "document_type",
                metadata.get("record_type", "unknown"),
            ),
            domain=metadata.get("domain", "unknown"),
            text=document,
            score=round(1 - distance, 4),
        )
        for document, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]

    if not config.RERANK:
        return sources

    ranked = rerank.rerank(question, [source.model_dump() for source in sources], top_k)
    return [Source(**source) for source in ranked]


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
        "rerank": config.RERANK,
        "knowledge_base_path": str(config.KNOWLEDGE_BASE_PATH),
        "orders_tracking_path": str(config.ORDERS_TRACKING_PATH),
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
    return retrieve(request.question, request.top_k, request.domain)


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
def ask(request: AskRequest) -> AskResponse:
    """Répond à une question à partir des documents récupérés."""
    sources = retrieve(request.question, request.top_k, request.domain)

    if not sources:
        raise HTTPException(
            status_code=404,
            detail="Aucune information pertinente n'a été trouvée.",
        )

    context = "\n\n---\n\n".join(
        (
            f"[{source.section} | domaine={source.domain} | "
            f"type={source.document_type}]\n{source.text}"
        )
        for source in sources
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Domaine sélectionné : {request.domain}\n\n"
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
        domain=request.domain,
        answer=answer.strip(),
        model=config.LLM_MODEL,
        sources=sources,
    )


@app.get("/orders/{order_id}", tags=["Suivi des commandes"])
def get_order(order_id: str) -> dict:
    """Retourne une commande de démonstration à partir du CSV de suivi.

    Pour le prototype, les données sont fictives et lues depuis un CSV.
    Dans une version réelle, cet endpoint devra être connecté à un système
    de commandes sécurisé et contrôlé par authentification.
    """
    # Deux sources fictives : le suivi du prototype (CMD-2026-xxx) et les
    # commandes du dataset synthétique (ORD-2026-xxx).
    sources = [
        path
        for path in (config.ORDERS_TRACKING_PATH, config.DATASET_ORDERS_PATH)
        if path.exists()
    ]

    if not sources:
        raise HTTPException(
            status_code=503,
            detail="Le fichier de suivi des commandes est introuvable.",
        )

    for path in sources:
        try:
            orders_df = pd.read_csv(path, dtype=str).fillna("")
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Impossible de lire le fichier de suivi : {exc}",
            ) from exc

        order = orders_df[
            orders_df["order_id"].str.upper() == order_id.strip().upper()
        ]

        if not order.empty:
            return order.iloc[0].to_dict()

    raise HTTPException(
        status_code=404,
        detail="Commande introuvable.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)