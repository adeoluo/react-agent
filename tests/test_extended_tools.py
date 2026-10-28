"""Tests for the extended tool library."""

from __future__ import annotations

import pytest

from react_agent.core import ToolError
from react_agent.tools import (
    CountOccurrencesTool,
    DateDifferenceTool,
    KnowledgeBaseTool,
    TextLengthTool,
    TextTransformTool,
    UnitConversionTool,
    WeekdayTool,
    full_toolset,
)


# --------------------------------------------------------------------------- #
# Date and time
# --------------------------------------------------------------------------- #
def test_date_difference() -> None:
    assert DateDifferenceTool()("2026-01-01 to 2026-01-31") == "30"


def test_date_difference_negative() -> None:
    assert DateDifferenceTool()("2026-02-01 to 2026-01-01") == "-31"


def test_date_difference_bad_format() -> None:
    with pytest.raises(ToolError, match="expects"):
        DateDifferenceTool()("tomorrow")


def test_date_difference_invalid_date() -> None:
    with pytest.raises(ToolError, match="YYYY-MM-DD"):
        DateDifferenceTool()("2026-13-99 to 2026-01-01")


def test_weekday() -> None:
    assert WeekdayTool()("2026-01-01") == "Thursday"


# --------------------------------------------------------------------------- #
# Units
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("1000 m to km", "1"),
        ("1 km to m", "1000"),
        ("100 C to F", "212"),
        ("32 F to C", "0"),
        ("0 C to K", "273.15"),
        ("1 kg to g", "1000"),
    ],
)
def test_unit_conversion(query: str, expected: str) -> None:
    assert UnitConversionTool()(query) == expected


def test_unit_conversion_bad_input() -> None:
    with pytest.raises(ToolError, match="expects"):
        UnitConversionTool()("ten kilometers")


def test_unit_conversion_incompatible() -> None:
    with pytest.raises(ToolError, match="cannot convert"):
        UnitConversionTool()("1 km to kg")


# --------------------------------------------------------------------------- #
# Text
# --------------------------------------------------------------------------- #
def test_text_length() -> None:
    assert TextLengthTool()("hello world") == "11 characters, 2 words"


def test_text_transform_operations() -> None:
    tool = TextTransformTool()
    assert tool("reverse: abc") == "cba"
    assert tool("upper: abc") == "ABC"
    assert tool("lower: ABC") == "abc"
    assert tool("title: hello world") == "Hello World"


def test_text_transform_unknown_op() -> None:
    with pytest.raises(ToolError, match="unknown operation"):
        TextTransformTool()("rotate: abc")


def test_count_occurrences() -> None:
    assert CountOccurrencesTool()("a in banana") == "3"


def test_count_occurrences_bad_format() -> None:
    with pytest.raises(ToolError, match="expects"):
        CountOccurrencesTool()("banana")


# --------------------------------------------------------------------------- #
# Knowledge base
# --------------------------------------------------------------------------- #
def test_knowledge_base_lookup() -> None:
    tool = KnowledgeBaseTool()
    assert tool("capital of France") == "Paris"
    assert tool("continent of Japan") == "Asia"


def test_knowledge_base_unknown_entity() -> None:
    assert "No entry" in KnowledgeBaseTool()("capital of Atlantis")


def test_knowledge_base_unknown_attribute() -> None:
    assert "No attribute" in KnowledgeBaseTool()("anthem of France")


def test_knowledge_base_bad_format() -> None:
    with pytest.raises(ToolError, match="expects"):
        KnowledgeBaseTool()("France capital")


# --------------------------------------------------------------------------- #
# Full toolset
# --------------------------------------------------------------------------- #
def test_full_toolset_has_ten_tools() -> None:
    registry = full_toolset()
    assert len(registry) == 10
    assert "convert_units" in registry
    assert "knowledge_base" in registry
