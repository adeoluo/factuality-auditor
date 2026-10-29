"""A dependency-free HTTP service exposing the factuality auditor.

The service builds the knowledge base once at startup and audits answers against
it. A pure handler is separated from the socket binding for testing.

Endpoints
---------
``GET  /health``   liveness and knowledge-base size.
``POST /audit``    body ``{"text": str}``; returns the judgment, calibrated
                   confidence, claim counts, and per-claim verdicts.
"""

from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from factuality_auditor.data import KNOWLEDGE
from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.observability import ServiceMetrics
from factuality_auditor.scoring import audit_document

JsonObject = dict[str, Any]
_MAX_TEXT_CHARS = 4000


@dataclass(frozen=True)
class AuditService:
    """Holds the knowledge base and audits answers."""

    knowledge: KnowledgeBase = KNOWLEDGE
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)

    def audit(self, text: str) -> JsonObject:
        audit = audit_document(text, self.knowledge)
        return {
            "text": text,
            "hallucinated": audit.is_hallucinated,
            "confidence": round(audit.confidence, 4),
            "probability_factual": round(audit.probability_factual, 4),
            "claims": {
                "supported": audit.supported,
                "refuted": audit.refuted,
                "unverifiable": audit.unverifiable,
            },
            "verdicts": [
                {
                    "subject": claim_audit.claim.fact.subject,
                    "relation": claim_audit.claim.fact.relation,
                    "object": claim_audit.claim.fact.object,
                    "verdict": claim_audit.verdict.value,
                    "evidence": (
                        claim_audit.evidence.object if claim_audit.evidence is not None else None
                    ),
                }
                for claim_audit in audit.audits
            ],
        }


def _validate_text(body: Mapping[str, Any]) -> str:
    text = body.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' must be a non-empty string")
    if len(text) > _MAX_TEXT_CHARS:
        raise ValueError(f"'text' exceeds {_MAX_TEXT_CHARS} characters")
    return text


def _route(
    method: str, path: str, body: Mapping[str, Any], service: AuditService
) -> tuple[int, JsonObject]:
    if method == "GET" and path == "/health":
        return 200, {"status": "ok", "facts": len(service.knowledge)}
    if method == "POST" and path == "/audit":
        try:
            text = _validate_text(body)
        except ValueError as error:
            return 400, {"error": str(error)}
        return 200, service.audit(text)
    return 404, {"error": f"no route for {method} {path}"}


def handle(
    method: str, path: str, body: Mapping[str, Any], service: AuditService
) -> tuple[int, JsonObject]:
    """Route a request, recording per-route metrics, and return status and payload."""

    if method == "GET" and path == "/ready":
        return 200, {"status": "ready"}
    start = time.perf_counter()
    status, payload = _route(method, path, body, service)
    service.metrics.observe(
        f"{method} {path}", (time.perf_counter() - start) * 1000.0, error=status >= 400
    )
    return status, payload


class _Handler(BaseHTTPRequestHandler):  # pragma: no cover - exercised over sockets
    service: AuditService

    def _respond(self, status: int, payload: JsonObject) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/metrics":
            body = self.service.metrics.render_prometheus().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        status, payload = handle("GET", self.path, {}, self.service)
        self._respond(status, payload)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._respond(400, {"error": "request body is not valid JSON"})
            return
        status, payload = handle("POST", self.path, body, self.service)
        self._respond(status, payload)

    def log_message(self, *_: Any) -> None:
        return


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:  # pragma: no cover
    """Start the HTTP service (blocking)."""

    handler = type("_BoundHandler", (_Handler,), {"service": AuditService()})
    server = ThreadingHTTPServer((host, port), handler)
    print(f"factuality-auditor service listening on http://{host}:{port}")
    server.serve_forever()
