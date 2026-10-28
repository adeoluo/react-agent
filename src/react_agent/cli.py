"""Command-line interface for the ReAct agent.

Three subcommands:

- ``tools`` - list the built-in tools.
- ``demonstrate`` - run a scripted, fully offline example and print the reasoning trace.
- ``run``   - answer a question with a frontier provider model (requires an API key).

The CLI only wires together the agent, tools, and models; it contains no reasoning logic.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from react_agent import __version__
from react_agent.core import LanguageModel, ReActAgent
from react_agent.llms import AnthropicModel, OpenAIModel, ScriptedModel
from react_agent.tools import default_toolset

_DEMO_QUESTION = "What is the capital of France, and what is 21 times 2?"
_DEMO_SCRIPT = (
    "Thought: I should look up the capital of France.\n"
    "Action: search\nAction Input: capital of France\n",
    "Thought: Now I compute 21 times 2.\nAction: calculator\nAction Input: 21 * 2\n",
    "Thought: I have both answers.\n"
    "Final Answer: The capital of France is Paris, and 21 times 2 is 42.",
)
_PROVIDERS = {"openai": OpenAIModel, "anthropic": AnthropicModel}


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="react-agent",
        description="A ReAct reasoning-and-acting agent built from scratch.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tools_parser = subparsers.add_parser("tools", help="List the built-in tools.")
    tools_parser.set_defaults(handler=_handle_tools)

    demo_parser = subparsers.add_parser(
        "demonstrate", help="Run a scripted offline example."
    )
    demo_parser.set_defaults(handler=_handle_demo)

    run_parser = subparsers.add_parser("run", help="Answer a question with a provider model.")
    run_parser.add_argument("question", help="The question to answer.")
    run_parser.add_argument(
        "--provider",
        choices=sorted(_PROVIDERS),
        default="openai",
        help="Model provider to use.",
    )
    run_parser.add_argument("--model", default=None, help="Override the provider's model id.")
    run_parser.add_argument("--max-steps", type=int, default=6, help="Maximum action steps.")
    run_parser.set_defaults(handler=_handle_run)
    return parser


def _handle_tools(_: argparse.Namespace) -> int:
    for tool in default_toolset():
        print(f"- {tool.name}: {tool.description}")
    return 0


def _run_and_print(model: LanguageModel, question: str, *, max_steps: int) -> int:
    agent = ReActAgent(model, default_toolset(), max_steps=max_steps)
    result = agent.run(question)
    print(result.transcript())
    return 0 if result.finished else 1


def _handle_demo(_: argparse.Namespace) -> int:
    return _run_and_print(ScriptedModel(_DEMO_SCRIPT), _DEMO_QUESTION, max_steps=6)


def _handle_run(args: argparse.Namespace) -> int:
    provider_cls = _PROVIDERS[args.provider]
    model = provider_cls(model=args.model) if args.model else provider_cls()
    try:
        return _run_and_print(model, args.question, max_steps=args.max_steps)
    except ImportError as error:
        print(str(error), file=sys.stderr)
        return 2


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point; returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args.handler
    exit_code: int = handler(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
