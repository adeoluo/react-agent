"""Tests for the benchmark harness, suite, and rule-policy model."""

from __future__ import annotations

from react_agent.benchmark import (
    BenchmarkReport,
    BenchmarkTask,
    TaskOutcome,
    contains,
    equals,
    run_benchmark,
)
from react_agent.core import ReActAgent
from react_agent.llms import RulePolicyModel
from react_agent.suite import SUITE
from react_agent.tools import full_toolset


def test_contains_judge() -> None:
    judge = contains("Paris")
    assert judge("The capital is paris.")
    assert not judge("The capital is London.")


def test_equals_judge() -> None:
    judge = equals("42")
    assert judge("  42 ")
    assert not judge("forty-two")


def test_run_benchmark_full_suite_passes() -> None:
    agent = ReActAgent(RulePolicyModel(), full_toolset(), max_steps=4)
    report = run_benchmark(agent, SUITE)
    assert report.total == len(SUITE)
    assert report.success_rate == 1.0
    assert report.mean_steps >= 1.0


def test_report_tracks_failures() -> None:
    tasks = [BenchmarkTask(name="impossible", question="What is XYZ?", judge=contains("never"))]
    agent = ReActAgent(RulePolicyModel(), full_toolset(), max_steps=3)
    report = run_benchmark(agent, tasks)
    assert report.passed == 0
    assert report.success_rate == 0.0


def test_report_summary_format() -> None:
    report = BenchmarkReport(
        outcomes=(
            TaskOutcome(task_name="a", passed=True, finished=True, steps=1, answer="x"),
            TaskOutcome(task_name="b", passed=False, finished=True, steps=2, answer="y"),
        )
    )
    summary = report.summary()
    assert "1/2 passed" in summary
    assert "[PASS] a" in summary
    assert "[FAIL] b" in summary


def test_empty_report() -> None:
    report = BenchmarkReport()
    assert report.success_rate == 0.0
    assert report.mean_steps == 0.0


def test_rule_policy_handles_unknown() -> None:
    model = RulePolicyModel()
    out = model.complete("Question: explain quantum gravity\nThought:")
    assert "Final Answer" in out
