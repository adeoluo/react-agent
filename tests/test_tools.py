"""Tests for the built-in tools."""

from __future__ import annotations

import pytest

from react_agent.core import ReActAgent, ToolError
from react_agent.tools import CalculatorTool, MemoryTool, SearchTool, default_toolset

from .helpers import ScriptedModel


# --------------------------------------------------------------------------- #
# Calculator
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("2 + 2", "4"),
        ("2 * (3 + 4)", "14"),
        ("10 / 4", "2.5"),
        ("-5 + 3", "-2"),
        ("2 ** 10", "1024"),
        ("17 % 5", "2"),
    ],
)
def test_calculator_evaluates(expression: str, expected: str) -> None:
    assert CalculatorTool()(expression) == expected


def test_calculator_rejects_empty() -> None:
    with pytest.raises(ToolError, match="empty"):
        CalculatorTool()("")


def test_calculator_rejects_code_injection() -> None:
    with pytest.raises(ToolError):
        CalculatorTool()("__import__('os').system('echo hi')")


def test_calculator_reports_division_by_zero() -> None:
    with pytest.raises(ToolError, match="division by zero"):
        CalculatorTool()("1 / 0")


def test_calculator_preserves_integer_precision() -> None:
    # Regression: coercing operands to float rounded large integer products.
    assert CalculatorTool()("99999999 * 99999999") == "9999999800000001"


def test_calculator_overflow_becomes_tool_error() -> None:
    # Regression: OverflowError / non-finite results escaped and crashed the run.
    with pytest.raises(ToolError):
        CalculatorTool()("10.0 ** 1000")
    with pytest.raises(ToolError):
        CalculatorTool()("1e308 * 10")


# --------------------------------------------------------------------------- #
# Memory
# --------------------------------------------------------------------------- #
def test_memory_set_and_get() -> None:
    memory = MemoryTool()
    assert "stored" in memory("set city = Paris")
    assert memory("get city") == "Paris"


def test_memory_missing_key() -> None:
    assert "no value" in MemoryTool()("get unknown")


def test_memory_rejects_bad_commands() -> None:
    memory = MemoryTool()
    with pytest.raises(ToolError, match="expects"):
        memory("delete city")
    with pytest.raises(ToolError, match="requires"):
        memory("set = value")


def test_memory_store_is_isolated_copy() -> None:
    memory = MemoryTool()
    memory("set a = 1")
    snapshot = memory.store
    snapshot["a"] = "mutated"
    assert memory("get a") == "1"


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
def test_search_finds_relevant_fact() -> None:
    result = SearchTool()("what is the capital of France")
    assert "Paris" in result


def test_search_no_results_for_unknown() -> None:
    assert SearchTool()("quantum chromodynamics lagrangian") == "No results."


def test_search_empty_query() -> None:
    assert SearchTool()("") == "No results."


# --------------------------------------------------------------------------- #
# Default toolset + integration
# --------------------------------------------------------------------------- #
def test_default_toolset_has_all_tools() -> None:
    registry = default_toolset()
    assert set(registry.names) == {"calculator", "search", "memory"}


def test_default_toolset_memory_is_fresh_each_call() -> None:
    first = default_toolset()
    first.get("memory")("set x = 1")
    second = default_toolset()
    assert "no value" in second.get("memory")("get x")


def test_agent_uses_calculator_end_to_end() -> None:
    model = ScriptedModel(
        [
            "Thought: compute it\nAction: calculator\nAction Input: 6 * 7\n",
            "Thought: done\nFinal Answer: 42",
        ]
    )
    result = ReActAgent(model, default_toolset()).run("What is 6 times 7?")
    assert result.answer == "42"
    assert result.steps[0].observation == "42"
