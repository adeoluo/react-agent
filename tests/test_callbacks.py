"""Tests for agent callbacks and the prompt-size budget."""

from __future__ import annotations

from react_agent.core import Callbacks, ReActAgent
from react_agent.core.steps import AgentAction, AgentFinish

from .helpers import ScriptedModel, simple_registry


def _run_with(model: ScriptedModel, callbacks: Callbacks, **kwargs: object) -> object:
    return ReActAgent(model, simple_registry(), callbacks=callbacks, **kwargs).run("q")  # type: ignore[arg-type]


def test_callbacks_fire_in_order() -> None:
    events: list[str] = []
    callbacks = Callbacks(
        on_step=lambda i: events.append(f"step{i}"),
        on_action=lambda i, a: events.append(f"action:{a.tool}"),
        on_observation=lambda i, o: events.append(f"obs:{o}"),
        on_finish=lambda f: events.append("finish"),
    )
    model = ScriptedModel(
        [
            "Thought: echo\nAction: echo\nAction Input: hi\n",
            "Thought: done\nFinal Answer: hi",
        ]
    )
    _run_with(model, callbacks)
    assert events == ["step1", "action:echo", "obs:hi", "step2", "finish"]


def test_action_callback_receives_action() -> None:
    captured: list[AgentAction] = []
    callbacks = Callbacks(on_action=lambda i, a: captured.append(a))
    model = ScriptedModel(
        [
            "Thought: t\nAction: upper\nAction Input: hi\n",
            "Thought: done\nFinal Answer: HI",
        ]
    )
    _run_with(model, callbacks)
    assert captured[0].tool == "upper"


def test_finish_callback_receives_finish() -> None:
    captured: list[AgentFinish] = []
    callbacks = Callbacks(on_finish=lambda f: captured.append(f))
    model = ScriptedModel(["Thought: done\nFinal Answer: 42"])
    _run_with(model, callbacks)
    assert captured[0].answer == "42"


def test_default_callbacks_are_noops() -> None:
    model = ScriptedModel(["Thought: done\nFinal Answer: ok"])
    result = ReActAgent(model, simple_registry()).run("q")
    assert result.answer == "ok"


def test_prompt_budget_stops_run() -> None:
    model = ScriptedModel(
        [
            "Thought: loop\nAction: echo\nAction Input: aaaaaaaaaa\n",
            "Thought: loop\nAction: echo\nAction Input: bbbbbbbbbb\n",
            "Thought: done\nFinal Answer: never reached",
        ]
    )
    # A tiny budget forces an early stop before the first completion.
    result = ReActAgent(model, simple_registry(), max_prompt_chars=10).run("q")
    assert not result.finished


def test_budget_validates() -> None:
    import pytest

    with pytest.raises(ValueError, match="max_prompt_chars"):
        ReActAgent(ScriptedModel(["x"]), simple_registry(), max_prompt_chars=0)
