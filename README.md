<h1 align="center">Factuality Auditor</h1>

<p align="center">
  <em>Hallucination detection built from scratch: extract atomic claims, verify them against a knowledge base, and produce a calibrated factuality judgment.</em>
</p>

<p align="center">
  <a href="https://github.com/adeoluo/factuality-auditor/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/adeoluo/factuality-auditor/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/adeoluo/factuality-auditor/releases"><img alt="Release" src="https://img.shields.io/github/v/release/adeoluo/factuality-auditor"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14%20%7C%203.15-blue">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green"></a>
</p>

---

## Motivation

A language model's answer can be fluent and wrong. Catching that requires checking the
answer's **individual factual claims** against trusted knowledge, and, just as importantly,
knowing **how much to trust the check itself**. This project builds a factuality auditor
**from scratch**: it decomposes an answer into atomic claims, verifies each against a
knowledge base, judges the whole answer, and reports a **calibrated confidence** so a
downstream system can act on a probability rather than a bare label. It is offline and
deterministic.

## Architecture

<p align="center">
  <img src="docs/architecture/architecture.svg" alt="Architecture diagram" width="860">
</p>

<sub>Legend: amber = entry points and external systems, indigo = core logic, green = data and state, blue = validation and control, grey = observability and outputs.</sub>

The CLI and the HTTP service (which first bounds the text length) share one deterministic
pipeline. An answer is normalized and split into sentences, rule-based extraction turns
them into claims, each claim is verified against the knowledge base (supported, refuted, or
unverifiable), and the verdicts are aggregated into a document judgment with a confidence.
On the labeled set, detection metrics compare the auditor with a trust-everything baseline
and a calibration metric checks the confidence against outcomes; every route also records
latency and errors for `/metrics`. See the [ADRs](docs/adr/) for the key design choices.

### How verification works

The knowledge base holds **functional facts**: a subject and relation fix a single correct
object (a country has one capital, an element one symbol). This is what lets the auditor
**refute** a claim rather than merely fail to support it:

- **Supported**: the base holds exactly the claimed fact.
- **Refuted**: the base holds the same subject and relation but a **different** object, so
  the claim contradicts known fact.
- **Unverifiable**: the base has nothing on that subject, so the auditor **abstains** with
  low confidence instead of guessing.

### Components

- **extraction**: rule-based mapping of sentences to (subject, relation, object) claims.
- **knowledge**: a functional-fact knowledge base supporting contradiction checks.
- **verification**: supported, refuted, or unverifiable, each with a confidence.
- **scoring**: aggregate claims into a document judgment and a calibrated probability.
- **calibration**: reliability bins and expected calibration error.
- **evaluation**: detection and calibration on the labeled set.

## Results

> Reproduce with `python -m factuality_auditor evaluate`. A labeled set of fifteen answers
> spanning supported, refutable-hallucinated, and unverifiable claims.

**Hallucination detection**

| Method | precision | recall | F1 |
|---|---:|---:|---:|
| **auditor** | **1.000** | **0.714** | **0.833** |
| trust-everything baseline | 0.000 | 0.000 | 0.000 |

**Confidence calibration** (expected calibration error, lower is better)

| Method | expected calibration error |
|---|---:|
| **auditor confidence** | **0.037** |
| overconfident baseline | 0.123 |

The auditor flags **every refutable hallucination with perfect precision**. It misses only
hallucinations whose subject lies outside its knowledge base, where it correctly **abstains
with low confidence** rather than guessing. That honesty is exactly what the calibration
number captures: the auditor's confidence tracks its accuracy (error 0.037), whereas an
overconfident baseline that always reports high confidence is far less trustworthy (0.123).

### Scale

To check that the audit pipeline holds up at volume, `benchmarks/scale.py` runs
`audit_document` over deterministically generated answer sets at growing sizes, auditing
each answer against a same-sized knowledge base of capital-of facts. Half of every batch
is factual and half is hallucinated (wrong country), so detection precision and recall
are measured against the known labels, while wall-clock time, throughput, and peak memory
(via the standard-library `tracemalloc`) are recorded. The data is synthetic and the
numbers are environment-specific, but the shape is the point: throughput stays roughly
flat and memory grows linearly with the workload, while detection stays exact on this
clean synthetic set.

| Answers | Wall-clock (s) | Throughput (answers/s) | Peak memory (MiB) | Precision | Recall |
|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.063 | ~16,000 | 0.57 | 1.000 | 1.000 |
| 4,000 | 0.265 | ~15,100 | 2.12 | 1.000 | 1.000 |
| 16,000 | 1.071 | ~14,900 | 8.95 | 1.000 | 1.000 |
| 32,000 | 2.460 | ~13,000 | 18.35 | 1.000 | 1.000 |

Reproduce with `uv run python benchmarks/scale.py`.

### Performance and reliability

A deterministic micro-benchmark (`uv run python benchmarks/benchmark.py`) audits a thousand
answers against a thousand-fact knowledge base end to end (extraction, verification, and
scoring), reporting throughput. On a laptop the auditor sustains tens of thousands of answers
per second, because verification is an indexed lookup rather than a model call.

A production-style stress benchmark (`uv run python benchmarks/stress.py`) drives the full
audit handler under concurrent load and reports throughput with p50, p95, and p99 latency,
confirming flat, sub-millisecond latency because verification is an indexed lookup. The
scaling path and tradeoffs are in [docs/SCALING.md](docs/SCALING.md), and a full audit
walk-through (including the honest-abstention case) is in the [case study](docs/CASE_STUDY.md).

## Quickstart

```bash
git clone https://github.com/adeoluo/factuality-auditor.git && cd factuality-auditor
make setup                    # install dev tooling + pre-commit hooks
make all                      # lint + type-check + test

python -m factuality_auditor evaluate                   # detection + calibration
python -m factuality_auditor audit "Mars has 5 moons."
```

Use the library directly:

```python
from factuality_auditor import KnowledgeBase, audit_document

knowledge = KnowledgeBase.from_triples([("Paris", "capital_of", "France")])
audit = audit_document("Paris is the capital of Germany.", knowledge)
print(audit.is_hallucinated, round(audit.confidence, 2))
```

## Usage

### Command line

```text
$ python -m factuality_auditor audit "Paris is the capital of Germany."
judgment: HALLUCINATED (confidence 0.97)
claims: 0 supported, 1 refuted, 0 unverifiable
  [     refuted] paris / capital_of / germany (known: france)
```

### HTTP service

A standard-library HTTP service exposes the auditor as a production-style JSON API:

```bash
python -m factuality_auditor serve --port 8000

curl localhost:8000/health
curl -s -X POST localhost:8000/audit -d '{"text": "Paris is the capital of Germany."}'
```

`GET /health` reports the knowledge-base size; `POST /audit` returns the judgment, the
calibrated confidence, claim counts, and per-claim verdicts with contradicting evidence.
See the [operations guide](docs/OPERATIONS.md) for the service contract and constraints.
The service also exposes `GET /ready` (readiness) and `GET /metrics` (per-route request, error, and latency metrics in Prometheus text format).

### Demos

Recorded from real runs with [vhs](https://github.com/charmbracelet/vhs); each tape is in `docs/demo/`.

Auditing a false claim against the evidence, then the evaluation.

<p align="center">
  <img src="docs/demo/audit.gif" alt="Auditing a false claim against the evidence, then the evaluation" width="860">
</p>

The HTTP service auditing a false claim.

<p align="center">
  <img src="docs/demo/http.gif" alt="The HTTP service auditing a false claim" width="860">
</p>

A supported claim and a refuted claim, audited against the evidence.

<p align="center">
  <img src="docs/demo/audit-more.gif" alt="A supported claim and a refuted claim, audited against the evidence" width="860">
</p>

## Design decisions

- **A functional knowledge base.** Functional relations are what make refutation possible, so
  the auditor can say a claim is wrong, not just unproven.
  ([ADR-0002](docs/adr/0002-functional-knowledge-base.md))
- **Calibrated confidence and abstention.** The auditor is confident on verifiable claims and
  deliberately uncertain on claims outside its knowledge, which calibration rewards.
  ([ADR-0003](docs/adr/0003-calibrated-confidence.md))

## Testing

```bash
make test        # uv run pytest
make coverage    # pytest with an 80% coverage gate, as in CI
make lint type   # ruff format check, ruff lint, mypy
```

- `tests/test_core.py`: text normalization, sentence splitting, claim-extraction patterns, knowledge-base lookup, and the supported, refuted, and unverifiable verdicts.
- `tests/test_scoring.py`: document judgments (factual, hallucinated, unverifiable, no claims) and calibration error and reliability bins.
- `tests/test_evaluation.py`: detection precision, the trust-everything baseline, calibration against the overconfident baseline, report formatting, and the command-line interface.
- `tests/test_service.py`: the HTTP handler layer, including health, readiness, metrics, `/audit` verdicts, input validation, and unknown routes.

CI runs ruff format, ruff lint, mypy, and pytest with the coverage gate on Python 3.12, 3.13, 3.14 and 3.15, then builds the package and the Docker image.

## Responsible AI

- **Model card:** [docs/MODEL_CARD.md](docs/MODEL_CARD.md)
- **Data card:** [docs/DATA_CARD.md](docs/DATA_CARD.md)
- **Threat model:** [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)
- **Standards:** the [threat model](docs/THREAT_MODEL.md#standards-mapping) maps the auditor to
  LLM07:2026 Misinformation in the OWASP Top 10 for LLM Applications 2026, to MITRE ATLAS
  v2026.10 (AML.T0062 Discover LLM Hallucinations) and to the Confabulation risk in NIST AI
  600-1.

## Limitations

- Extraction is rule-based; messy prose needs a model-backed extractor (a deliberate boundary
  to keep the pipeline from scratch and inspectable).
- The knowledge base is small and covers five functional relations; recall is bounded by its
  coverage, which the calibrated confidence makes explicit.
- The bundled set is a demonstration, not a competitive benchmark.

## Roadmap

- [ ] A model-backed claim extractor behind the existing interface
- [ ] Retrieval-backed verification over a document corpus
- [ ] Temperature scaling and a learned calibrator over claim features

## License

Released under the [MIT License](LICENSE).
