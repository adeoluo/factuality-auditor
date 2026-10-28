# ADR-0003: Calibrated confidence and abstention

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

A factuality judgment is more useful as a trustworthy probability than a bare label,
especially because the auditor cannot verify claims outside its knowledge base and should not
pretend otherwise.

## Decision

Combine per-claim truth probabilities into a document-level probability of being factual, and
report the confidence in the predicted label. On unverifiable claims the auditor abstains
(predicts factual) with deliberately low confidence. Calibration is measured by the expected
calibration error against outcomes.

## Alternatives considered

- **Hard labels only.** Simpler, but gives downstream systems no way to threshold on risk.
- **Always-high confidence.** Looks decisive but is poorly calibrated, as the overconfident
  baseline shows (error 0.123 versus the auditor's 0.037).

## Consequences

- Confidence tracks accuracy: high on verifiable claims, low where the auditor abstains.
- The expected calibration error is a first-class, reported metric.
- The probability model is simple and inspectable, and can be replaced by a learned calibrator.
