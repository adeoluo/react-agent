"""ReAct Agent - a reasoning-and-acting agent built from scratch.

Public API: the agent, its tool and language-model interfaces, and the structured
records that make every run an auditable trace.
"""

from __future__ import annotations

from react_agent.core import (
    AgentAction,
    AgentFinish,
    AgentResult,
    FunctionTool,
    LanguageModel,
    ParseError,
    ReActAgent,
    Tool,
    ToolError,
    ToolRegistry,
    TraceStep,
    parse_output,
)
from react_agent.llms import AnthropicModel, OpenAIModel, ScriptedModel

__version__ = "0.1.0"

__all__ = [
    "AgentAction",
    "AgentFinish",
    "AgentResult",
    "AnthropicModel",
    "FunctionTool",
    "LanguageModel",
    "OpenAIModel",
    "ParseError",
    "ReActAgent",
    "ScriptedModel",
    "Tool",
    "ToolError",
    "ToolRegistry",
    "TraceStep",
    "__version__",
    "parse_output",
]
