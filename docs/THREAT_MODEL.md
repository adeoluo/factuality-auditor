# Threat Model - Factuality Auditor

## Assets

- Integrity of the verdicts, the document judgment, and the calibration numbers.

## Trust boundaries

- **Answers and claims are untrusted text.** They are parsed and compared, never executed;
  there is no path from text to execution.

## Threats and mitigations

| Threat | Vector | Impact | Mitigation |
|---|---|---|---|
| False confidence on the unknown | Claims outside the knowledge base | Trusting a hallucination | The auditor abstains with low, calibrated confidence |
| Knowledge-base poisoning | Wrong facts added to the base | Wrong verdicts | Verification is read-only; callers control the base |
| Overstated accuracy | Reporting only detection | Hidden miscalibration | Both detection and calibration are reported |
| Supply-chain compromise | Malicious dependency | Code execution | Zero runtime dependencies; Dependabot and CodeQL in continuous integration |

## Residual risk

Recall is bounded by the knowledge base, so some hallucinations are not refutable; the
calibrated confidence makes that uncertainty explicit rather than hiding it.
