"""Factuality Auditor - hallucination detection and calibration from scratch."""

from __future__ import annotations

from factuality_auditor.calibration import (
    CalibrationBin,
    Prediction,
    expected_calibration_error,
    reliability_table,
)
from factuality_auditor.evaluation import (
    DetectionMetrics,
    auditor_calibration_error,
    baseline_detection_metrics,
    detection_metrics,
    format_report,
    overconfident_calibration_error,
)
from factuality_auditor.extraction import extract_claims
from factuality_auditor.knowledge import RELATIONS, KnowledgeBase
from factuality_auditor.scoring import DocumentAudit, audit_document
from factuality_auditor.text import normalize, split_sentences
from factuality_auditor.types import Claim, ClaimAudit, Fact, Verdict
from factuality_auditor.verification import verify_claim, verify_claims

__version__ = "0.1.0"

__all__ = [
    "RELATIONS",
    "CalibrationBin",
    "Claim",
    "ClaimAudit",
    "DetectionMetrics",
    "DocumentAudit",
    "Fact",
    "KnowledgeBase",
    "Prediction",
    "Verdict",
    "audit_document",
    "auditor_calibration_error",
    "baseline_detection_metrics",
    "detection_metrics",
    "expected_calibration_error",
    "extract_claims",
    "format_report",
    "normalize",
    "overconfident_calibration_error",
    "reliability_table",
    "split_sentences",
    "verify_claim",
    "verify_claims",
]
