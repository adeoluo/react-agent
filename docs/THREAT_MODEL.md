# Threat Model - ReAct Agent

## Assets

- The host system and its resources (the agent executes tools).
- Any API keys supplied for provider adapters.
- Integrity of the agent's answers and trace.

## Trust boundaries

- **The question and all model output are untrusted text.** Model output selects a tool
  and its input, so it must never be able to escalate beyond the registered tools.
- **Provider adapters** are the only components that cross the network boundary.

## Threats and mitigations

| Threat | Vector | Impact | Mitigation |
|---|---|---|---|
| Arbitrary code execution | Model asks the calculator to evaluate code | Host compromise | Calculator parses an AST with an operator allow-list; `eval` is never used |
| Prompt injection via tool output | A tool returns text that steers later reasoning | Hijacked behavior | Tools are safe and read-only; observations are data, and the model can only ever select a registered tool |
| Unbounded loops / cost | Model never emits a Final Answer | Resource / token blowup | Hard `max_steps` budget; malformed steps also consume the budget |
| Unknown or side-effecting tool | Model names a tool that is not registered | Unexpected action | Unknown tools are rejected and reported; only explicitly registered tools can run |
| Secret leakage | API keys in logs or traces | Credential compromise | Keys read from environment only; never logged; `.env` is git-ignored |
| Supply-chain compromise | Malicious dependency | Code execution | Zero runtime dependencies; provider SDKs are optional; Dependabot and CodeQL in CI |

## Residual risk

If a user registers a side-effecting or privileged tool, the model's output can trigger it.
Such tools must add their own authorization, sandboxing, and approval gates; the framework
provides the step budget and the unknown-tool guard but cannot vet arbitrary user tools.
