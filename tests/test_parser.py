"""Tests for parsing ReAct model output."""

from __future__ import annotations

import pytest

from react_agent.core import AgentAction, AgentFinish, ParseError, parse_output


def test_parse_action() -> None:
    text = "Thought: I should compute this\nAction: calculator\nAction Input: 2 + 2\n"
    result = parse_output(text)
    assert isinstance(result, AgentAction)
    assert result.tool == "calculator"
    assert result.tool_input == "2 + 2"
    assert "compute" in result.thought


def test_parse_final_answer() -> None:
    text = "Thought: I now know the answer\nFinal Answer: 4"
    result = parse_output(text)
    assert isinstance(result, AgentFinish)
    assert result.answer == "4"


def test_final_answer_takes_precedence_over_action_text() -> None:
    text = "Thought: done\nFinal Answer: the Action is complete"
    result = parse_output(text)
    assert isinstance(result, AgentFinish)


def test_parse_is_lenient_about_label_case() -> None:
    text = "thought: ok\naction: echo\naction input: hi\n"
    result = parse_output(text)
    assert isinstance(result, AgentAction)
    assert result.tool == "echo"


def test_parse_multiline_action_input() -> None:
    text = "Thought: t\nAction: run\nAction Input: line one\nline two\nObservation:"
    result = parse_output(text)
    assert isinstance(result, AgentAction)
    assert result.tool_input == "line one\nline two"


def test_parse_error_on_garbage() -> None:
    with pytest.raises(ParseError, match="Expected an 'Action:'"):
        parse_output("I have no idea what to do here.")


def test_parse_action_without_input_is_error() -> None:
    with pytest.raises(ParseError):
        parse_output("Thought: t\nAction: echo\n")
