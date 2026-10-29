# Operations Guide - ReAct Agent

The operational contract of the agent service.

## Running the service

```bash
uv run python -m react_agent serve --host 0.0.0.0 --port 8000
```

A standard-library HTTP server with **zero runtime dependencies**. It runs the agent with
the offline, deterministic rule-policy model and the full toolset, so it is reproducible
and needs no provider credentials.

## Endpoints

| Method | Path | Body | Success |
|---|---|---|---|
| GET | `/health` | none | status, tool names, model name |
| POST | `/run` | `{"question", "max_steps"?}` | answer, finished, full trace |

Errors return JSON `{"error": ...}` with a 4xx status. `max_steps` is bounded so a request
cannot loop unboundedly.

## Service level objectives

Measured by `benchmarks/stress.py` on a developer laptop:

| Objective | Target | Observed (single worker) |
|---|---|---|
| Run latency p50 | < 1 ms | about 0.03 ms |
| Run latency p99 | < 1 ms | about 0.09 ms |
| Throughput | > 10000 runs/second/core | about 31000 runs/second |
| Benchmark success rate | 1.00 | 1.00 (6/6) |

Observed with the deterministic rule-policy model. A real provider model would dominate
latency and cost; the loop structure and bounds are unchanged.

## Operational constraints

- **The step budget bounds every request.** `max_steps` caps the number of tool calls, so a
  run cannot loop forever; the service caps it at 12.
- **With a real provider model, latency and cost are dominated by model calls, not the
  loop.** Each step is one model call; budget accordingly and cache where possible.
- **The loop is CPU bound with the offline model and holds the global interpreter lock.**
  Scale with processes for the offline model; for a provider model, concurrency is bound by
  provider rate limits.
- **Tools are the trust boundary.** Built-in tools are pure and side-effect-free; any added
  tool must validate its input and must not execute untrusted content.
- **No persistence, no authentication.** Front the service with a gateway.

## Failure modes and responses

| Symptom | Likely cause | Response |
|---|---|---|
| `finished: false` | Step budget hit before an answer | Raise `max_steps`, or inspect the trace for a loop |
| `400` on run | Empty question or bad `max_steps` | Inspect the `error` field |
| Provider errors (CLI `run`) | Missing credentials or rate limits | Use the offline model, or back off |

## Capacity planning

With the offline model, a single core serves tens of thousands of runs per second. With a
provider model, provision for the provider's rate limit and latency, not local CPU.
