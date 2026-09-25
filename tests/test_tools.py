"""Unit tests for order, return, and escalation tools."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from meridian_support import store, tools

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    tickets = tmp_path / "tickets.json"
    returns = tmp_path / "returns.json"
    tickets.write_text("[]", encoding="utf-8")
    returns.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(store, "TICKETS_FILE", tickets)
    monkeypatch.setattr(store, "RETURNS_FILE", returns)
    monkeypatch.setattr(store, "ORDERS_FILE", DATA / "orders.json")


def test_order_ok():
    raw = tools.get_order_details.invoke(
        {"order_id": "MG-4412", "customer_email": "alex@example.com"}
    )
    data = json.loads(raw)
    assert data["order_id"] == "MG-4412"
    assert data["status"] == "shipped"


def test_order_email_gate():
    raw = tools.get_order_details.invoke(
        {"order_id": "MG-4412", "customer_email": "nope@example.com"}
    )
    assert "error" in json.loads(raw)


def test_return_blocked_if_not_delivered():
    raw = tools.open_return_request.invoke(
        {
            "order_id": "MG-4412",
            "customer_email": "alex@example.com",
            "reason": "changed mind",
        }
    )
    err = json.loads(raw)["error"].lower()
    assert "after delivery" in err


def test_return_delivered():
    raw = tools.open_return_request.invoke(
        {
            "order_id": "MG-4425",
            "customer_email": "jordan@example.com",
            "reason": "wrong size",
        }
    )
    data = json.loads(raw)
    assert data["return_id"].startswith("R-")


def test_escalate():
    raw = tools.escalate_to_human.invoke(
        {
            "summary": "Cracked bottle needs photos",
            "customer_email": "alex@example.com",
            "priority": "high",
            "order_id": "MG-4412",
        }
    )
    data = json.loads(raw)
    assert data["ticket_id"].startswith("MS-")
