"""Evaluate the auditor on detection and calibration.

Two questions are measured over the labeled answer set:

* **Detection.** How well does flagging refuted claims identify hallucinated
  answers? Reported as precision, recall, and F1, against a baseline that trusts
  every answer (the implicit assumption that models do not hallucinate).
* **Calibration.** Is the auditor's confidence trustworthy? Reported as the
  expected calibration error, against an overconfident baseline that reports a
  fixed high confidence for every prediction.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from factuality_auditor.calibration import Prediction, expected_calibration_error
from factuality_auditor.data import ANSWERS, KNOWLEDGE, LabeledAnswer
from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.scoring import audit_document

_OVERCONFIDENT = 0.99


@dataclass(frozen=True)
class DetectionMetrics:
    """Precision, recall, and F1 for hallucination detection."""

    precision: float
    recall: float
    f1: float

    @classmethod
    def from_counts(
        cls, true_positive: int, false_positive: int, false_negative: int
    ) -> DetectionMetrics:
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return cls(precision, recall, f1)


def detection_metrics(
    answers: Sequence[LabeledAnswer] = ANSWERS, knowledge: KnowledgeBase = KNOWLEDGE
) -> DetectionMetrics:
    """Detection metrics for flagging refuted claims as hallucinations."""

    true_positive = false_positive = false_negative = 0
    for answer in answers:
        flagged = audit_document(answer.text, knowledge).is_hallucinated
        if flagged and answer.hallucinated:
            true_positive += 1
        elif flagged and not answer.hallucinated:
            false_positive += 1
        elif not flagged and answer.hallucinated:
            false_negative += 1
    return DetectionMetrics.from_counts(true_positive, false_positive, false_negative)


def baseline_detection_metrics(
    answers: Sequence[LabeledAnswer] = ANSWERS,
) -> DetectionMetrics:
    """The trust-everything baseline flags nothing."""

    false_negative = sum(1 for answer in answers if answer.hallucinated)
    return DetectionMetrics.from_counts(0, 0, false_negative)


def _predictions(
    answers: Sequence[LabeledAnswer], knowledge: KnowledgeBase
) -> list[tuple[bool, float]]:
    rows: list[tuple[bool, float]] = []
    for answer in answers:
        audit = audit_document(answer.text, knowledge)
        correct = audit.is_hallucinated == answer.hallucinated
        rows.append((correct, audit.confidence))
    return rows


def auditor_calibration_error(
    answers: Sequence[LabeledAnswer] = ANSWERS, knowledge: KnowledgeBase = KNOWLEDGE
) -> float:
    """Expected calibration error of the auditor's own confidence."""

    predictions = [Prediction(conf, correct) for correct, conf in _predictions(answers, knowledge)]
    return expected_calibration_error(predictions)


def overconfident_calibration_error(
    answers: Sequence[LabeledAnswer] = ANSWERS, knowledge: KnowledgeBase = KNOWLEDGE
) -> float:
    """Expected calibration error when every prediction claims fixed high confidence."""

    predictions = [
        Prediction(_OVERCONFIDENT, correct) for correct, _ in _predictions(answers, knowledge)
    ]
    return expected_calibration_error(predictions)


def format_report(
    answers: Sequence[LabeledAnswer] = ANSWERS, knowledge: KnowledgeBase = KNOWLEDGE
) -> str:
    """Render the detection and calibration results as text."""

    auditor = detection_metrics(answers, knowledge)
    baseline = baseline_detection_metrics(answers)
    auditor_error = auditor_calibration_error(answers, knowledge)
    overconfident_error = overconfident_calibration_error(answers, knowledge)
    lines = [
        "Hallucination detection",
        f"  {'method':<24}{'precision':>11}{'recall':>9}{'f1':>8}",
        f"  {'auditor':<24}{auditor.precision:>11.3f}{auditor.recall:>9.3f}{auditor.f1:>8.3f}",
        f"  {'trust-everything':<24}{baseline.precision:>11.3f}"
        f"{baseline.recall:>9.3f}{baseline.f1:>8.3f}",
        "",
        "Confidence calibration (expected calibration error, lower is better)",
        f"  {'auditor confidence':<30}{auditor_error:>8.3f}",
        f"  {'overconfident baseline':<30}{overconfident_error:>8.3f}",
    ]
    return "\n".join(lines)
