"""A micro-benchmark for agent throughput.

Measures how many full ReAct runs per second the agent completes over the offline
benchmark suite (with the deterministic rule-policy model and full toolset), and the raw
tool-call rate, so the README can quote numbers. Run with:

    uv run python benchmarks/benchmark.py
"""

from __future__ import annotations

import time

from react_agent.benchmark import run_benchmark
from react_agent.core import ReActAgent
from react_agent.llms import RulePolicyModel
from react_agent.suite import SUITE
from react_agent.tools import CalculatorTool, full_toolset


def _bench_runs(repeats: int) -> float:
    agent = ReActAgent(RulePolicyModel(), full_toolset(), max_steps=4)
    start = time.perf_counter()
    for _ in range(repeats):
        run_benchmark(agent, SUITE)
    elapsed = time.perf_counter() - start
    total_runs = repeats * len(SUITE)
    return total_runs / elapsed if elapsed > 0 else float("inf")


def _bench_tool(repeats: int) -> float:
    tool = CalculatorTool()
    start = time.perf_counter()
    for _ in range(repeats):
        tool("2 * (3 + 4) - 5")
    elapsed = time.perf_counter() - start
    return repeats / elapsed if elapsed > 0 else float("inf")


def main() -> None:
    runs_per_sec = _bench_runs(2_000)
    tools_per_sec = _bench_tool(100_000)
    print("ReAct Agent micro-benchmark\n")
    print(f"  full agent runs (suite) : {runs_per_sec:>12,.0f} runs/sec")
    print(f"  calculator tool calls   : {tools_per_sec:>12,.0f} calls/sec")


if __name__ == "__main__":
    main()
