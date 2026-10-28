"""Tests for prompt construction."""

from __future__ import annotations

from react_agent.core.prompt import build_prompt, build_system_prompt

from .helpers import simple_registry


def test_system_prompt_lists_tools_and_format() -> None:
    prompt = build_system_prompt(simple_registry())
    assert "echo" in prompt and "upper" in prompt
    assert "Thought:" in prompt
    assert "Final Answer:" in prompt


def test_system_prompt_handles_no_tools() -> None:
    from react_agent.core import ToolRegistry

    prompt = build_system_prompt(ToolRegistry())
    assert "no tools available" in prompt


def test_build_prompt_includes_question_and_scratchpad() -> None:
    prompt = build_prompt("What is 2+2?", simple_registry(), "Thought: t\nObservation: 4")
    assert "Question: What is 2+2?" in prompt
    assert "Observation: 4" in prompt
    assert prompt.endswith("\n")


def test_build_prompt_without_scratchpad() -> None:
    prompt = build_prompt("Q?", simple_registry(), "")
    assert "Question: Q?" in prompt
