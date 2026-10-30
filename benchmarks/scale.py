"""A large-workload scale benchmark for the core audit pipeline.

Where ``benchmark.py`` quotes peak audit throughput and ``stress.py`` drives the
HTTP service under concurrent load, this script measures the core operation -
:func:`audit_document`, which extracts, verifies, and scores the claims in a
document - on progressively larger synthetic workloads. It reports wall-clock
time, throughput, peak memory (via the standard-library :mod:`tracemalloc`), and
hallucination-detection precision and recall so the README can show how the
auditor behaves as the knowledge base and answer set grow.

The knowledge base and answers are generated deterministically (nothing is
downloaded), so the run is reproducible and fully offline. Run with:

    uv run python benchmarks/scale.py
"""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass

from factuality_auditor.evaluation import DetectionMetrics
from factuality_auditor.knowledge import KnowledgeBase
from factuality_auditor.scoring import audit_document

WORKLOAD_SIZES: tuple[int, ...] = (1_000, 4_000, 16_000, 32_000)


def _name(index: int) -> str:
    letters = ""
    value = index + 1
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        letters = chr(ord("a") + remainder) + letters
    return letters.capitalize()


@dataclass(frozen=True, slots=True)
class ScaleRow:
    """One measured row of the scale sweep."""

    size: int
    seconds: float
    throughput: float
    peak_mib: float
    precision: float
    recall: float


def run_workload(size: int) -> ScaleRow:
    """Audit ``size`` synthetic answers against a knowledge base of ``size`` facts.

    Half the answers are factual and half are hallucinated (they name the wrong
    country), so detection precision and recall can be measured against the known
    labels. Timing and memory cover the per-answer audit loop.
    """
    tracemalloc.start()
    triples = [(f"City{_name(i)}", "capital_of", f"Country{_name(i)}") for i in range(size)]
    knowledge = KnowledgeBase.from_triples(triples)
    answers: list[tuple[str, bool]] = []
    for i in range(size):
        if i % 2 == 0:
            answers.append((f"City{_name(i)} is the capital of Country{_name(i)}.", False))
        else:
            answers.append((f"City{_name(i)} is the capital of Country{_name(i + 1)}.", True))

    true_positive = false_positive = false_negative = 0
    start = time.perf_counter()
    for text, hallucinated in answers:
        flagged = audit_document(text, knowledge).is_hallucinated
        if flagged and hallucinated:
            true_positive += 1
        elif flagged and not hallucinated:
            false_positive += 1
        elif not flagged and hallucinated:
            false_negative += 1
    elapsed = time.perf_counter() - start
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    metrics = DetectionMetrics.from_counts(true_positive, false_positive, false_negative)
    throughput = size / elapsed if elapsed > 0 else float("inf")
    return ScaleRow(
        size, elapsed, throughput, peak / (1024 * 1024), metrics.precision, metrics.recall
    )


def main() -> None:
    print("Factuality Auditor scale benchmark")
    print("Data is SYNTHETIC: capital-of facts and answers generated deterministically.\n")
    header = (
        f"{'answers':>9}  {'seconds':>8}  {'answers/sec':>12}  "
        f"{'peak MiB':>9}  {'precision':>10}  {'recall':>8}"
    )
    print(header)
    print("-" * len(header))
    for size in WORKLOAD_SIZES:
        row = run_workload(size)
        print(
            f"{row.size:>9,}  {row.seconds:>8.3f}  {row.throughput:>12,.0f}  "
            f"{row.peak_mib:>9.2f}  {row.precision:>10.3f}  {row.recall:>8.3f}"
        )


if __name__ == "__main__":
    main()
