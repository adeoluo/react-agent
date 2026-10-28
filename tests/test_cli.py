"""Tests for the command-line interface."""

from __future__ import annotations

import pytest

from react_agent.cli import main


def test_tools_lists_builtin_tools(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["tools"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "calculator" in output
    assert "search" in output
    assert "memory" in output


def test_demo_runs_offline_and_finishes(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["demo"])
    output = capsys.readouterr().out
    assert exit_code == 0
    # The scripted demo uses search then calculator and answers with both facts.
    assert "Paris" in output
    assert "42" in output
    assert "Final Answer:" in output


def test_run_with_missing_sdk_exits_cleanly(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from react_agent.llms import providers

    monkeypatch.setattr(providers.importlib.util, "find_spec", lambda name: None)
    exit_code = main(["run", "hello", "--provider", "openai"])
    assert exit_code == 2
    assert "uv sync --extra openai" in capsys.readouterr().err


def test_missing_command_errors() -> None:
    with pytest.raises(SystemExit):
        main([])
