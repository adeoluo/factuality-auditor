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
| Supply-chain compromise | Malicious dependency | Code execution | No third-party runtime packages; development tools pinned in `uv.lock`; CodeQL in continuous integration |

## Standards mapping

The risk the auditor addresses and its own threats are mapped to the OWASP Top 10 for LLM
Applications 2026 and MITRE ATLAS v2026.10 (IDs and names checked against `ATLAS.yaml` from the
[v2026.10 release of mitre-atlas/atlas-data](https://github.com/mitre-atlas/atlas-data/releases)).
The OWASP Top 10 for Agentic Applications 2026 is not mapped because no agent is involved.

| What | OWASP LLM 2026 | MITRE ATLAS v2026.10 | Role of this project |
|---|---|---|---|
| Hallucinated claims in an answer (what the auditor checks) | LLM07:2026 Misinformation | AML.T0062 Discover LLM Hallucinations; AML.T0060 Publish Hallucinated Entities | Detects refutable claims before they are trusted, which narrows what an adversary can exploit |
| False confidence on the unknown | LLM07:2026 Misinformation | | Mitigates: calibrated abstention on unverifiable claims |
| Knowledge-base poisoning | LLM05:2026 Data and Model Poisoning; LLM07:2026 Misinformation | AML.T0059 Erode Dataset Integrity | Not mitigated: the caller owns the base |
| Oversized inputs to the HTTP service | LLM06:2026 Unbounded Consumption | AML.T0029 Denial of AI Service | Mitigates with a 4,000 character limit per request |
| Malicious dependency | LLM04:2026 Supply Chain | AML.T0010.001 Supply Chain Compromise: Software | Mitigates with no runtime dependencies and CodeQL |

In NIST AI 600-1 (Generative AI Profile) terms the project addresses the Confabulation and
Information Integrity risks.

## Residual risk

Recall is bounded by the knowledge base, so some hallucinations are not refutable; the
calibrated confidence makes that uncertainty explicit rather than hiding it.
