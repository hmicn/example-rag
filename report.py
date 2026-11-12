"""Synthèse de toutes les évaluations dans results/SYNTHESE.md.

Lit chaque results/eval_*.json (produit par evaluate.py ou baseline_tfidf.py)
et construit un tableau comparatif unique.

Usage :
    python report.py
"""

from __future__ import annotations

import json
import time

import evaluate

OUTPUT = evaluate.RESULTS_DIR / "SYNTHESE.md"


def pct(x: float) -> str:
    return f"{x * 100:.1f} %".replace(".", ",")


def verdict(meta: dict, summary: dict) -> str:
    if meta.get("retrieval_only"):
        return "recherche validée" if summary["validated"] else "recherche non validée"
    return "**validé**" if summary["validated"] else "non validé"


def row(meta: dict, summary: dict) -> str:
    v = summary["validation"]

    def mark(metric: str) -> str:
        return "" if metric not in v else (" ✅" if v[metric] else " ❌")

    accuracy = (f"{summary['answers_ok']}/{summary['answerable_cases']} ({pct(summary['answer_accuracy'])}){mark('answer_accuracy')}"
                if "answer_accuracy" in summary else "—")
    refusal = (f"{pct(summary['refusal_accuracy'])}{mark('refusal_accuracy')}"
               if "refusal_accuracy" in summary else "—")
    mrr = f"{summary['mrr']:.3f}".replace(".", ",")
    return (
        f"| `{meta['label']}` | {summary['cases']} | {meta['embed_model']} | {meta['llm_model']} | "
        f"{'oui' if meta.get('rerank') else 'non'} | "
        f"{summary['hits']}/{summary['answerable_cases']} ({pct(summary['hit_at_k'])}){mark('hit_at_k')} | "
        f"{mrr}{mark('mrr')} | {accuracy} | {refusal} | "
        f"{evaluate.fmt_seconds(summary['latency_mean_s'])} | "
        f"{verdict(meta, summary)} |"
    )


def main() -> None:
    reports = []
    for path in sorted(evaluate.RESULTS_DIR.glob("eval_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        summary = data["summary"]
        # Rapports produits avant l'ajout des compteurs : on les recalcule.
        if "hits" not in summary:
            summary = evaluate.summarize(data["results"], data["meta"].get("retrieval_only", False))
        reports.append((data["meta"], summary))

    lines = [
        "# Synthèse des évaluations",
        "",
        f"Générée par `python report.py` le {time.strftime('%Y-%m-%d %H:%M')} à partir de "
        f"{len(reports)} rapport(s). Protocole et seuils : [docs/EVALUATION.md](../docs/EVALUATION.md).",
        "",
        "| Configuration | Cas | Embeddings | LLM | Reclassement | Bon document dans le top 4 | MRR | "
        "Réponses exactes | Refus corrects | Latence moy. | Verdict |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    lines += [row(meta, summary) for meta, summary in reports]
    lines += [
        "",
        "Seuils : top 4 ≥ 90 %, MRR ≥ 0,75, réponses exactes ≥ 80 %, refus corrects 100 %, "
        "latence ≤ 10 s. « — » : non mesuré (configuration sans LLM). Le détail par cas, avec "
        "les réponses du modèle, est dans chaque `eval_<configuration>.md` / `.json`.",
    ]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUTPUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
