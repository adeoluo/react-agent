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
    assert OpenAIModel(model="gpt-6.1-sol").name == "gpt-6.1-sol"


def test_require_raises_when_sdk_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(providers.importlib.util, "find_spec", lambda name: None)
    with pytest.raises(ImportError, match="uv sync --extra anthropic"):
        providers._require("anthropic", "anthropic")


class _Recorder:
    """Stands in for an SDK client and records the keyword arguments of each call."""

    def __init__(self, reply: object) -> None:
        self.calls: list[dict[str, object]] = []
        self.reply = reply

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return self.reply


def _fake_sdks(monkeypatch: pytest.MonkeyPatch) -> tuple[_Recorder, _Recorder]:
    import sys
    import types

    openai_reply = types.SimpleNamespace(
        choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="ok"))]
    )
    anthropic_reply = types.SimpleNamespace(
        content=[
            types.SimpleNamespace(type="thinking"),
            types.SimpleNamespace(type="text", text="ok"),
        ]
    )
    chat, messages = _Recorder(openai_reply), _Recorder(anthropic_reply)
    openai_mod = types.ModuleType("openai")
    openai_mod.OpenAI = lambda: types.SimpleNamespace(chat=types.SimpleNamespace(completions=chat))  # type: ignore[attr-defined]
    anthropic_mod = types.ModuleType("anthropic")
    anthropic_mod.Anthropic = lambda: types.SimpleNamespace(messages=messages)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", openai_mod)
    monkeypatch.setitem(sys.modules, "anthropic", anthropic_mod)
    monkeypatch.setattr(providers, "_require", lambda package, extra: None)
    return chat, messages


def test_openai_request_turns_reasoning_off_for_repeatable_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chat, _ = _fake_sdks(monkeypatch)
    model = providers.OpenAIModel()
    assert model.complete("p", stop=["Observation:"]) == "ok"
    sent = chat.calls[0]
    assert sent["model"] == "gpt-6-luna"
    assert sent["reasoning_effort"] == "none"
    assert sent["temperature"] == 0.0


def test_anthropic_request_sends_no_sampling_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    _, messages = _fake_sdks(monkeypatch)
    model = providers.AnthropicModel()
    assert model.complete("p", stop=["Observation:"]) == "ok"
    sent = messages.calls[0]
    assert sent["model"] == "claude-sonnet-5-5"
    assert sent["max_tokens"] == 2048
    assert not {"temperature", "top_p", "top_k"} & sent.keys()
