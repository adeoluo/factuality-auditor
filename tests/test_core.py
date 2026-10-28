"""Tests for normalization, extraction, the knowledge base, and verification."""

from __future__ import annotations

from factuality_auditor import (
    Fact,
    KnowledgeBase,
    Verdict,
    extract_claims,
    normalize,
    split_sentences,
    verify_claims,
)

_KB = KnowledgeBase.from_triples(
    [
        ("Paris", "capital_of", "France"),
        ("The Eiffel Tower", "located_in", "Paris"),
        ("Gold", "symbol_is", "Au"),
        ("Mars", "moon_count", "2"),
    ]
)


def test_normalize_strips_articles_and_punctuation() -> None:
    assert normalize("The Eiffel Tower!") == "eiffel tower"
    assert normalize("  Gold.  ") == "gold"


def test_split_sentences() -> None:
    assert split_sentences("A is B. C is D!") == ["A is B", "C is D"]


def test_extraction_patterns() -> None:
    claims = extract_claims("Paris is the capital of France.")
    assert claims[0].fact == Fact("paris", "capital_of", "france")
    claims = extract_claims("The capital of France is Paris.")
    assert claims[0].fact == Fact("paris", "capital_of", "france")
    claims = extract_claims("The Eiffel Tower is located in Paris.")
    assert claims[0].fact == Fact("eiffel tower", "located_in", "paris")
    claims = extract_claims("Mars has 2 moons.")
    assert claims[0].fact == Fact("mars", "moon_count", "2")


def test_knowledge_base_lookup() -> None:
    assert len(_KB) == 4
    fact = _KB.canonical("paris", "capital_of")
    assert fact is not None and fact.object == "france"
    assert _KB.canonical("berlin", "capital_of") is None


def test_verification_supported() -> None:
    audits = verify_claims(extract_claims("Paris is the capital of France."), _KB)
    assert audits[0].verdict is Verdict.SUPPORTED
    assert audits[0].evidence is not None
    assert audits[0].confidence == 0.95


def test_verification_refuted() -> None:
    audits = verify_claims(extract_claims("Paris is the capital of Germany."), _KB)
    assert audits[0].verdict is Verdict.REFUTED
    assert audits[0].evidence is not None and audits[0].evidence.object == "france"


def test_verification_unverifiable() -> None:
    audits = verify_claims(extract_claims("Oslo is the capital of Norway."), _KB)
    assert audits[0].verdict is Verdict.UNVERIFIABLE
    assert audits[0].evidence is None
    assert audits[0].confidence == 0.5


def test_moon_count_refuted() -> None:
    audits = verify_claims(extract_claims("Mars has 5 moons."), _KB)
    assert audits[0].verdict is Verdict.REFUTED
