# Data Card - Factuality Auditor

The project bundles one small knowledge base and one labeled answer set. There is no training
data and nothing is downloaded.

## knowledge base (`src/factuality_auditor/data.py`)

- **Provenance:** hand-authored general-knowledge facts over five functional relations
  (capital_of, located_in, born_in, symbol_is, moon_count).
- **Licensing:** authored by this repository; MIT.

## labeled answers (`src/factuality_auditor/data.py`)

- **Provenance:** fifteen hand-authored answers, each labeled factual or hallucinated.
- **Composition:** supported-factual, refutable-hallucinated, and unverifiable answers (both
  factual and hallucinated), chosen so detection and calibration are both meaningful.
- **Known gaps:** small, English, general knowledge; a demonstration set, not a benchmark.

## Ethical considerations

All content is synthetic general knowledge with no personal, sensitive, or copyrighted
material.
