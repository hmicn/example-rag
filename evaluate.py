"""Évaluation du modèle RAG sur les 30 cas de référence.

Le script passe chaque question de data/eval/reference_cases.json dans le
même pipeline que l'API (recherche ChromaDB + réponse du LLM) et calcule :

  - Hit@k        : part des questions dont un document attendu est dans le top k ;
  - MRR          : rang moyen inverse du premier document attendu retrouvé ;
  - Exactitude   : part des réponses contenant toutes les informations attendues ;
  - Refus        : part des questions hors périmètre correctement refusées ;
  - Latence      : temps moyen et p95 de /ask (recherche + génération).

Usage :
    python evaluate.py --label v2_nomic                # EMBED_MODEL=nomic-embed-text
    python evaluate.py --label v2_qwen3                # EMBED_MODEL=qwen3-embedding:4b (après réindexation)
    python evaluate.py --label v2_nomic --retrieval-only  # recherche seule, sans LLM (rapide)

Les résultats sont écrits dans results/eval_<label>.json et results/eval_<label>.md.
Pré-requis : `python ingest.py` avec le même EMBED_MODEL.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import time
import unicodedata
from pathlib import Path

import config

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES = BASE_DIR / "data" / "eval" / "reference_cases.json"
RESULTS_DIR = BASE_DIR / "results"

# Critères de validation (voir docs/EVALUATION.md).
THRESHOLDS = {
    "hit_at_k": 0.90,
    "mrr": 0.75,
    "answer_accuracy": 0.80,
    "refusal_accuracy": 1.00,
    "latency_mean_s": 10.0,
}

REFUSAL_MARKERS = ["non disponible", "not available", "confidentiel", "confidential"]


def normalize(text: str) -> str:
    """Minuscules, sans accents, sans espaces de milliers, virgule décimale -> point."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()
    text = re.sub(r"(?<=\d)[\s  ](?=\d)", "", text)
    return text.replace(",", ".")


def contains(answer: str, alternatives: list[str]) -> bool:
    norm = normalize(answer)
    return any(normalize(alt) in norm for alt in alternatives)


def evaluate_case(case: dict, top_k: int, retrieval_only: bool) -> dict:
    import api  # import tardif : le module charge ChromaDB et Ollama

    error = None
    start = time.perf_counter()
    try:
        if retrieval_only:
            sources = api.retrieve(case["question"], top_k)
            answer = ""
        else:
            response = api.ask(api.AskRequest(question=case["question"], top_k=top_k))
            sources, answer = response.sources, response.answer
    except Exception as exc:  # un cas en erreur ne doit pas arrêter toute l'évaluation
        error = getattr(exc, "detail", None) or repr(exc)
        answer = ""
        try:
            sources = api.retrieve(case["question"], top_k)
        except Exception:
            sources = []
    latency = time.perf_counter() - start

    retrieved = [s.doc_id for s in sources]
    expected = case["expected_doc_ids"]
    rank = next((i + 1 for i, d in enumerate(retrieved) if d in expected), None)

    result = {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "expected_doc_ids": expected,
        "retrieved_doc_ids": retrieved,
        "rank": rank,
        "answer": answer,
        "latency_s": round(latency, 3),
    }
    if error:
        result["error"] = str(error)

    if case["expect_refusal"]:
        result["refusal_ok"] = None if retrieval_only else contains(answer, REFUSAL_MARKERS)
    else:
        result["hit"] = rank is not None
        if not retrieval_only:
            missing = [group for group in case["must_include"] if not contains(answer, group)]
            result["answer_ok"] = not missing
            result["missing"] = missing
    return result


def summarize(results: list[dict], retrieval_only: bool) -> dict:
    answerable = [r for r in results if "hit" in r]
    refusals = [r for r in results if "refusal_ok" in r]
    latencies = sorted(r["latency_s"] for r in results)

    summary = {
        "cases": len(results),
        "answerable_cases": len(answerable),
        "hits": sum(r["hit"] for r in answerable),
        "errors": sum("error" in r for r in results),
        "hit_at_k": sum(r["hit"] for r in answerable) / len(answerable),
        "mrr": sum(1 / r["rank"] for r in answerable if r["rank"]) / len(answerable),
        "latency_mean_s": round(statistics.mean(latencies), 3),
        "latency_p95_s": round(latencies[max(0, int(0.95 * len(latencies)) - 1)], 3),
    }
    if not retrieval_only:
        summary["answers_ok"] = sum(r["answer_ok"] for r in answerable)
        summary["answer_accuracy"] = summary["answers_ok"] / len(answerable)
        summary["refusal_accuracy"] = (
            sum(r["refusal_ok"] for r in refusals) / len(refusals) if refusals else 1.0
        )

    by_category: dict[str, dict] = {}
    for r in answerable:
        cat = by_category.setdefault(r["category"], {"n": 0, "hits": 0, "answers_ok": 0})
        cat["n"] += 1
        cat["hits"] += r["hit"]
        cat["answers_ok"] += r.get("answer_ok", False)
    summary["by_category"] = by_category

    checks = {}
    for metric, threshold in THRESHOLDS.items():
        if metric not in summary:
            continue
        value = summary[metric]
        checks[metric] = value <= threshold if metric.startswith("latency") else value >= threshold
    summary["validation"] = checks
    summary["validated"] = all(checks.values())
    return summary


def fmt_seconds(value: float) -> str:
    """0.0012 -> '1.2 ms' ; 2.345 -> '2.35 s'."""
    return f"{value * 1000:.1f} ms" if value < 1 else f"{value:.2f} s"


def write_markdown(path: Path, label: str, meta: dict, summary: dict, results: list[dict]) -> None:
    def pct(x: float) -> str:
        return f"{x * 100:.1f} %"

    lines = [
        f"# Évaluation RAG — {label}",
        "",
        f"- Modèle d'embeddings : `{meta['embed_model']}`",
        f"- LLM : `{meta['llm_model']}`" + (" (non utilisé : recherche seule)" if meta["retrieval_only"] else ""),
        f"- top_k : {meta['top_k']} — reclassement : {'oui' if meta.get('rerank') else 'non'}"
        f" — cas : {summary['cases']} — date : {meta['date']}",
        "",
        "| Métrique | Valeur | Seuil | Validé |",
        "|---|---|---|---|",
    ]
    for metric, threshold in THRESHOLDS.items():
        if metric not in summary:
            continue
        value = summary[metric]
        shown = fmt_seconds(value) if metric.startswith("latency") else (
            f"{value:.3f}" if metric == "mrr" else pct(value))
        limit = f"≤ {threshold:.0f} s" if metric.startswith("latency") else (
            f"≥ {threshold:.2f}" if metric == "mrr" else f"≥ {pct(threshold)}")
        lines.append(f"| {metric} | {shown} | {limit} | {'✅' if summary['validation'][metric] else '❌'} |")
    lines += [
        "",
        f"Bon document dans le top {meta['top_k']} : {summary['hits']}/{summary['answerable_cases']} questions"
        + (f" ; réponses exactes : {summary['answers_ok']}/{summary['answerable_cases']}" if "answers_ok" in summary else "")
        + (f" ; **{summary['errors']} cas en erreur** (voir le JSON)" if summary.get("errors") else ""),
        "",
        f"**Résultat global : {'VALIDÉ' if summary['validated'] else 'NON VALIDÉ'}**"
        + (" (recherche seule : exactitude des réponses et refus non mesurés)"
           if meta["retrieval_only"] else ""),
        "",
        "## Détail par cas",
        "",
        "| Cas | Catégorie | Rang du bon document | Réponse OK | Latence |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        if "hit" in r:
            ok = "—" if "answer_ok" not in r else ("✅" if r["answer_ok"] else "❌")
            rank = r["rank"] or "absent"
        else:
            ok = "—" if r["refusal_ok"] is None else ("✅ refus" if r["refusal_ok"] else "❌ pas de refus")
            rank = "n/a"
        lines.append(f"| {r['id']} | {r['category']} | {rank} | {ok} | {fmt_seconds(r['latency_s'])} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Évalue le RAG sur le jeu de référence.")
    parser.add_argument("--label", default="v2", help="nom de la configuration évaluée (ex. v2_nomic, v2_qwen3)")
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--top-k", type=int, default=config.TOP_K)
    parser.add_argument("--retrieval-only", action="store_true", help="évalue seulement la recherche")
    args = parser.parse_args()

    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    results = []
    for case in cases:
        result = evaluate_case(case, args.top_k, args.retrieval_only)
        results.append(result)
        status = f"rang={result['rank']}" if "hit" in result else "refus attendu"
        print(f"{case['id']} {status} ({result['latency_s']:.2f} s)")

    summary = summarize(results, args.retrieval_only)
    meta = {
        "label": args.label,
        "embed_model": config.EMBED_MODEL,
        "llm_model": config.LLM_MODEL,
        "top_k": args.top_k,
        "rerank": config.RERANK,
        "retrieval_only": args.retrieval_only,
        "date": time.strftime("%Y-%m-%d %H:%M"),
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    json_path = RESULTS_DIR / f"eval_{args.label}.json"
    json_path.write_text(
        json.dumps({"meta": meta, "summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_path = RESULTS_DIR / f"eval_{args.label}.md"
    write_markdown(md_path, args.label, meta, summary, results)

    print()
    print(md_path.read_text(encoding="utf-8").split("## Détail")[0])
    print(f"Rapport : {md_path}")


if __name__ == "__main__":
    main()
