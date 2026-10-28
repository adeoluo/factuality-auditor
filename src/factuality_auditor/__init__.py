"""Factuality Auditor - hallucination detection and calibration from scratch."""

from __future__ import annotations

from factuality_auditor.extraction import extract_claims
from factuality_auditor.knowledge import RELATIONS, KnowledgeBase
from factuality_auditor.text import normalize, split_sentences
from factuality_auditor.types import Claim, ClaimAudit, Fact, Verdict
from factuality_auditor.verification import verify_claim, verify_claims

__version__ = "0.1.0"

__all__ = [
    "RELATIONS",
    "Claim",
    "ClaimAudit",
    "Fact",
    "KnowledgeBase",
    "Verdict",
    "extract_claims",
    "normalize",
    "split_sentences",
    "verify_claim",
    "verify_claims",
]
