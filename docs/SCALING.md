# Scaling and Design Tradeoffs - Factuality Auditor

How the reference design grows, and the tradeoffs taken.

## Reference architecture (today)

A single process: an in-memory functional-fact knowledge base, the extraction, verification,
and scoring pipeline, and a standard-library HTTP service. Shared-nothing and stateless.

## Scaling path

| Stage | Bottleneck | Change |
|---|---|---|
| One process | CPU, global interpreter lock | One replica per core |
| One host | Knowledge-base memory | Horizontal replicas behind a load balancer |
| Large knowledge base | Memory per replica | Shard by subject namespace; route by subject |
| Messy prose | Rule-based extraction recall | Model-backed extractor behind the extraction interface |
| Open-domain claims | Fixed knowledge base | Retrieval-backed verification over a corpus |

Because replicas share nothing, throughput is approximately linear in replica count.

## Substantial tradeoffs

- **Functional knowledge base vs open-world retrieval.** Functional facts make refutation
  exact and the pipeline offline and deterministic, bounded by coverage. Retrieval-backed
  verification is open-domain but adds a dependency, nondeterminism, and the risk of
  retrieving wrong evidence. The reference chooses exactness; verification sits behind an
  interface for a later swap.
- **Rule-based extraction vs a model.** Rules are deterministic, free, and auditable but
  miss claims phrased outside their patterns. A model generalizes at the cost of latency,
  spend, and nondeterminism. Extraction is isolated behind `extract_claims`.
- **Abstention vs forced judgment.** Abstaining with low confidence on unverifiable claims
  keeps the auditor calibrated and honest, at the cost of lower recall. Forcing a judgment
  would raise recall but wreck calibration; the reference optimizes for trustworthy
  confidence.
- **Threads vs processes.** The pipeline is pure Python and GIL-bound, so processes, not
  threads, are the unit of scaling. The service is stateless to make that trivial.

## What would change under real load

Shard the knowledge base, run process-per-core replicas, and, for open-domain coverage,
move verification behind a retrieval service and extraction behind a batched model. The
scoring and calibration are unchanged; only what sits behind the interfaces changes.
