"""Calibration metrics: is the auditor's confidence trustworthy?

A confidence is well calibrated when, among predictions made with confidence
around ``p``, a fraction close to ``p`` are correct. The expected calibration
error bins predictions by confidence and averages the gap between mean
confidence and accuracy, weighted by bin size.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Prediction:
    """One prediction: the confidence placed in it and whether it was correct."""

    confidence: float
    correct: bool


@dataclass(frozen=True)
class CalibrationBin:
    """A confidence bin's count, mean confidence, and accuracy."""

    lower: float
    upper: float
    count: int
    mean_confidence: float
    accuracy: float


def _bin_predictions(predictions: Sequence[Prediction], bins: int) -> list[CalibrationBin]:
    edges = [index / bins for index in range(bins + 1)]
    result: list[CalibrationBin] = []
    for index in range(bins):
        lower, upper = edges[index], edges[index + 1]
        if index == bins - 1:
            members = [p for p in predictions if lower <= p.confidence <= upper]
        else:
            members = [p for p in predictions if lower <= p.confidence < upper]
        if not members:
            continue
        count = len(members)
        mean_confidence = sum(p.confidence for p in members) / count
        accuracy = sum(1 for p in members if p.correct) / count
        result.append(CalibrationBin(lower, upper, count, mean_confidence, accuracy))
    return result


def expected_calibration_error(predictions: Sequence[Prediction], bins: int = 10) -> float:
    """The size-weighted average gap between confidence and accuracy."""

    if not predictions:
        return 0.0
    total = len(predictions)
    error = 0.0
    for calibration_bin in _bin_predictions(predictions, bins):
        weight = calibration_bin.count / total
        error += weight * abs(calibration_bin.mean_confidence - calibration_bin.accuracy)
    return error


def reliability_table(predictions: Sequence[Prediction], bins: int = 10) -> list[CalibrationBin]:
    """Return the non-empty confidence bins for a reliability diagram."""

    return _bin_predictions(predictions, bins)
