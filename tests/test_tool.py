"""Tests for the tool abstraction and registry."""

from __future__ import annotations

import pytest

from react_agent.core import FunctionTool, ToolRegistry


def test_function_tool_calls_wrapped_function() -> None:
    tool = FunctionTool(name="double", description="d", function=lambda s: s + s)
    assert tool("ab") == "abab"


def test_registry_add_and_get() -> None:
    tool = FunctionTool(name="echo", description="d", function=lambda s: s)
    registry = ToolRegistry([tool])
    assert "echo" in registry
    assert registry.get("echo") is tool
    assert registry.names == ["echo"]
    assert len(registry) == 1


def test_registry_rejects_duplicate_names() -> None:
    tool = FunctionTool(name="echo", description="d", function=lambda s: s)
    with pytest.raises(ValueError, match="Duplicate tool"):
        ToolRegistry([tool, tool])


def test_registry_unknown_tool_raises_with_suggestions() -> None:
    registry = ToolRegistry([FunctionTool(name="echo", description="d", function=lambda s: s)])
    with pytest.raises(KeyError, match="Unknown tool"):
        registry.get("missing")


def test_registry_preserves_insertion_order() -> None:
    a = FunctionTool(name="a", description="d", function=lambda s: s)
    b = FunctionTool(name="b", description="d", function=lambda s: s)
    registry = ToolRegistry([b, a])
    assert registry.names == ["b", "a"]
    assert [tool.name for tool in registry] == ["b", "a"]
