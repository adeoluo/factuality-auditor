"""Aggregate per-claim audits into a document-level factuality judgment.

A document is judged **hallucinated** when any of its claims is refuted. The
auditor also emits a calibrated probability that the document is factual, formed
by combining per-claim truth probabilities, so downstream systems can threshold
on confidence rather than a hard label.
"""

from __future__ import annotations

from dataclasses import dataclass

from factuality_auditor.extraction import extract_claims
from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.types import ClaimAudit, Verdict
from factuality_auditor.verification import verify_claims

# Probability that a claim is true, by verdict.
_TRUTH_PROBABILITY = {
    Verdict.SUPPORTED: 0.95,
    Verdict.UNVERIFIABLE: 0.7,
    Verdict.REFUTED: 0.03,
}

# Used when a document yields no extractable claims.
_NO_CLAIMS_PROBABILITY = 0.7


@dataclass(frozen=True)
class DocumentAudit:
    """The audit of a whole document: its claims, judgment, and confidence."""

    audits: tuple[ClaimAudit, ...]
    probability_factual: float

    @property
    def supported(self) -> int:
        return sum(1 for audit in self.audits if audit.verdict is Verdict.SUPPORTED)

    @property
    def refuted(self) -> int:
        return sum(1 for audit in self.audits if audit.verdict is Verdict.REFUTED)

    @property
    def unverifiable(self) -> int:
        return sum(1 for audit in self.audits if audit.verdict is Verdict.UNVERIFIABLE)

    @property
    def is_hallucinated(self) -> bool:
        """A document is flagged when it contains a refuted claim."""

        return self.refuted > 0

    @property
    def confidence(self) -> float:
        """Confidence in the predicted label (factual or hallucinated)."""

        if self.is_hallucinated:
            return 1.0 - self.probability_factual
        return self.probability_factual


def audit_document(text: str, knowledge: KnowledgeBase) -> DocumentAudit:
    """Extract, verify, and aggregate the claims in a document."""

    audits = tuple(verify_claims(extract_claims(text), knowledge))
    if not audits:
        return DocumentAudit(audits, _NO_CLAIMS_PROBABILITY)
    probability = 1.0
    for audit in audits:
        probability *= _TRUTH_PROBABILITY[audit.verdict]
    return DocumentAudit(audits, probability)
