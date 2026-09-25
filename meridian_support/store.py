"""JSON-backed store for orders, tickets, and returns."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from meridian_support.settings import DATA_DIR

ORDERS_FILE = DATA_DIR / "orders.json"
TICKETS_FILE = DATA_DIR / "tickets.json"
RETURNS_FILE = DATA_DIR / "returns.json"


def _read(path: Path, default: Any) -> Any:
    if not path.exists():
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def get_order(order_id: str) -> dict | None:
    orders = _read(ORDERS_FILE, {})
    return orders.get(order_id.strip().upper())


def create_ticket(
    *,
    summary: str,
    customer_email: str,
    priority: str = "normal",
    order_id: str | None = None,
) -> dict:
    priority = priority.lower()
    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"
    ticket = {
        "ticket_id": f"MS-{uuid.uuid4().hex[:8].upper()}",
        "summary": summary.strip(),
        "customer_email": customer_email.strip(),
        "order_id": order_id.strip().upper() if order_id else None,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tickets = _read(TICKETS_FILE, [])
    tickets.append(ticket)
    _write(TICKETS_FILE, tickets)
    return ticket


def create_return(
    *,
    order_id: str,
    customer_email: str,
    reason: str,
    item_sku: str | None = None,
) -> dict:
    record = {
        "return_id": f"R-{uuid.uuid4().hex[:8].upper()}",
        "order_id": order_id.strip().upper(),
        "customer_email": customer_email.strip().lower(),
        "item_sku": item_sku,
        "reason": reason.strip(),
        "status": "label_ready",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label_url": f"https://returns.meridiansupply.example/l/{order_id.strip().upper()}",
    }
    returns = _read(RETURNS_FILE, [])
    returns.append(record)
    _write(RETURNS_FILE, returns)
    return record


def list_orders() -> dict:
    return _read(ORDERS_FILE, {})


def list_tickets() -> list:
    return _read(TICKETS_FILE, [])


def list_returns() -> list:
    return _read(RETURNS_FILE, [])
