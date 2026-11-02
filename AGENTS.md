# AGENTS.md

Working notes for coding agents and contributors in **ReAct Agent**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

A reasoning-and-acting agent built from scratch: tool use, a transparent control loop, and full step tracing.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/react_agent/__init__.py`: ReAct Agent - a reasoning-and-acting agent built from scratch.
- `src/react_agent/benchmark.py`: A benchmark harness for measuring agent task success.
- `src/react_agent/cli.py`: Command-line interface for the ReAct agent.
- `src/react_agent/core/__init__.py`: Core abstractions for the ReAct agent.
- `src/react_agent/core/agent.py`: The ReAct control loop.
- `src/react_agent/core/callbacks.py`: Observability hooks for an agent run.
- `src/react_agent/core/llm.py`: The language model interface the agent reasons with.
- `src/react_agent/core/parser.py`: Parsing the model's ReAct output into a structured decision.
- `src/react_agent/core/prompt.py`: Constructing the ReAct prompt from the task, tools, and running scratchpad.
- `src/react_agent/core/steps.py`: Typed records for the agent's reasoning trace.
- `src/react_agent/core/tool.py`: Tools: the actions a ReAct agent can take in the world.
- `src/react_agent/llms/__init__.py`: Language models: offline scripted model and optional provider adapters.
- `src/react_agent/llms/providers.py`: Optional adapters for frontier model providers.
- `src/react_agent/llms/rule_policy.py`: A deterministic rule-based policy model for offline benchmarking.
- `src/react_agent/llms/scripted.py`: A scripted language model for offline demonstrations and tests.
- `src/react_agent/logging_callbacks.py`: A logging-callbacks factory.
- `src/react_agent/observability.py`: In-process request metrics for the HTTP service.
- `src/react_agent/service.py`: A standard-library HTTP service exposing the ReAct agent.
- `src/react_agent/suite.py`: A small built-in benchmark suite for the agent.
- `src/react_agent/tools/__init__.py`: Built-in tools and ready-made toolsets.
- `src/react_agent/tools/calculator.py`: A safe arithmetic calculator tool.
- `src/react_agent/tools/datetime_tools.py`: Date and time tools.
- `src/react_agent/tools/knowledge_base.py`: A structured knowledge-base tool with exact-key lookup.
- `src/react_agent/tools/memory.py`: A simple scratch-memory tool the agent can write to and read from.
- `src/react_agent/tools/search.py`: A deterministic, offline search tool over a small bundled knowledge base.
- `src/react_agent/tools/text.py`: String utility tools.
- `src/react_agent/tools/units.py`: Unit conversion tool.
- `src/react_agent/trace.py`: Serializing an agent run to JSON and back.

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
