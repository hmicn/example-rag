"""Dataset : cohérence des données générées."""

import csv
import json

import pytest

import generate_dataset as g


def test_validation_passe():
    g.validate()


def test_validation_detecte_une_commande_sous_la_moq(monkeypatch):
    order = dict(g.orders[0], quantity_kg=1)
    monkeypatch.setattr(g, "orders", [order] + g.orders[1:])
    with pytest.raises(SystemExit, match="MOQ"):
        g.validate()


def test_validation_detecte_un_doublon(monkeypatch):
    monkeypatch.setattr(g, "clients", g.clients + [g.clients[0]])
    with pytest.raises(SystemExit, match="double"):
        g.validate()


def test_volumes():
    documents = g.build_documents()
    counts = {}
    for d in documents:
        counts[d["metadata"]["type"]] = counts.get(d["metadata"]["type"], 0) + 1
    assert counts == {"client": 10, "product": 30, "raw_material": 14, "project": 12,
                      "sample": 17, "order": 10, "faq": 10}


def test_identifiants_uniques_et_domaines_valides():
    documents = g.build_documents()
    ids = [d["id"] for d in documents]
    assert len(ids) == len(set(ids))
    assert {d["metadata"]["domain"] for d in documents} <= {"fragrance", "dairy_aroma", "shared"}


def test_remise_volume():
    by_id = {o["order_id"]: o for o in g.orders}
    assert g.order_amount(by_id["ORD-2026-002"])[1] == 0     # 80 kg
    assert g.order_amount(by_id["ORD-2026-004"]) == (38400, 5, 36480.0)   # 800 kg
    assert g.order_amount(by_id["ORD-2026-007"])[1] == 10    # 1 200 kg


def test_toute_commande_de_projet_a_un_echantillon_valide():
    for order in g.orders:
        if order["project_id"]:
            assert any(s["project_id"] == order["project_id"] and s["decision"] == "Validé"
                       for s in g.samples), order["order_id"]


def test_fichiers_generes(tmp_path):
    g.main()
    lines = (g.RAG_DIR / "documents.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 103
    json.loads(lines[0])
    text = (g.BASE_DIR / "givaudan_data.txt").read_text(encoding="utf-8")
    assert text.count("\nChapter ") == 103


def test_suivi_commandes_meme_format_que_le_prototype():
    with open(g.DATA_DIR / "orders_tracking_dataset.csv", encoding="utf-8") as f:
        dataset_columns = next(csv.reader(f))
    with open(g.DATA_DIR / "orders_tracking_prototype.csv", encoding="utf-8") as f:
        prototype_columns = next(csv.reader(f))
    assert dataset_columns == prototype_columns


def test_dates_de_statut_coherentes():
    for order in g.orders:
        status_date = g.ORDER_STATUS_DATES[order["order_id"]]
        assert order["order_date"] <= status_date <= g.REFERENCE_DATE
