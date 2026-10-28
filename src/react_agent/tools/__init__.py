"""Built-in tools and a default toolset.

The tools are deliberately safe and offline: a calculator that evaluates expressions
through an AST allow-list (never ``eval``), a per-run key-value memory, and a search tool
over a small bundled knowledge base. Together they are enough to demonstrate real
multi-step reasoning without any network access.
"""

from __future__ import annotations

from react_agent.core.tool import ToolRegistry
from react_agent.tools.calculator import CalculatorTool
from react_agent.tools.memory import MemoryTool
from react_agent.tools.search import SearchTool


def default_toolset() -> ToolRegistry:
    """Construct a registry with the calculator, memory, and search tools.

    A fresh :class:`MemoryTool` is created per call so runs do not share state.
    """
    return ToolRegistry([CalculatorTool(), SearchTool(), MemoryTool()])


__all__ = [
    "CalculatorTool",
    "MemoryTool",
    "SearchTool",
    "default_toolset",
]
