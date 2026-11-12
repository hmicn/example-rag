"""Reclassement des résultats de recherche.

La recherche vectorielle (ou lexicale) renvoie des documents proches de la
question, mais confond souvent des documents qui parlent des mêmes choses :
un projet et le produit qu'il utilise, une commande et une autre du même
client… Ce module réordonne une liste de candidats avec deux règles simples
et explicables :

1. Référence exacte : si la question cite une référence (ORD-2026-007,
   FRG-108, PJ-003…), le document dont c'est la référence principale
   (elle apparaît dans son en-tête) passe devant.
2. Type de question : quelques tournures indiquent le type de document
   recherché (« où en est » → projet, « je cherche » → produit, « retour sur
   l'échantillon » → échantillon, « statut de la commande » → commande).
   Le bonus est faible : il départage des documents proches sans écraser
   la similarité.

Les règles sont génériques et n'ont pas été réglées cas par cas ; leur effet
est mesuré sur les 30 cas de référence ET sur 10 cas inédits.
"""

from __future__ import annotations

import re
import unicodedata

# Nombre de candidats examinés = top_k × CANDIDATE_FACTOR.
CANDIDATE_FACTOR = 5
REFERENCE_BONUS = 0.5
TYPE_BONUS = 0.1
# Nombre de caractères du début du document où une référence est « principale ».
HEADER_LENGTH = 80

REFERENCE_RE = re.compile(
    r"\b(ORD-\d{4}-\d{3}|CMD-\d{4}-\d{3}|(?:FRG|FLV|ARM)-\d{3}|PJ-\d{3}|SMP-\d{3}|CL-\d{3}|RM-\d{3})\b",
    re.IGNORECASE,
)

# Tournures (sans accents, en minuscules) -> type de document attendu.
INTENT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("project", re.compile(r"\bou en est\b|\bavancement\b|\bprojet\b|\bproject\b|prochain echantillon|combien de versions")),
    ("sample", re.compile(r"\b(retour|avis|note|feedback)\b.*\bechantillon|\bechantillon\b.*\b(retour|avis|note|valide)|\bv[1-9]\b.*\bechantillon|premiere version")),
    ("order", re.compile(r"\b(statut|montant|livree?|expediee?|annulee?|en cours)\b.*\bcommande\b|\bcommande\b.*\b(statut|montant|livree?|expediee?|annulee?|en cours)\b")),
    ("product", re.compile(r"\bje cherche\b|\bavez-vous\b|\bproposez\b|\bconvien|\bquel arome\b|\bquelle fragrance\b|\bwhich (fragrance|flavou?r)\b")),
]

# Ces tournures désignent une règle générale de la plateforme, pas un dossier précis.
GENERAL_RULE_RE = re.compile(r"\bcomment\b|\bpasser une commande\b|\bremise\b|\binclus|\bcombien coute\b|\bgratuit")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def question_intents(question: str) -> set[str]:
    """Types de documents suggérés par la formulation de la question."""
    q = normalize(question)
    if GENERAL_RULE_RE.search(q):
        return {"faq"}
    return {doc_type for doc_type, pattern in INTENT_PATTERNS if pattern.search(q)}


def question_references(question: str) -> set[str]:
    return {ref.upper() for ref in REFERENCE_RE.findall(question)}


def rerank(question: str, candidates: list[dict], top_k: int) -> list[dict]:
    """Réordonne des candidats {doc_id, document_type, text, score} et garde top_k.

    Le score d'origine (similarité) est conservé ; chaque candidat reçoit
    rank_score = score + bonus, qui est la valeur utilisée pour le tri.
    """
    references = question_references(question)
    intents = question_intents(question)

    def boosted(candidate: dict) -> float:
        bonus = 0.0
        header = candidate["text"][:HEADER_LENGTH].upper()
        if references and any(ref in header for ref in references):
            bonus += REFERENCE_BONUS
        if candidate.get("document_type") in intents:
            bonus += TYPE_BONUS
        return candidate["score"] + bonus

    ranked = [dict(c, rank_score=round(boosted(c), 4)) for c in candidates]
    return sorted(ranked, key=lambda c: c["rank_score"], reverse=True)[:top_k]
