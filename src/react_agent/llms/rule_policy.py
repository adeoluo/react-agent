"""A deterministic rule-based policy model for offline benchmarking.

To report a real agent success rate without a network, we need a model that actually
drives the ReAct loop to correct answers on the benchmark suite. :class:`RulePolicyModel`
inspects the running prompt and emits the next ReAct step: it recognizes a handful of
question shapes (arithmetic, capital-of, unit conversion), issues the right tool call, and
then reads the observation to produce a final answer.

It is intentionally narrow and transparent - a stand-in for a capable model that keeps the
benchmark deterministic and offline. A frontier model would replace it unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

_CALC = re.compile(r"what is[ \t]+([^?]+?)[ \t]*\?", re.IGNORECASE)
_CAPITAL = re.compile(r"capital of[ \t]+([A-Za-z]+)", re.IGNORECASE)
_CONVERT = re.compile(r"convert[ \t]+([^?\n]+)", re.IGNORECASE)
_LAST_OBSERVATION = re.compile(r"Observation:[ \t]*([^\n]*)")


@dataclass
class RulePolicyModel:
    """Emits ReAct steps by pattern-matching the question and reading observations."""

    name: str = "rule-policy"

    def complete(self, prompt: str, *, stop: Sequence[str] | None = None) -> str:
        question = _extract_question(prompt)
        observations = _LAST_OBSERVATION.findall(prompt)

        # If a tool has already produced an observation, finish with it.
        if observations:
            return f"Thought: I have the result.\nFinal Answer: {observations[-1].strip()}"

        calc = _CALC.search(question)
        if calc and any(ch.isdigit() for ch in calc.group(1)):
            return (
                "Thought: I will calculate this.\n"
                f"Action: calculator\nAction Input: {calc.group(1).strip()}\n"
            )

        capital = _CAPITAL.search(question)
        if capital:
            return (
                "Thought: I will look this up.\n"
                f"Action: knowledge_base\nAction Input: capital of {capital.group(1)}\n"
            )

        convert = _CONVERT.search(question)
        if convert:
            return (
                "Thought: I will convert the units.\n"
                f"Action: convert_units\nAction Input: {convert.group(1).strip()}\n"
            )

        return "Thought: I am not sure.\nFinal Answer: unknown"


def _extract_question(prompt: str) -> str:
    for line in prompt.splitlines():
        if line.startswith("Question:"):
            return line.split(":", 1)[1].strip()
    return ""
