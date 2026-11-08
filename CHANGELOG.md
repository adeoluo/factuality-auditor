# Changelog

All notable changes to this project are documented here. The file is generated
from Conventional Commits by [git-cliff](https://git-cliff.org) when a release is cut
with `make cut-release`.

## [0.1.1] 2026-11-08

### Documentation

- Complete citation metadata and bump it on release (#6)
- Map the threat model to OWASP LLM 2026 and MITRE ATLAS v2026.10 (#8)
- Add standards keywords to the citation metadata (#9)

### Maintenance

- Latest toolchain and CI versions (#5)
- Release script keeps hard-coded version strings in step (#7)

## [0.1.0] 2026-11-03

### Features

- Add claim extraction, a knowledge base, and verification
- Add document scoring and calibration metrics
- Add labeled dataset, detection and calibration evaluation, and CLI
- Add a deterministic audit micro-benchmark
- Add HTTP service, stress benchmark, and operations documentation
- Add production observability (metrics and readiness) and reword footer

### Documentation

- Write README, architecture diagram, and responsible-AI cards
- Use plain, factual wording (#13)
- Standard README structure and language framing (#15)
- Vertical layered architecture diagram
- Horizontal layered architecture diagram
- Compact horizontal architecture diagram
- Recorded demos of more commands, with their vhs tapes (#1)
- Recorded demos of the HTTP service and more commands (#2)
- Describe the supply chain accurately (#3)

### Build and CI

- Run CodeQL on main and on a weekly schedule only

### Maintenance

- Scaffold factuality-auditor project
- Bump continuous integration action versions and dev dependencies
- Remove Dependabot configuration
- Release tooling, changelog and agent guides (#4)
