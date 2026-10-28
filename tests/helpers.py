"""Shared test fixtures: a scripted model and simple tools."""

from __future__ import annotations

from collections.abc import Sequence

from react_agent.core import FunctionTool, ToolRegistry


class ScriptedModel:
    """A language model that replays a fixed list of completions in order.

    This makes the agent's control loop fully deterministic and testable offline: each
    call to :meth:`complete` returns the next scripted completion, so a whole multi-step
    ReAct interaction can be specified up front.
    """

    def __init__(self, completions: Sequence[str], *, name: str = "scripted") -> None:
        self._completions = list(completions)
        self._index = 0
        self.name = name
        self.prompts: list[str] = []

    def complete(self, prompt: str, *, stop: Sequence[str] | None = None) -> str:
        self.prompts.append(prompt)
        if self._index >= len(self._completions):
            raise AssertionError("ScriptedModel ran out of completions")
        completion = self._completions[self._index]
        self._index += 1
        return completion


def echo_tool() -> FunctionTool:
    return FunctionTool(name="echo", description="Echo the input.", function=lambda text: text)


def upper_tool() -> FunctionTool:
    return FunctionTool(
        name="upper",
        description="Uppercase the input.",
        function=lambda text: text.upper(),
    )


def simple_registry() -> ToolRegistry:
    return ToolRegistry([echo_tool(), upper_tool()])
