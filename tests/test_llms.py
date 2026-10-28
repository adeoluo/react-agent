"""Tests for the scripted model and provider adapters."""

from __future__ import annotations

import pytest

from react_agent.llms import OpenAIModel, ScriptedModel, providers


def test_scripted_model_replays_in_order() -> None:
    model = ScriptedModel(["a", "b"], name="m")
    assert model.name == "m"
    assert model.complete("p1") == "a"
    assert model.complete("p2") == "b"


def test_scripted_model_requires_completions() -> None:
    with pytest.raises(ValueError, match="at least one"):
        ScriptedModel([])


def test_scripted_model_raises_when_exhausted() -> None:
    model = ScriptedModel(["only"])
    model.complete("p")
    with pytest.raises(RuntimeError, match="exhausted"):
        model.complete("p")


def test_provider_name() -> None:
    assert OpenAIModel(model="gpt-4o").name == "gpt-4o"


def test_require_raises_when_sdk_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(providers.importlib.util, "find_spec", lambda name: None)
    with pytest.raises(ImportError, match="uv sync --extra anthropic"):
        providers._require("anthropic", "anthropic")
