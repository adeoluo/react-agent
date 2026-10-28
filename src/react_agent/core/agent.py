"""The ReAct control loop.

The agent interleaves reasoning and acting: it asks the model for a Thought and an Action,
executes the chosen tool, feeds the resulting Observation back, and repeats until the model
produces a Final Answer or a step budget is exhausted.

Robustness is a first-class concern. The loop recovers from three failure modes by turning
each into an observation the model can learn from, rather than crashing:

1. **Malformed output** - a parse error becomes a formatting reminder.
2. **Unknown tool** - an invalid tool name becomes a list of valid tools.
3. **Tool failure** - a :class:`ToolError` becomes the error message.

Every step is recorded, so a run is a fully auditable trace.
"""

from __future__ import annotations

from react_agent.core.llm import LanguageModel
from react_agent.core.parser import ParseError, parse_output
from react_agent.core.prompt import build_prompt
from react_agent.core.steps import AgentAction, AgentFinish, AgentResult, TraceStep
from react_agent.core.tool import ToolError, ToolRegistry

_STOP = ("\nObservation:", "Observation:")


class ReActAgent:
    """An agent that reasons and acts over a fixed tool set."""

    def __init__(
        self,
        model: LanguageModel,
        tools: ToolRegistry,
        *,
        max_steps: int = 6,
    ) -> None:
        """Create an agent.

        Args:
            model: The language model used for reasoning.
            tools: The tools the agent may call.
            max_steps: Maximum number of action steps before giving up.
        """
        if max_steps < 1:
            raise ValueError("max_steps must be at least 1")
        self._model = model
        self._tools = tools
        self._max_steps = max_steps

    def run(self, question: str) -> AgentResult:
        """Answer ``question`` by interleaving reasoning and tool use."""
        steps: list[TraceStep] = []
        scratchpad = ""

        for _ in range(self._max_steps):
            prompt = build_prompt(question, self._tools, scratchpad)
            completion = self._model.complete(prompt, stop=_STOP)
            step_text = completion if "Thought:" in completion else f"Thought:{completion}"

            try:
                decision = parse_output(step_text)
            except ParseError as error:
                scratchpad = _append(
                    scratchpad,
                    step_text,
                    f"Error: {error} Respond using the required format.",
                )
                continue

            if isinstance(decision, AgentFinish):
                return AgentResult(
                    question=question,
                    answer=decision.answer,
                    steps=tuple(steps),
                    finished=True,
                    model_name=self._model.name,
                )

            observation = self._act(decision)
            steps.append(TraceStep(action=decision, observation=observation))
            scratchpad = _append_step(scratchpad, decision, observation)

        return AgentResult(
            question=question,
            answer="",
            steps=tuple(steps),
            finished=False,
            model_name=self._model.name,
        )

    def _act(self, action: AgentAction) -> str:
        """Execute a tool, converting failures into recoverable observations."""
        if action.tool not in self._tools:
            return (
                f"Error: unknown tool {action.tool!r}. Valid tools: {', '.join(self._tools.names)}."
            )
        tool = self._tools.get(action.tool)
        try:
            return tool(action.tool_input)
        except ToolError as error:
            return f"Error: {error}"


def _append_step(scratchpad: str, action: AgentAction, observation: str) -> str:
    block = (
        f"Thought: {action.thought}\n"
        f"Action: {action.tool}\n"
        f"Action Input: {action.tool_input}\n"
        f"Observation: {observation}"
    )
    return f"{scratchpad}\n{block}".lstrip("\n")


def _append(scratchpad: str, step_text: str, observation: str) -> str:
    block = f"{step_text.strip()}\nObservation: {observation}"
    return f"{scratchpad}\n{block}".lstrip("\n")
