# End-to-End Case Study - A Tool-Using Agent Run

How the agent answers a question by reasoning and acting, and why the trace matters.

## Scenario

> "What is 2 * (3 + 4)?"

The answer requires computation, not recall. The agent must decide to use a tool, call it
with the right input, read the result, and stop.

## Trace

```bash
curl -s -X POST localhost:8000/run -d '{"question": "What is 2 * (3 + 4)?"}'
```

The response contains the final answer and the full ReAct trace: each thought, the tool and
input chosen, and the observation returned. For the arithmetic suite the agent reaches the
answer in a single tool call, and the benchmark passes 6 of 6 tasks (`python -m react_agent
benchmark`).

## Why the trace matters

- **Auditability.** Every answer is accompanied by the exact sequence of decisions that
  produced it, so a reviewer can see why the agent did what it did.
- **Debuggability.** When a run fails (`finished: false`), the trace shows where the loop
  stalled, which tool misfired, or whether the step budget was too small.
- **Determinism.** With the rule-policy model the same question always produces the same
  trace, so regressions are caught by exact comparison.

## What an operator sees

- **Bounded cost.** `max_steps` caps tool calls per request; with a provider model this caps
  the number of model calls and therefore spend.
- **A clear trust boundary.** Tools are where the agent touches the world; each is pure and
  validated, so a malformed question cannot cause a side effect.
- **A swap seam.** The same loop runs against a provider model by changing one argument; the
  service uses the offline model for reproducibility.

## Takeaway

Structuring the agent as an explicit reason-act loop with a typed trace turns an opaque
answer into an auditable, bounded, debuggable process, which is what makes an agent
operable in production.
