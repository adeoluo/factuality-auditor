"""Core data types for the factuality auditor."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    """The result of verifying a single claim against the knowledge base."""

    SUPPORTED = "supported"
    REFUTED = "refuted"
    UNVERIFIABLE = "unverifiable"


@dataclass(frozen=True)
class Fact:
    """A normalized (subject, relation, object) triple."""

    subject: str
    relation: str
    object: str

    def key(self) -> tuple[str, str]:
        """The functional key: a subject and relation that fix the object."""

        return (self.subject, self.relation)


@dataclass(frozen=True)
class Claim:
    """An atomic factual claim extracted from text, as a triple plus its source."""

    fact: Fact
    source_text: str


@dataclass(frozen=True)
class ClaimAudit:
    """A claim paired with its verdict, supporting evidence, and confidence."""

    claim: Claim
    verdict: Verdict
    evidence: Fact | None
    confidence: float
