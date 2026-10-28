"""Verify extracted claims against the knowledge base.

For a claim ``(subject, relation, object)``:

* if the base holds exactly that fact, the claim is **supported**;
* if the base holds the same subject and relation but a different object, the
  claim **contradicts** a known fact and is **refuted**;
* otherwise the base has nothing to say and the claim is **unverifiable**.

Each verdict carries a confidence that later feeds the calibrated document score.
"""

from __future__ import annotations

from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.types import Claim, ClaimAudit, Verdict

_CONFIDENCE = {
    Verdict.SUPPORTED: 0.95,
    Verdict.REFUTED: 0.95,
    Verdict.UNVERIFIABLE: 0.5,
}


def verify_claim(claim: Claim, knowledge: KnowledgeBase) -> ClaimAudit:
    """Verify a single claim and return its audit."""

    canonical = knowledge.canonical(claim.fact.subject, claim.fact.relation)
    if canonical is None:
        return ClaimAudit(claim, Verdict.UNVERIFIABLE, None, _CONFIDENCE[Verdict.UNVERIFIABLE])
    if canonical.object == claim.fact.object:
        return ClaimAudit(claim, Verdict.SUPPORTED, canonical, _CONFIDENCE[Verdict.SUPPORTED])
    return ClaimAudit(claim, Verdict.REFUTED, canonical, _CONFIDENCE[Verdict.REFUTED])


def verify_claims(claims: list[Claim], knowledge: KnowledgeBase) -> list[ClaimAudit]:
    """Verify every claim against the knowledge base."""

    return [verify_claim(claim, knowledge) for claim in claims]
