"""Tests for the dependency-free HTTP agent service (pure handler layer)."""

from __future__ import annotations

from react_agent.service import AgentService, handle

_SERVICE = AgentService.build()


def test_health() -> None:
    status, payload = handle("GET", "/health", {}, _SERVICE)
    assert status == 200
    assert payload["status"] == "ok"
    assert "calculator" in payload["tools"]
    assert payload["model"] == "rule-policy"


def test_run_arithmetic() -> None:
    status, payload = handle("POST", "/run", {"question": "What is 21 * 2?"}, _SERVICE)
    assert status == 200
    assert payload["finished"] is True
    assert "42" in payload["answer"]
    assert payload["steps"]


def test_run_rejects_missing_question() -> None:
    status, payload = handle("POST", "/run", {}, _SERVICE)
    assert status == 400
    assert "question" in payload["error"]


def test_run_rejects_bad_max_steps() -> None:
    status, _ = handle("POST", "/run", {"question": "x", "max_steps": 0}, _SERVICE)
    assert status == 400
    status, _ = handle("POST", "/run", {"question": "x", "max_steps": 99}, _SERVICE)
    assert status == 400


def test_run_rejects_overlong_question() -> None:
    status, _ = handle("POST", "/run", {"question": "a" * 5000}, _SERVICE)
    assert status == 400


def test_unknown_route() -> None:
    status, payload = handle("GET", "/nope", {}, _SERVICE)
    assert status == 404
    assert "error" in payload
