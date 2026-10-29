"""A production-style stress benchmark for the agent service.

Drives the full run handler (the ReAct loop with the deterministic rule-policy
model and the full toolset) under sustained, concurrent load over the benchmark
questions and reports throughput with p50, p95, and p99 latency. Deterministic
and offline; run with:

    uv run python benchmarks/stress.py
"""

from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from react_agent.service import AgentService, handle
from react_agent.suite import SUITE


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main() -> None:
    service = AgentService.build()
    questions = [task.question for task in SUITE]
    requests = [{"question": questions[index % len(questions)]} for index in range(1500)]

    def one(body: dict[str, str]) -> float:
        start = time.perf_counter()
        handle("POST", "/run", body, service)
        return (time.perf_counter() - start) * 1000

    print(f"Suite questions: {len(questions)} | Requests: {len(requests)}")
    for workers in (1, 4, 8):
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            latencies = list(pool.map(one, requests))
        wall = time.perf_counter() - start
        print(
            f"workers={workers:<2}  "
            f"throughput={len(requests) / wall:>7.0f} req/s  "
            f"p50={statistics.median(latencies):>6.3f} ms  "
            f"p95={_percentile(latencies, 0.95):>6.3f} ms  "
            f"p99={_percentile(latencies, 0.99):>6.3f} ms"
        )


if __name__ == "__main__":
    main()
