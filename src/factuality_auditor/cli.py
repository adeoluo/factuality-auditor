"""Command line interface for the factuality auditor."""

from __future__ import annotations

import argparse

from factuality_auditor.data import KNOWLEDGE
from factuality_auditor.evaluation import format_report
from factuality_auditor.scoring import audit_document


def _cmd_evaluate(_: argparse.Namespace) -> None:
    print(format_report())


def _cmd_audit(args: argparse.Namespace) -> None:
    audit = audit_document(args.text, KNOWLEDGE)
    verdict = "HALLUCINATED" if audit.is_hallucinated else "factual"
    print(f"judgment: {verdict} (confidence {audit.confidence:.2f})")
    print(
        f"claims: {audit.supported} supported, {audit.refuted} refuted, "
        f"{audit.unverifiable} unverifiable"
    )
    for claim_audit in audit.audits:
        fact = claim_audit.claim.fact
        evidence = claim_audit.evidence
        suffix = f" (known: {evidence.object})" if evidence is not None else ""
        print(
            f"  [{claim_audit.verdict.value:>12}] "
            f"{fact.subject} / {fact.relation} / {fact.object}{suffix}"
        )


def _cmd_serve(args: argparse.Namespace) -> None:
    from factuality_auditor.service import serve

    serve(host=args.host, port=args.port)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="factuality-auditor", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("evaluate", help="detection and calibration on the labeled set")

    audit = sub.add_parser("audit", help="audit a single answer")
    audit.add_argument("text", help="the answer text to audit")

    serve = sub.add_parser("serve", help="start the HTTP audit service")
    serve.add_argument("--host", default="127.0.0.1", help="bind host")
    serve.add_argument("--port", type=int, default=8000, help="bind port")

    handlers = {"evaluate": _cmd_evaluate, "audit": _cmd_audit, "serve": _cmd_serve}
    args = parser.parse_args(argv)
    handlers[args.command](args)


if __name__ == "__main__":
    main()
