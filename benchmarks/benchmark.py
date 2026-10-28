"""A micro-benchmark for the audit pipeline.

Measures end-to-end audit throughput (extraction, verification, and scoring)
over a synthetic set of answers against a knowledge base, so the README can
quote concrete numbers. Deterministic and offline; run with:

    uv run python benchmarks/benchmark.py
"""

from __future__ import annotations

import time

from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.scoring import audit_document


def _name(index: int) -> str:
    letters = ""
    value = index + 1
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        letters = chr(ord("a") + remainder) + letters
    return letters.capitalize()


def main() -> None:
    triples = [
        (f"City{_name(index)}", "capital_of", f"Country{_name(index)}") for index in range(1000)
    ]
    knowledge = KnowledgeBase.from_triples(triples)

    answers = [
        f"City{_name(index)} is the capital of Country{_name(index)}." for index in range(1000)
    ]

    start = time.perf_counter()
    for answer in answers:
        audit_document(answer, knowledge)
    elapsed = time.perf_counter() - start

    print(f"Knowledge base: {len(knowledge)} facts | Answers: {len(answers)}")
    print(f"Audit throughput: {len(answers) / elapsed:.0f} answers/sec")


if __name__ == "__main__":
    main()
