<h1 align="center">ReAct Agent</h1>

<p align="center">
  <em>A reasoning-and-acting agent built from scratch: tool use, a transparent control loop, and full step tracing.</em>
</p>

<p align="center">
  <a href="https://github.com/adeoluo/react-agent/actions/workflows/ci.yml"><img alt="Continuous integration" src="https://github.com/adeoluo/react-agent/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Coverage" src="https://img.shields.io/badge/coverage-93%25-brightgreen">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%20%7C%203.12-blue">
  <img alt="Type checked" src="https://img.shields.io/badge/mypy-strict-blue">
  <img alt="Runtime dependencies" src="https://img.shields.io/badge/runtime%20deps-0-brightgreen">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

---

## Motivation

Agent frameworks hide the one thing worth understanding: the control loop that turns a
language model into something that *acts*. This project implements the ReAct pattern
(interleaved **Rea**soning and **Act**ing) from first principles, with **zero runtime
dependencies**, so the mechanism is fully visible - how a prompt is built, how the model's
output is parsed into an action, how a tool is executed, and how the observation feeds the
next step.

Two properties make it principle-level rather than a toy: every run is a **fully auditable
trace**, and the loop **recovers** from malformed output, unknown tools, and tool failures
by turning each into feedback the model can act on, instead of crashing.

## Architecture

<p align="center">
  <img src="docs/architecture/architecture.svg" alt="System architecture" width="860">
</p>

The **Agent** builds a **prompt** from the question, the tool descriptions, and the running
scratchpad; the **language model** returns a Thought plus an Action; the **parser** turns
that text into a structured decision; the chosen **tool** runs and its observation is
appended; the loop repeats until a Final Answer or a step limit. Tools, the model, and the
registry are all injected, so a deterministic scripted model and a frontier API are
interchangeable. See the [architecture decision records](docs/adr/) for key choices.

## Demonstration

Fully offline, via `python -m react_agent demonstrate`:

```text
Question: What is the capital of France, and what is 21 times 2?
Thought: I should look up the capital of France.
Action: search
Action Input: capital of France
Observation: Paris is the capital and most populous city of France.
Thought: Now I compute 21 times 2.
Action: calculator
Action Input: 21 * 2
Observation: 42
Final Answer: The capital of France is Paris, and 21 times 2 is 42.
```

## Robustness

The control loop is tested against each failure mode it is designed to survive:

| Failure | How the loop recovers |
|---|---|
| Malformed model output | A `ParseError` becomes a formatting reminder observation |
| Unknown tool requested | The observation lists the valid tool names |
| A tool raises `ToolError` | The error message becomes the observation |
| No answer within budget | The run stops at `max_steps` and reports `finished = False` |

## Quickstart

```bash
git clone https://github.com/adeoluo/react-agent.git && cd react-agent
make setup                    # install dev tooling + pre-commit hooks
make all                      # lint + type-check + test

python -m react_agent tools   # list the built-in tools
python -m react_agent demonstrate    # run the offline scripted example
```

Use a frontier model by installing its optional extra and setting an API key:

```bash
uv sync --extra openai        # or: --extra anthropic
export OPENAI_API_KEY=...
python -m react_agent run "What is 17 * 23, and what is the capital of Japan?"
```

## Built-in tools

- **calculator** - evaluates arithmetic through an AST operator allow-list; never uses
  `eval`, so neither the model nor a prompt injection can execute arbitrary code.
- **search** - deterministic, offline lookup over a small bundled knowledge base.
- **memory** - a per-run key-value scratchpad (`set k = v` / `get k`).

## Design decisions

- **Structural `Protocol` typing** for `Tool` and `LanguageModel`: any object with the
  right shape is a first-class citizen, so stubs and APIs are interchangeable.
  ([ADR-0002](docs/adr/0002-protocol-interfaces.md))
- **Recover, do not crash.** Every failure becomes an observation, which both matches how
  capable agents behave and keeps runs debuggable.
  ([ADR-0003](docs/adr/0003-error-recovery-as-observation.md))
- **Zero runtime dependencies.** The agent is pure Python; provider SDKs are optional and
  lazily imported.

## Responsible AI

- **Model card:** [docs/MODEL_CARD.md](docs/MODEL_CARD.md)
- **Data card:** [docs/DATA_CARD.md](docs/DATA_CARD.md)
- **Threat model:** [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md)

## Limitations

- The bundled search tool is a small fixed knowledge base, not real retrieval.
- Single-agent and single-tool-per-step by design; planning, multiple agents, and
  parallel tool calls are out of scope (and are the subject of later portfolio projects).
- Provider-backed runs are only as reliable as the underlying model's adherence to the
  ReAct format; the parser is lenient but not magic.

## Roadmap

- [ ] Streaming token output for provider models
- [ ] Reflection step (self-critique) before the final answer
- [ ] A benchmark harness scoring task success over a suite of questions

## License

[MIT](LICENSE). Part of a 28-project artificial intelligence engineering portfolio by
[adeoluo](https://github.com/adeoluo).
