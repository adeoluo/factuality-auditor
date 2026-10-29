# End-to-End Case Study - Auditing a Generated Answer

How one answer is decomposed, verified, judged, and scored with calibrated confidence.

## Scenario

A generator produces an answer that is fluent but wrong:

> "Paris is the capital of Germany."

A string match would not catch this; the sentence is well formed. Catching it requires
checking the claim against trusted knowledge.

## Trace

```bash
curl -s -X POST localhost:8000/audit -d '{"text": "Paris is the capital of Germany."}'
```

```json
{
  "hallucinated": true,
  "confidence": 0.97,
  "claims": {"supported": 0, "refuted": 1, "unverifiable": 0},
  "verdicts": [
    {"subject": "paris", "relation": "capital_of", "object": "germany",
     "verdict": "refuted", "evidence": "france"}
  ]
}
```

The auditor extracts the claim `(paris, capital_of, germany)`, finds the knowledge base
holds `(paris, capital_of, france)`, and **refutes** the claim, flagging the answer with
high confidence and citing the contradicting fact.

## The honest-abstention case

```bash
curl -s -X POST localhost:8000/audit -d '{"text": "Oslo is the capital of Norway."}'
```

If Norway is outside the knowledge base, the auditor returns `hallucinated: false` with a
**low** confidence (about 0.7): it cannot verify the claim and says so rather than
guessing. That calibrated honesty is what the expected calibration error measures (0.037
for the auditor versus 0.123 for an overconfident baseline).

## What an operator sees

- **Latency.** An indexed lookup; p50 about 0.04 ms.
- **Auditability.** Every verdict names the subject, relation, object, and the contradicting
  evidence.
- **Trustworthy confidence.** High on verifiable claims, low where the auditor abstains, so
  a caller can threshold on risk.

## Takeaway

Checking an answer's atomic claims against trusted knowledge, and being honest about what
cannot be checked, turns a fluent-but-wrong answer into a flagged, cited, calibrated result.
