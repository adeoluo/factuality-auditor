# Operations Guide - Factuality Auditor

The operational contract of the audit service.

## Running the service

```bash
uv run python -m factuality_auditor serve --host 0.0.0.0 --port 8000
```

A standard-library HTTP server with **zero runtime dependencies**. The knowledge base is
built once at startup and then serves stateless audits.

## Endpoints

| Method | Path | Body | Success |
|---|---|---|---|
| GET | `/health` | none | `{"status": "ok", "facts": N}` |
| POST | `/audit` | `{"text"}` | judgment, confidence, claim counts, per-claim verdicts |

Errors return JSON `{"error": ...}` with a 4xx status; malformed JSON yields `400`.

## Service level objectives

Measured by `benchmarks/stress.py` over a 1000 fact knowledge base on a developer laptop:

| Objective | Target | Observed (single worker) |
|---|---|---|
| Audit latency p50 | < 1 ms | about 0.04 ms |
| Audit latency p99 | < 1 ms | about 0.2 ms |
| Throughput | > 10000 audits/second/core | about 19000 audits/second |

Illustrative targets for the reference implementation.

## Operational constraints

- **Verification is an indexed lookup, so auditing is cheap and latency is flat.** The path
  is CPU bound and holds the global interpreter lock; throughput per process is already
  high, so scale with processes if a core saturates.
- **The knowledge base is in memory and immutable after startup.** Memory grows linearly
  with the number of facts; updates require a restart or a blue/green swap.
- **Inputs are bounded** to 4000 characters, so a single request cannot exhaust CPU on
  extraction.
- **Recall is bounded by knowledge-base coverage.** The auditor abstains with low,
  calibrated confidence on claims it cannot verify; absence of a refutation is not proof
  of truth. Treat low-confidence factual judgments accordingly.
- **No persistence, no authentication.** Front the service with a gateway.

## Failure modes and responses

| Symptom | Likely cause | Response |
|---|---|---|
| Hallucination not flagged | Claim subject outside the knowledge base | Expected; confidence is low, extend the base |
| `400` on input | Empty or overlong text | Inspect the `error` field |
| Memory growth at startup | Large knowledge base | Shard by subject namespace across replicas |

## Capacity planning

A single core serves on the order of 19000 audits per second. Provision replicas for
availability and for throughput beyond a single core; the service is stateless.
