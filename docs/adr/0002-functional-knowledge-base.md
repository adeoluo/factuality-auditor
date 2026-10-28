# ADR-0002: A functional-fact knowledge base

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

To detect hallucinations the auditor must do more than fail to find support; it must be able
to say a claim is **wrong**. That requires knowing when a claimed fact contradicts a known
one.

## Decision

Model the knowledge base with **functional relations**: a subject and relation fix a single
correct object. A claim that asserts a different object for a known subject and relation is
refuted; a claim about an unknown subject is unverifiable.

## Alternatives considered

- **A set of true statements with no functional structure.** Supports confirmation but cannot
  distinguish a contradiction from a simple absence, so it cannot refute.
- **An open-world retrieval index.** More general, but adds dependencies and nondeterminism;
  functional facts keep the reference offline and exact.

## Consequences

- The auditor can refute contradictions and abstain on the unknown.
- Recall is bounded by the base's coverage, which the calibrated confidence makes explicit.
- A retrieval-backed verifier can replace the base behind the verification interface.
