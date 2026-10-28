"""Optional adapters for frontier model providers.

Both adapters implement the :class:`~react_agent.core.llm.LanguageModel` protocol by
completing a prompt and honoring the ReAct stop sequences. They lazily import their SDK,
so the agent has no hard dependency on any provider: a missing SDK raises a clear,
actionable error rather than an opaque ``ImportError``.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from dataclasses import dataclass


def _require(package: str, extra: str) -> None:
    if importlib.util.find_spec(package) is None:
        raise ImportError(
            f"The {package!r} package is required for this model. "
            f"Install it with: uv sync --extra {extra}"
        )


@dataclass(frozen=True)
class OpenAIModel:
    """Chat-completion adapter for OpenAI models."""

    model: str = "gpt-4o-mini"
    temperature: float = 0.0

    @property
    def name(self) -> str:
        return self.model

    def complete(self, prompt: str, *, stop: Sequence[str] | None = None) -> str:
        _require("openai", "openai")
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            stop=list(stop) if stop else None,
        )
        return response.choices[0].message.content or ""


@dataclass(frozen=True)
class AnthropicModel:
    """Messages-API adapter for Anthropic Claude models."""

    model: str = "claude-3-5-sonnet-latest"
    temperature: float = 0.0
    max_tokens: int = 1024

    @property
    def name(self) -> str:
        return self.model

    def complete(self, prompt: str, *, stop: Sequence[str] | None = None) -> str:
        _require("anthropic", "anthropic")
        from anthropic import Anthropic

        client = Anthropic()
        response = client.messages.create(  # type: ignore[call-overload]
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stop_sequences=list(stop) if stop else [],
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [
            getattr(block, "text", "")
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]
        return "".join(parts)
