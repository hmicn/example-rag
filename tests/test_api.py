"""Ingestion et API de bout en bout (embedding et LLM de test)."""

import ingest


def test_decoupage_une_section_par_fiche():
    text = ingest.config.DATASET_PATH.read_text(encoding="utf-8")
    _, sections = ingest.split_into_sections(text)
    assert len(sections) == 103
    assert all(ingest.get_document_type(title) != "unknown" for title, _ in sections)
    assert ingest.get_doc_id("Chapter 12: product_PR-001") == "product_PR-001"


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["indexed_documents"] == 123   # 103 du dataset + 20 de la base de connaissances
    assert body["rerank"] is True


def test_demo_ping(client):
    assert client.get("/demo/ping").json()["status"] == "ok"


def test_search_renvoie_les_champs_du_contrat(client):
    sources = client.post("/search", json={"question": "arôme mangue boisson protéinée"}).json()
    assert len(sources) == 4
    assert set(sources[0]) == {"section", "doc_id", "document_type", "domain", "text", "score", "rank_score"}
    # L'ordre des sources suit rank_score (similarité + bonus du reclassement).
    assert [s["rank_score"] for s in sources] == sorted((s["rank_score"] for s in sources), reverse=True)


def test_search_reference_exacte_en_premier(client):
    sources = client.post("/search", json={"question": "Quel est le statut de la commande ORD-2026-007 ?"}).json()
    assert sources[0]["doc_id"] == "order_ORD-2026-007"


def test_filtre_de_domaine(client):
    for domain in ("fragrance", "dairy_aroma"):
        sources = client.post("/search", json={"question": "produit floral fruité", "domain": domain, "top_k": 10}).json()
        assert {s["domain"] for s in sources} <= {domain, "shared"}


def test_ask(client):
    response = client.post("/ask", json={"question": "Où en est le projet PJ-003 ?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] and body["sources"]


def test_validation_de_la_requete(client):
    assert client.post("/ask", json={"question": ""}).status_code == 422
    assert client.post("/ask", json={"question": "x", "domain": "autre"}).status_code == 422


def test_orders_un_seul_format(client):
    dataset_order = client.get("/orders/ORD-2026-007").json()
    prototype_order = client.get("/orders/CMD-2026-003").json()
    assert set(dataset_order) == set(prototype_order)
    assert dataset_order["order_status"] == "Expédiée"
    assert client.get("/orders/ord-2026-010").json()["order_status"] == "Annulée"


def test_orders_introuvable(client):
    assert client.get("/orders/INCONNUE").status_code == 404


def test_cors_pour_les_interfaces_web(client):
    response = client.options("/ask", headers={
        "Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] in {"*", "http://localhost:5173"}


def test_contrat_openapi_a_jour(indexed):
    import json
    from pathlib import Path

    exported = json.loads((Path(__file__).resolve().parents[1] / "docs" / "openapi.json").read_text(encoding="utf-8"))
    assert exported == json.loads(json.dumps(indexed.app.openapi())), \
        "docs/openapi.json n'est plus à jour : lancer python export_openapi.py"
