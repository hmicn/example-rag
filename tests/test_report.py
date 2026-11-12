"""Synthèse des évaluations (report.py)."""

import report

SUMMARY = {
    "cases": 30, "answerable_cases": 28, "hits": 27, "hit_at_k": 27 / 28, "mrr": 0.9,
    "answers_ok": 24, "answer_accuracy": 24 / 28, "refusal_accuracy": 1.0, "latency_mean_s": 3.2,
    "validation": {"hit_at_k": True, "mrr": True, "answer_accuracy": True,
                   "refusal_accuracy": True, "latency_mean_s": True},
    "validated": True,
}
META = {"label": "v2_qwen3", "embed_model": "qwen3-embedding:4b", "llm_model": "qwen2.5:1.5b",
        "rerank": True, "retrieval_only": False}


def test_ligne_complete():
    line = report.row(META, SUMMARY)
    assert "27/28 (96,4 %)" in line and "0,900" in line and "24/28 (85,7 %)" in line
    assert "qwen2.5:1.5b" in line          # les noms de modèles ne sont pas « francisés »
    assert line.endswith("**validé** |")


def test_recherche_seule():
    meta = dict(META, retrieval_only=True)
    summary = {k: v for k, v in SUMMARY.items() if k not in {"answers_ok", "answer_accuracy", "refusal_accuracy"}}
    line = report.row(meta, summary)
    assert "| — | — |" in line and "recherche validée" in line
