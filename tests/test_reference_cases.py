"""Jeux d'évaluation : chaque cas est répondable à partir du dataset."""

import json
from pathlib import Path

import pytest

import evaluate
import generate_dataset as g

EVAL_DIR = Path(__file__).resolve().parents[1] / "data" / "eval"
DOCS = {d["id"]: d["text"] for d in g.build_documents()}


def load(name):
    return json.loads((EVAL_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name,expected", [("reference_cases.json", 30), ("unseen_cases.json", 10)])
def test_nombre_de_cas_et_identifiants_uniques(name, expected):
    cases = load(name)
    assert len(cases) == expected
    assert len({c["id"] for c in cases}) == expected


@pytest.mark.parametrize("case", load("reference_cases.json") + load("unseen_cases.json"),
                         ids=lambda c: c["id"])
def test_cas_coherent_avec_le_dataset(case):
    if case["expect_refusal"]:
        assert not case["expected_doc_ids"] and not case["must_include"]
        return
    for doc_id in case["expected_doc_ids"]:
        assert doc_id in DOCS, doc_id
    text = " ".join(DOCS[d] for d in case["expected_doc_ids"])
    for group in case["must_include"]:
        assert evaluate.contains(text, group), group


def test_normalisation_des_nombres_et_accents():
    assert evaluate.contains("Montant total : 36 480 € HT", ["36480"])
    assert evaluate.contains("Statut : Expédiée", ["expedi"])
    assert evaluate.contains("dosage 0,05 à 0,10 %", ["0.05"])
