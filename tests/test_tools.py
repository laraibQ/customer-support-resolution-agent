"""Unit tests for support tools (no LLM / API key required)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(autouse=True)
def _isolate_side_effect_files(tmp_path, monkeypatch):
    """Point tickets/returns at temp files so tests do not dirty demo data."""
    tickets = tmp_path / "tickets.json"
    returns = tmp_path / "returns.json"
    tickets.write_text("[]", encoding="utf-8")
    returns.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(tools, "TICKETS_PATH", tickets)
    monkeypatch.setattr(tools, "RETURNS_PATH", returns)
    # Keep orders on real sample DB
    monkeypatch.setattr(tools, "ORDERS_PATH", DATA / "orders.json")


def test_lookup_order_success():
    raw = tools.lookup_order.invoke(
        {"order_id": "MS-20481", "customer_email": "alex@example.com"}
    )
    payload = json.loads(raw)
    assert payload["order_id"] == "MS-20481"
    assert payload["status"] == "shipped"
    assert "tracking" in payload


def test_lookup_order_email_mismatch():
    raw = tools.lookup_order.invoke(
        {"order_id": "MS-20481", "customer_email": "wrong@example.com"}
    )
    payload = json.loads(raw)
    assert "error" in payload
    assert "Email does not match" in payload["error"]


def test_lookup_order_not_found():
    raw = tools.lookup_order.invoke({"order_id": "MS-00000"})
    payload = json.loads(raw)
    assert "error" in payload


def test_start_return_requires_delivered():
    raw = tools.start_return.invoke(
        {
            "order_id": "MS-20481",
            "customer_email": "alex@example.com",
            "reason": "changed mind",
        }
    )
    payload = json.loads(raw)
    assert "error" in payload
    assert "after delivery" in payload["error"].lower()


def test_start_return_delivered_ok():
    raw = tools.start_return.invoke(
        {
            "order_id": "MS-20483",
            "customer_email": "jordan@example.com",
            "reason": "wrong size",
        }
    )
    payload = json.loads(raw)
    assert "return_id" in payload
    assert payload["return_id"].startswith("RTN-")


def test_create_ticket():
    raw = tools.create_ticket.invoke(
        {
            "summary": "Broken package needs review",
            "customer_email": "alex@example.com",
            "priority": "high",
            "order_id": "MS-20481",
        }
    )
    payload = json.loads(raw)
    assert payload["ticket_id"].startswith("TCK-")
    assert "follow up" in payload["message"].lower()
