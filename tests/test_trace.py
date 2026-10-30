"""Tests for trace export and logging callbacks."""

from __future__ import annotations

from react_agent.core import ReActAgent
from react_agent.logging_callbacks import logging_callbacks
from react_agent.trace import trace_from_json, trace_to_dict, trace_to_json

from .helpers import ScriptedModel, simple_registry


def _run() -> object:
    model = ScriptedModel(
        [
            "Thought: echo it\nAction: echo\nAction Input: hi\n",
            "Thought: done\nFinal Answer: hi",
        ]
    )
    return ReActAgent(model, simple_registry()).run("greet")


def test_trace_to_dict_structure() -> None:
    payload = trace_to_dict(_run())  # type: ignore[arg-type]
    assert payload["question"] == "greet"
    assert payload["answer"] == "hi"
    assert payload["finished"] is True
    assert payload["steps"][0]["tool"] == "echo"


def test_trace_round_trips() -> None:
    original = _run()
    restored = trace_from_json(trace_to_json(original))  # type: ignore[arg-type]
    assert restored.question == original.question  # type: ignore[attr-defined]
    assert restored.answer == original.answer  # type: ignore[attr-defined]
    assert restored.step_count == original.step_count  # type: ignore[attr-defined]
    assert restored.steps[0].action.tool == "echo"


def test_trace_round_trip_preserves_raw_action() -> None:
    # Regression: AgentAction.raw was dropped on serialization, so a round trip
    # was not lossless as the module docstring claims.
    original = _run()
    restored = trace_from_json(trace_to_json(original))  # type: ignore[arg-type]
    assert restored.steps == original.steps  # type: ignore[attr-defined]
    for before, after in zip(original.steps, restored.steps, strict=True):  # type: ignore[attr-defined]
        assert after.action.raw == before.action.raw


def test_logging_callbacks_emit_lines() -> None:
    lines: list[str] = []
    callbacks = logging_callbacks(sink=lines.append)
    model = ScriptedModel(
        [
            "Thought: echo\nAction: echo\nAction Input: hi\n",
            "Thought: done\nFinal Answer: hi",
        ]
    )
    ReActAgent(model, simple_registry(), callbacks=callbacks).run("q")
    joined = "\n".join(lines)
    assert "action: echo" in joined
    assert "observation: hi" in joined
    assert "[finish] hi" in joined
