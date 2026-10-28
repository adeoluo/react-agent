"""Tests for the ReAct control loop, including failure recovery."""

from __future__ import annotations

import pytest

from react_agent.core import FunctionTool, ReActAgent, ToolError, ToolRegistry

from .helpers import ScriptedModel, simple_registry


def test_single_tool_call_then_finish() -> None:
    model = ScriptedModel(
        [
            "Thought: I will echo it\nAction: echo\nAction Input: hello\n",
            "Thought: done\nFinal Answer: hello",
        ]
    )
    result = ReActAgent(model, simple_registry()).run("say hello")
    assert result.finished
    assert result.answer == "hello"
    assert result.step_count == 1
    assert result.steps[0].observation == "hello"
    assert result.model_name == "scripted"


def test_multi_step_reasoning() -> None:
    model = ScriptedModel(
        [
            "Thought: echo first\nAction: echo\nAction Input: hi\n",
            "Thought: now shout\nAction: upper\nAction Input: hi\n",
            "Thought: done\nFinal Answer: HI",
        ]
    )
    result = ReActAgent(model, simple_registry()).run("shout hi")
    assert result.answer == "HI"
    assert result.step_count == 2
    assert result.steps[1].observation == "HI"


def test_recovers_from_unknown_tool() -> None:
    model = ScriptedModel(
        [
            "Thought: try foo\nAction: foo\nAction Input: x\n",
            "Thought: use echo\nAction: echo\nAction Input: y\n",
            "Thought: done\nFinal Answer: y",
        ]
    )
    result = ReActAgent(model, simple_registry()).run("q")
    assert result.answer == "y"
    assert "unknown tool" in result.steps[0].observation


def test_recovers_from_tool_error() -> None:
    def boom(_: str) -> str:
        raise ToolError("tool exploded")

    registry = ToolRegistry([FunctionTool(name="boom", description="d", function=boom)])
    model = ScriptedModel(
        [
            "Thought: try boom\nAction: boom\nAction Input: x\n",
            "Thought: give up gracefully\nFinal Answer: handled",
        ]
    )
    result = ReActAgent(model, registry).run("q")
    assert result.answer == "handled"
    assert "tool exploded" in result.steps[0].observation


def test_recovers_from_malformed_output() -> None:
    model = ScriptedModel(
        [
            "I have no idea what the format is",
            "Thought: ok now\nAction: echo\nAction Input: z\n",
            "Thought: done\nFinal Answer: z",
        ]
    )
    result = ReActAgent(model, simple_registry()).run("q")
    assert result.answer == "z"
    # The malformed turn is not a tool step, so only the echo call is recorded.
    assert result.step_count == 1


def test_prepends_thought_when_model_omits_it() -> None:
    model = ScriptedModel([" I can answer now\nFinal Answer: 42"])
    result = ReActAgent(model, simple_registry()).run("q")
    assert result.finished
    assert result.answer == "42"


def test_stops_at_step_limit() -> None:
    model = ScriptedModel(
        [
            "Thought: loop\nAction: echo\nAction Input: a\n",
            "Thought: loop\nAction: echo\nAction Input: b\n",
        ]
    )
    result = ReActAgent(model, simple_registry(), max_steps=2).run("q")
    assert not result.finished
    assert result.answer == ""
    assert result.step_count == 2


def test_transcript_renders_steps() -> None:
    model = ScriptedModel(
        [
            "Thought: echo\nAction: echo\nAction Input: hi\n",
            "Thought: done\nFinal Answer: hi",
        ]
    )
    transcript = ReActAgent(model, simple_registry()).run("greet").transcript()
    assert "Question: greet" in transcript
    assert "Action: echo" in transcript
    assert "Final Answer: hi" in transcript


def test_rejects_invalid_max_steps() -> None:
    with pytest.raises(ValueError, match="max_steps"):
        ReActAgent(ScriptedModel([]), simple_registry(), max_steps=0)
