# Scaling and Design Tradeoffs - ReAct Agent

How the reference design grows, and the tradeoffs taken.

## Reference architecture (today)

A single process runs the reason-act loop with a pluggable language model and a tool
registry, served over a standard-library HTTP service. The service uses the offline
rule-policy model; the CLI can use provider models.

## Scaling path

| Stage | Bottleneck | Change |
|---|---|---|
| Offline model, one process | CPU, global interpreter lock | One replica per core |
| Provider model | Model latency and rate limits | Concurrency bound by the provider; batch and cache |
| Many tools | Tool latency | Run slow tools asynchronously; cache deterministic tools |
| Repeated questions | Re-running the same loop | Cache by (question, max_steps, model) |
| Long traces | Step budget and context growth | Tune `max_steps`; summarize intermediate observations |

With the offline model the service is shared-nothing and throughput is linear in replicas.
With a provider model the binding constraint moves to the provider.

## Substantial tradeoffs

- **Offline rule-policy model vs a provider model.** The offline model makes runs
  deterministic, free, and reproducible, at the cost of generality; a provider model
  generalizes but adds latency, cost, nondeterminism, and credentials. The model is a single
  interface, so either drops in; the service chooses the offline model deliberately.
- **Explicit reason-act loop vs a single call.** The loop enables tool use and an auditable
  trace at the cost of multiple model calls per answer. A single call is cheaper but cannot
  act or show its work.
- **Step budget vs open-ended reasoning.** A bounded budget guarantees termination and a
  predictable cost envelope at the risk of stopping before an answer; the budget is
  per-request so callers trade recall for cost.
- **Pure tools vs powerful tools.** Keeping tools pure and validated makes the trust boundary
  tight at the cost of capability; a tool that touches the world would widen the boundary and
  demand more validation.

## What would change under real load

Cache by request key, run process-per-core replicas for the offline model, and, for a
provider model, add batching, caching, and rate-limit-aware concurrency behind the model
interface. The loop, the tools, and the trace are unchanged.
