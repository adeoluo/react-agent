# System Card - ReAct Agent

## Overview

- **What it is:** a from-scratch implementation of the ReAct (reason + act) agent loop. It
  prompts a language model to interleave reasoning with tool calls and returns an answer
  plus a full trace.
- **Reasoning model:** any object satisfying the `LanguageModel` protocol - a deterministic
  scripted model (offline), or the optional OpenAI / Anthropic adapters.
- **Version:** 0.1.0.

## Intended use

- **Primary use cases:** learning and demonstrating how an agent control loop works;
  prototyping tool-using agents; a teaching reference for ReAct.
- **Primary users:** engineers and researchers building or studying agents.

## Out-of-scope / prohibited use

- Not a production autonomous agent; it has no sandboxing beyond the safe built-in tools
  and no authorization model for side-effecting tools.
- Do not connect side-effecting or privileged tools without adding approval gates and
  sandboxing appropriate to your setting.

## Performance

The offline demo completes a two-tool task correctly and deterministically. There is no
accuracy benchmark yet; a task-success harness is on the roadmap. Robustness to malformed
output, unknown tools, and tool errors is covered by tests.

## Risks and limitations

- **Format adherence:** provider-backed runs depend on the model following the ReAct
  format; the parser is lenient but can still fail on very unusual output.
- **Tool safety:** only the bundled, safe tools are vetted. Any tool you add inherits your
  responsibility for safety.
- **No long-term memory across runs:** the memory tool is per-run by design.

## Safety mitigations

- The calculator evaluates an AST with an operator allow-list; `eval` is never used.
- Provider adapters are opt-in and lazily imported; nothing contacts the network by default.
- A step budget bounds worst-case cost and prevents infinite loops.

## Environmental / cost footprint

Offline runs use negligible CPU and no API calls. Provider-backed runs cost exactly the
tokens of the prompts and completions the loop generates, bounded by `max_steps`.
