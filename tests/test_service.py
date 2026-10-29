"""Tests for the dependency-free HTTP audit service (pure handler layer)."""

from __future__ import annotations

from factuality_auditor.service import AuditService, handle


def _service() -> AuditService:
    return AuditService()


def test_health() -> None:
    status, payload = handle("GET", "/health", {}, _service())
    assert status == 200
    assert payload["status"] == "ok"
    assert payload["facts"] > 0


def test_audit_refuted() -> None:
    status, payload = handle(
        "POST", "/audit", {"text": "Paris is the capital of Germany."}, _service()
    )
    assert status == 200
    assert payload["hallucinated"] is True
    assert payload["claims"]["refuted"] == 1
    assert payload["verdicts"][0]["evidence"] == "france"


def test_audit_supported() -> None:
    status, payload = handle(
        "POST", "/audit", {"text": "Paris is the capital of France."}, _service()
    )
    assert status == 200
    assert payload["hallucinated"] is False
    assert payload["claims"]["supported"] == 1


def test_audit_rejects_missing_text() -> None:
    status, payload = handle("POST", "/audit", {}, _service())
    assert status == 400
    assert "text" in payload["error"]


def test_audit_rejects_overlong_text() -> None:
    status, _ = handle("POST", "/audit", {"text": "a" * 9000}, _service())
    assert status == 400


def test_unknown_route() -> None:
    status, payload = handle("GET", "/nope", {}, _service())
    assert status == 404
    assert "error" in payload


def test_ready_endpoint() -> None:
    status, payload = handle("GET", "/ready", {}, AuditService())
    assert status == 200
    assert payload["status"] == "ready"


def test_metrics_record_requests() -> None:
    service = AuditService()
    handle("POST", "/audit", {"text": "Paris is the capital of Germany."}, service)
    text = service.metrics.render_prometheus()
    assert "service_requests_total" in text
    assert 'route="POST /audit"' in text
    assert "service_request_duration_ms_bucket" in text
    assert service.metrics.total_requests >= 1
