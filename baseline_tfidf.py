"""Baseline lexicale (TF-IDF, sans IA) sur les 30 cas de référence.

Sert de point de comparaison pour les modèles d'embeddings : si un modèle
d'embeddings ne fait pas mieux qu'une simple recherche par mots-clés, il
n'apporte rien. Ne nécessite ni Ollama ni ChromaDB.

Indexe exactement les mêmes documents que ingest.py (dataset synthétique +
base de connaissances du chatbot) et mesure la recherche seule : Hit@k, MRR,
latence. L'exactitude des réponses et les refus ne sont pas mesurés (pas de LLM).

Usage :
    python baseline_tfidf.py                                  # 30 cas de référence
    python baseline_tfidf.py --cases data/eval/unseen_cases.json --label baseline_tfidf_inedits
    python baseline_tfidf.py --rerank --label baseline_tfidf_rerank      # avec rerank.py

Résultats : results/eval_<label>.md et .json
"""

from __future__ import annotations

import argparse
import json
import time
import unicodedata
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import config
import evaluate
import ingest
import rerank


def strip_accents(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", default=str(evaluate.DEFAULT_CASES))
    parser.add_argument("--label", default="baseline_tfidf")
    parser.add_argument("--rerank", action="store_true", help="applique rerank.py aux candidats")
    args = parser.parse_args()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    ingest.add_existing_dataset(config.DATASET_PATH, ids, documents, metadatas)
    ingest.add_knowledge_base(config.KNOWLEDGE_BASE_PATH, ids, documents, metadatas)

    # Même texte que celui envoyé au modèle d'embeddings dans ingest.py.
    texts = [f"{m['title']}\n{d}" for d, m in zip(documents, metadatas)]
    doc_ids = [m.get("doc_id", "") for m in metadatas]

    vectorizer = TfidfVectorizer(
        preprocessor=strip_accents, ngram_range=(1, 2), sublinear_tf=True, min_df=1
    )
    matrix = vectorizer.fit_transform(texts)

    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    top_k = config.TOP_K
    results = []

    for case in cases:
        start = time.perf_counter()
        scores = linear_kernel(vectorizer.transform([case["question"]]), matrix)[0]
        if args.rerank:
            pool = scores.argsort()[::-1][: top_k * rerank.CANDIDATE_FACTOR]
            candidates = [
                {"doc_id": doc_ids[i], "document_type": metadatas[i]["document_type"],
                 "text": documents[i], "score": float(scores[i])}
                for i in pool
            ]
            retrieved = [c["doc_id"] for c in rerank.rerank(case["question"], candidates, top_k)]
        else:
            retrieved = [doc_ids[i] for i in scores.argsort()[::-1][:top_k]]
        latency = time.perf_counter() - start

        expected = case["expected_doc_ids"]
        rank = next((i + 1 for i, d in enumerate(retrieved) if d in expected), None)
        result = {
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "expected_doc_ids": expected,
            "retrieved_doc_ids": retrieved,
            "rank": rank,
            "answer": "",
            "latency_s": round(latency, 4),
        }
        if case["expect_refusal"]:
            result["refusal_ok"] = None
        else:
            result["hit"] = rank is not None
        results.append(result)
        print(f"{case['id']} rang={rank}")

    summary = evaluate.summarize(results, retrieval_only=True)
    meta = {
        "label": args.label,
        "embed_model": "TF-IDF lexical (sans IA, scikit-learn)" + (" + reclassement" if args.rerank else ""),
        "llm_model": "aucun",
        "top_k": top_k,
        "rerank": args.rerank,
        "retrieval_only": True,
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "indexed_documents": len(texts),
    }

    evaluate.RESULTS_DIR.mkdir(exist_ok=True)
    (evaluate.RESULTS_DIR / f"eval_{args.label}.json").write_text(
        json.dumps({"meta": meta, "summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_path = evaluate.RESULTS_DIR / f"eval_{args.label}.md"
    evaluate.write_markdown(md_path, f"{args.label} — TF-IDF (recherche seule, sans IA)", meta, summary, results)
    print()
    print(md_path.read_text(encoding="utf-8").split("## Détail")[0])


if __name__ == "__main__":
    main()
