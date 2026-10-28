# Evaluation Report - Factuality Auditor

> Reproduce with `python -m factuality_auditor evaluate`. Deterministic and offline.

## Setup

- **Knowledge base:** functional facts over five relations.
- **Answers:** fifteen labeled answers spanning supported, refutable-hallucinated, and
  unverifiable (factual and hallucinated) cases.
- **Metrics:** hallucination detection (precision, recall, F1) and expected calibration error.
- **Baselines:** a trust-everything detector and an overconfident calibrator.

## Results

| Method | precision | recall | F1 |
|---|---:|---:|---:|
| auditor | 1.000 | 0.714 | 0.833 |
| trust-everything | 0.000 | 0.000 | 0.000 |

| Method | expected calibration error |
|---|---:|
| auditor confidence | 0.037 |
| overconfident baseline | 0.123 |

## Interpretation

The auditor flags every refutable hallucination and never flags a factual answer, giving
perfect precision. Its recall is below one because some hallucinations concern subjects
outside the knowledge base; there the auditor abstains with low confidence rather than
guessing. That calibrated honesty is visible in the expected calibration error: the auditor's
confidence tracks its accuracy (0.037), while an overconfident baseline that always reports
high confidence is much less trustworthy (0.123). Detection and calibration together tell the
whole story, measured on held-out, labeled answers.

## Reproducibility

Everything is offline and deterministic; the numbers regenerate exactly.
