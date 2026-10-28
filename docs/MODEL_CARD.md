# System Card - Factuality Auditor

## Overview

- **What it is:** a hallucination and factuality auditor - it extracts atomic claims, verifies
  them against a knowledge base, and produces a calibrated factuality judgment.
- **What it is not:** a generator or a general fact checker; it verifies claims expressible as
  functional facts in its knowledge base.
- **Version:** 0.1.0.

## Intended use

- **Primary use cases:** learning and demonstrating claim-level hallucination detection and
  confidence calibration; a from-scratch reference for verification pipelines.
- **Primary users:** engineers and researchers building factuality and safety tooling.

## Out-of-scope / prohibited use

- Not a substitute for human review on high-stakes facts.
- Recall is bounded by the knowledge base; absence of a refutation is not proof of truth.

## Performance

See the README: detection precision 1.000, recall 0.714, F1 0.833 versus 0.000 for the
baseline, and calibration error 0.037 versus 0.123 overconfident.

## Risks and limitations

- Rule-based extraction misses claims phrased outside its patterns.
- The knowledge base is small and covers five functional relations.

## Safety mitigations

- The auditor abstains with low confidence on unverifiable claims rather than guessing.
- Deterministic, offline, reproducible.

## Environmental / cost footprint

Negligible; all in-memory with no model calls.
