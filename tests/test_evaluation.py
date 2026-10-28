"""Tests for detection and calibration evaluation and the command line interface."""

from __future__ import annotations

from factuality_auditor.cli import main
from factuality_auditor.evaluation import (
    auditor_calibration_error,
    baseline_detection_metrics,
    detection_metrics,
    format_report,
    overconfident_calibration_error,
)


def test_detection_precision_is_perfect() -> None:
    metrics = detection_metrics()
    assert metrics.precision == 1.0
    assert 0.0 < metrics.recall < 1.0
    assert metrics.f1 > 0.8


def test_baseline_detects_nothing() -> None:
    metrics = baseline_detection_metrics()
    assert metrics.precision == 0.0
    assert metrics.recall == 0.0
    assert metrics.f1 == 0.0


def test_auditor_is_better_calibrated_than_overconfident() -> None:
    auditor = auditor_calibration_error()
    overconfident = overconfident_calibration_error()
    assert auditor < overconfident
    assert auditor < 0.1


def test_format_report_contents() -> None:
    report = format_report()
    assert "Hallucination detection" in report
    assert "expected calibration error" in report
    assert "auditor" in report


def test_cli_evaluate(capsys) -> None:
    main(["evaluate"])
    out = capsys.readouterr().out
    assert "detection" in out.lower()


def test_cli_audit_refuted(capsys) -> None:
    main(["audit", "Paris is the capital of Germany."])
    out = capsys.readouterr().out
    assert "HALLUCINATED" in out
    assert "refuted" in out


def test_cli_audit_supported(capsys) -> None:
    main(["audit", "Paris is the capital of France."])
    out = capsys.readouterr().out
    assert "factual" in out
