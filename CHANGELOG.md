# Changelog

All notable changes to this project are documented here. The file is generated
from Conventional Commits by [git-cliff](https://git-cliff.org) when a release is cut
with `make cut-release`.

## [0.1.1] 2026-11-09

### Bug fixes

- Current OpenAI and Claude models, SDK majors and request parameters for the provider adapters (#9)

### Documentation

- Standard README structure and language framing (#2)
- Horizontal layered architecture diagram
- Compact horizontal architecture diagram
- Recorded terminal demo of a real run, with its vhs tape (#1)
- Remove authorship statements from docs and scripts
- Recorded demos of more commands, with their vhs tapes (#2)
- Recorded demos of the HTTP service and more commands (#3)
- Describe the supply chain accurately (#4)
- Complete citation metadata and bump it on release (#6)
- Diagrams on white in the shared theme, make diagram for every diagram, and a self-contained Definition of Done (#8)

### Build and CI

- Run CodeQL on main and on a weekly schedule only
- Build and attach the sdist and wheel to every release (#10)

### Maintenance

- Add release automation, AGENTS.md, llms.txt and contributor docs
- Classify squash merges in the changelog by the commits they contain
- Latest toolchain and CI versions (#5)
- Release script keeps hard-coded version strings in step (#7)

## [0.1.0] 2026-11-02

### Features

- **core:** Add the ReAct reasoning-and-acting control loop
- **tools:** Add safe calculator, memory, and search tools
- **cli:** Add provider adapters, scripted model, and the CLI
- **tools:** Expand the tool library from 3 to 10
- **agent:** Add observability callbacks and a prompt-size budget
- **benchmark:** Add a task-success benchmark harness and suite
- **trace:** Add JSON trace export, logging callbacks, and CLI flags
- Add HTTP service, stress benchmark, and operations documentation
- Add production observability (metrics and readiness) and reword footer
- Adversarial tool-use hardening, tool retry, and a baseline benchmark (#1)

### Bug fixes

- Make agent parser and rule-policy regexes linear time
- Use linear line-scanning patterns in the ReAct parser
- Remove overlapping whitespace quantifier in the calculator pattern
- Extract calculator questions with linear string operations
- Harden calculator and make trace round-trip lossless (#19)

### Documentation

- Write README, architecture diagram, and responsible-AI cards
- Document the expanded tools, benchmark, and trace features
- Add agent benchmark and a performance section
- Use plain, factual wording (#18)

### Maintenance

- Scaffold react-agent from standards template
- Let the formatter collapse the subparser call
- **deps:** Bump github/codeql-action from 3 to 4
- **deps:** Bump actions/upload-artifact from 4 to 7
- **deps:** Bump astral-sh/setup-uv from 4 to 7
- **ci:** Bump GitHub Actions to current major versions
- Remove Dependabot configuration
