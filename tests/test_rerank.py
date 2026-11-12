"""Reclassement des résultats de recherche."""

import rerank


def cand(doc_id, document_type, text, score):
    return {"doc_id": doc_id, "document_type": document_type, "text": text, "score": score}


def test_reference_exacte_passe_devant():
    candidates = [
        cand("project_PJ-009", "project", "PROJET DE CRÉATION | PJ-009 — … commande ORD-2026-007", 0.60),
        cand("order_ORD-2026-007", "order", "COMMANDE | ORD-2026-007 de Northstar Beverages", 0.55),
    ]
    ranked = rerank.rerank("Quel est le statut de la commande ORD-2026-007 ?", candidates, 2)
    assert ranked[0]["doc_id"] == "order_ORD-2026-007"


def test_reference_citee_hors_en_tete_sans_bonus():
    text = "PROJET DE CRÉATION | PJ-009 — " + "x" * 100 + " ORD-2026-007"
    candidates = [cand("project_PJ-009", "project", text, 0.5)]
    assert rerank.rerank("ORD-2026-007 ?", candidates, 1)[0]["score"] == 0.5


def test_intentions():
    assert "project" in rerank.question_intents("Où en est le projet de Lumina ?")
    assert "product" in rerank.question_intents("Je cherche un arôme fruité")
    assert "product" in rerank.question_intents("Which fragrance for a sunscreen?")
    assert "sample" in rerank.question_intents("Quel retour sur l'échantillon caramel ?")
    assert "order" in rerank.question_intents("Quel est le statut de la commande ?")


def test_regle_generale_prime_sur_la_commande():
    assert rerank.question_intents("Quelles informations pour passer une commande ?") == {"faq"}
    assert rerank.question_intents("Quelle remise pour une commande de 1000 kg ?") == {"faq"}


def test_sans_indice_l_ordre_est_conserve():
    candidates = [cand("a", "product", "A", 0.9), cand("b", "faq", "B", 0.8), cand("c", "order", "C", 0.7)]
    assert [c["doc_id"] for c in rerank.rerank("bonjour", candidates, 3)] == ["a", "b", "c"]


def test_top_k_respecte():
    candidates = [cand(str(i), "product", "x", 1 - i / 10) for i in range(10)]
    assert len(rerank.rerank("je cherche", candidates, 4)) == 4
