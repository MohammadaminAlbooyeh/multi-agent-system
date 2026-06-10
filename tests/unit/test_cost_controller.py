"""Unit tests for the CostController."""

from __future__ import annotations

import pytest

from mares.llm.cost_controller import CostController, TokenBudgetExceeded


def test_record_tracks_usage():
    cc = CostController(per_agent_budgets={"planner_agent": 100}, global_budget=1000)
    cc.record("planner_agent", 30, 20)
    snap = cc.snapshot()
    assert snap["per_agent_used"]["planner_agent"] == 50
    assert snap["global_used"] == 50


def test_per_agent_budget_exceeded():
    cc = CostController(per_agent_budgets={"planner_agent": 10})
    with pytest.raises(TokenBudgetExceeded):
        cc.record("planner_agent", 100, 0)


def test_global_budget_exceeded():
    cc = CostController(per_agent_budgets={"a": 1000}, global_budget=10)
    with pytest.raises(TokenBudgetExceeded):
        cc.record("a", 20, 0)


def test_estimate_is_pessimistic():
    cc = CostController()
    assert cc.estimate("a", "x" * 400) == 100


def test_from_env_reads_defaults(monkeypatch):
    monkeypatch.setenv("TOKEN_BUDGET_PLANNER", "1234")
    monkeypatch.setenv("TOKEN_BUDGET_GLOBAL", "99999")
    cc = CostController.from_env()
    assert cc.per_agent_budgets["planner_agent"] == 1234
    assert cc.global_budget == 99999
