"""A large-workload scale benchmark for the ReAct agent loop.

Where ``benchmark.py`` reports peak throughput on a cached suite, this script asks
how the agent behaves as the *batch* of tasks grows: it runs the deterministic
rule-policy agent (full toolset) over progressively larger synthetic suites of
arithmetic tasks and reports wall-clock time, run throughput, peak memory (via the
stdlib ``tracemalloc``), and the task success rate.

The headline is a scaling *shape*: the ReAct control loop is O(1) work per task,
so throughput stays roughly flat as the batch grows, while peak memory rises
linearly with the retained per-task traces and answers. Success stays at 100%
because the rule policy solves every generated task.

The data is synthetic and the loop is from-scratch pure Python with an offline
deterministic model: these numbers measure the harness overhead, not a frontier
model's latency, and are not a comparison against a hosted agent framework. The
point is to show how this implementation scales, honestly.

Run with:

    uv run python benchmarks/scale.py
"""

from __future__ import annotations

import random
import time
import tracemalloc
from dataclasses import dataclass

from react_agent.benchmark import BenchmarkReport, BenchmarkTask, contains, run_benchmark
from react_agent.core import ReActAgent
from react_agent.llms import RulePolicyModel
from react_agent.tools import full_toolset

_BATCH_SIZES: tuple[int, ...] = (1000, 2000, 4000, 8000)


def build_suite(num_tasks: int, *, seed: int = 0) -> list[BenchmarkTask]:
    """Build ``num_tasks`` arithmetic tasks the rule policy can solve with the calculator."""
    rng = random.Random(seed)
    tasks: list[BenchmarkTask] = []
    for index in range(num_tasks):
        left = rng.randint(2, 99)
        right = rng.randint(2, 99)
        tasks.append(
            BenchmarkTask(
                name=f"mul-{index}",
                question=f"What is {left} * {right}?",
                judge=contains(str(left * right)),
                tags=("calculator",),
            )
        )
    return tasks


def _new_agent() -> ReActAgent:
    return ReActAgent(RulePolicyModel(), full_toolset(), max_steps=4)


@dataclass(frozen=True, slots=True)
class ScaleResult:
    """One row of the scale table."""

    tasks: int
    seconds: float
    runs_per_sec: float
    peak_mib: float
    success_rate: float


def measure(num_tasks: int) -> ScaleResult:
    """Run the agent over ``num_tasks`` tasks, timing and memory measured separately.

    Timing and throughput are measured without ``tracemalloc`` (whose per-allocation
    hook would otherwise understate throughput); peak memory is then captured in a
    separate ``tracemalloc`` pass over the same batch.
    """
    suite = build_suite(num_tasks)

    start = time.perf_counter()
    report: BenchmarkReport = run_benchmark(_new_agent(), suite)
    elapsed = time.perf_counter() - start

    peak = _peak_memory(suite)

    return ScaleResult(
        tasks=num_tasks,
        seconds=elapsed,
        runs_per_sec=num_tasks / elapsed if elapsed else 0.0,
        peak_mib=peak / (1024 * 1024),
        success_rate=report.success_rate,
    )


def _peak_memory(suite: list[BenchmarkTask]) -> int:
    """Return the peak bytes to run the batch and retain every task outcome."""
    tracemalloc.start()
    run_benchmark(_new_agent(), suite)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def main() -> None:
    print("Synthetic tasks; from-scratch pure-Python ReAct loop with an offline model.")
    print("Measures harness overhead, not a frontier model's latency or a hosted framework.\n")
    header = f"{'runs':>8}{'seconds':>10}{'runs/sec':>12}{'peak MiB':>11}{'success':>10}"
    print(header)
    print("-" * len(header))
    for num_tasks in _BATCH_SIZES:
        result = measure(num_tasks)
        print(
            f"{result.tasks:>8}{result.seconds:>10.3f}{result.runs_per_sec:>12.0f}"
            f"{result.peak_mib:>11.1f}{result.success_rate:>10.2f}"
        )


if __name__ == "__main__":
    main()
