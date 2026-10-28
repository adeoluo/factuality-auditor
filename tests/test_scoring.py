"""Tests for document scoring and calibration."""

from __future__ import annotations

from factuality_auditor import (
    KnowledgeBase,
    Prediction,
    audit_document,
    expected_calibration_error,
    reliability_table,
)

_KB = KnowledgeBase.from_triples(
    [
        ("Paris", "capital_of", "France"),
        ("Tokyo", "capital_of", "Japan"),
        ("Gold", "symbol_is", "Au"),
        ("Mars", "moon_count", "2"),
    ]
)


def test_factual_document_not_flagged() -> None:
    audit = audit_document("Paris is the capital of France. The symbol for Gold is Au.", _KB)
    assert audit.supported == 2
    assert audit.refuted == 0
    assert not audit.is_hallucinated
    assert audit.probability_factual > 0.8
    assert audit.confidence > 0.8


def test_hallucinated_document_flagged() -> None:
    audit = audit_document("Paris is the capital of Germany.", _KB)
    assert audit.refuted == 1
    assert audit.is_hallucinated
    assert audit.probability_factual < 0.1
    assert audit.confidence > 0.9


def test_unverifiable_document() -> None:
    audit = audit_document("Oslo is the capital of Norway.", _KB)
    assert audit.unverifiable == 1
    assert not audit.is_hallucinated


def test_no_claims_document() -> None:
    audit = audit_document("Hello there, how are you today?", _KB)
    assert audit.audits == ()
    assert not audit.is_hallucinated
    assert audit.probability_factual == 0.7


def test_perfect_calibration_has_zero_error() -> None:
    predictions = [Prediction(1.0, True) for _ in range(5)]
    assert expected_calibration_error(predictions) == 0.0


def test_overconfidence_has_high_error() -> None:
    predictions = [Prediction(1.0, index % 2 == 0) for index in range(10)]
    assert expected_calibration_error(predictions) == 0.5


def test_reliability_table_bins() -> None:
    predictions = [Prediction(0.95, True), Prediction(0.05, False)]
    table = reliability_table(predictions, bins=10)
    assert len(table) == 2
    assert expected_calibration_error([]) == 0.0
