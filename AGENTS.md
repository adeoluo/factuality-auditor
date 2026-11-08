# AGENTS.md

Working notes for coding agents and contributors in **Factuality Auditor**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

Hallucination detection built from scratch: extract atomic claims, verify them against a knowledge base, and produce a calibrated factuality judgment.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `scripts/`: maintenance scripts (release, assets, data)
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/factuality_auditor/__init__.py`: Factuality Auditor - hallucination detection and calibration from scratch.
- `src/factuality_auditor/calibration.py`: Calibration metrics: is the auditor's confidence trustworthy? A confidence is well calibrated when, among predictions made with confidence around ``p``, a fraction close to ``p`` are correct.
- `src/factuality_auditor/cli.py`: Command line interface for the factuality auditor.
- `src/factuality_auditor/data.py`: A bundled knowledge base and a labeled set of answers to audit.
- `src/factuality_auditor/evaluation.py`: Evaluate the auditor on detection and calibration.
- `src/factuality_auditor/extraction.py`: Extract atomic factual claims from text as (subject, relation, object) triples.
- `src/factuality_auditor/knowledge.py`: A trusted knowledge base of facts used to verify claims.
- `src/factuality_auditor/observability.py`: In-process request metrics for the HTTP service.
- `src/factuality_auditor/scoring.py`: Aggregate per-claim audits into a document-level factuality judgment.
- `src/factuality_auditor/service.py`: A standard-library HTTP service exposing the factuality auditor.
- `src/factuality_auditor/text.py`: Deterministic normalization and sentence splitting.
- `src/factuality_auditor/types.py`: Core data types for the factuality auditor.
- `src/factuality_auditor/verification.py`: Verify extracted claims against the knowledge base.

## Commands

| Command | Purpose |
|---|---|
| `make help` | Show this help |
| `make setup` | Install dependencies and pre-commit hooks |
| `make format` | Format automatically |
| `make lint` | Lint (no fixes) |
| `make type` | Type-check |
| `make test` | Run tests |
| `make coverage` | Tests with coverage gate |
| `make evaluation` | Reproduce the results table |
| `make run` | Run the application entrypoint |
| `make diagram` | Render architecture diagram to SVG |
| `make docker-build` | Build the image |
| `make docker-up` | Run via docker compose |
| `make clean` | Remove caches and artifacts |
| `make all` | Full local gate (mirror of continuous integration) |
| `make changelog` | Regenerate CHANGELOG.md from Conventional Commits (git-cliff) |
| `make cut-release` | Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional) |

Run the full local gate (`make all`) before committing; CI runs the same checks.

## Conventions

- Commits follow Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`).
  The changelog and the next version number are derived from them.
- Every number quoted in the README is produced by a command in this repository. When behavior
  changes, rerun that command and update the number in the same commit.
- When a component is added, removed or renamed, update `docs/architecture/architecture.mmd`
  and re-render `architecture.svg` so the diagram matches the code.
- README sections keep their fixed order. Prose avoids em and en dashes and promotional wording.
- Tests accompany behavior changes; a bug fix comes with a test that fails without it.
- Releases are cut with `make cut-release`.

## Python notes

- Python is managed with `uv`; run commands through `uv run` so the locked environment is used.
- Lint and format with `ruff`; type-check with `mypy`; tests use `pytest`.
- Public functions carry type hints and a docstring that states the contract, not the steps.
