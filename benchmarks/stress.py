"""A production-style stress benchmark for the audit service.

Drives the full audit handler (extraction, verification, scoring) under
sustained, concurrent load against a large knowledge base and reports throughput
with p50, p95, and p99 latency. Deterministic and offline; run with:

    uv run python benchmarks/stress.py
"""

from __future__ import annotations

import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.service import AuditService, handle


def _name(index: int) -> str:
    letters = ""
    value = index + 1
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        letters = chr(ord("a") + remainder) + letters
    return letters.capitalize()


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main() -> None:
    knowledge = KnowledgeBase.from_triples(
        [(f"City{_name(index)}", "capital_of", f"Country{_name(index)}") for index in range(1000)]
    )
    service = AuditService(knowledge=knowledge)
    rng = random.Random(0)
    requests = []
    for _ in range(3000):
        index = rng.randrange(1000)
        country = f"Country{_name(index)}" if rng.random() < 0.5 else f"Country{_name(index + 1)}"
        requests.append({"text": f"City{_name(index)} is the capital of {country}."})

    def one(body: dict[str, str]) -> float:
        start = time.perf_counter()
        handle("POST", "/audit", body, service)
        return (time.perf_counter() - start) * 1000

    print(f"Knowledge base: {len(knowledge)} facts | Requests: {len(requests)}")
    for workers in (1, 4, 8):
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            latencies = list(pool.map(one, requests))
        wall = time.perf_counter() - start
        print(
            f"workers={workers:<2}  "
            f"throughput={len(requests) / wall:>7.0f} req/s  "
            f"p50={statistics.median(latencies):>6.3f} ms  "
            f"p95={_percentile(latencies, 0.95):>6.3f} ms  "
            f"p99={_percentile(latencies, 0.99):>6.3f} ms"
        )


if __name__ == "__main__":
    main()
