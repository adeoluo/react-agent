# ADR-0003: Treat failures as observations, not exceptions

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

During a run the agent encounters three recoverable failures: the model emits malformed
output, it names a tool that does not exist, or a tool raises an error. The naive approach
lets these propagate and crash the run.

## Decision

Catch each failure inside the control loop and convert it into an **observation** that is
fed back to the model on the next step:

- malformed output -> a reminder of the required format
- unknown tool -> the list of valid tool names
- `ToolError` -> the error message

The run only ends on a Final Answer or when the step budget is exhausted.

## Alternatives considered

- **Propagate exceptions.** Simplest to implement, but a single formatting slip aborts the
  whole run, which is brittle and hard to debug.
- **Silent retries with the same prompt.** Wastes steps because the model gets no new
  information about what went wrong.

## Consequences

- Runs are robust to the imperfect formatting real models produce.
- The failure and the model's recovery are both recorded in the trace, so debugging is
  straightforward.
- A malformed step still consumes part of the step budget, bounding worst-case cost.
