"""LangChain tools the Meridian Supply support agent can call."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

from ingest import load_index

ROOT = Path(__file__).parent
ORDERS_PATH = ROOT / "data" / "orders.json"
TICKETS_PATH = ROOT / "data" / "tickets.json"
RETURNS_PATH = ROOT / "data" / "returns.json"

_kb = None


def _get_kb():
    global _kb
    if _kb is None:
        _kb = load_index()
    return _kb


def _load_json(path: Path, default):
    if not path.exists():
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@tool
def lookup_order(order_id: str, customer_email: Optional[str] = None) -> str:
    """Look up an order by its ID (e.g. 'MS-20481').

    If `customer_email` is provided, the order is only returned when the
    email matches the order's customer — use this whenever the user has
    given their email so the agent does not leak another customer's data.
    Returns a JSON string with order status, items, totals, and tracking
    info, or an error message if the order is not found / mismatched.
    """
    orders = _load_json(ORDERS_PATH, {})
    order = orders.get(order_id.strip().upper())
    if not order:
        return json.dumps({"error": f"Order {order_id} not found."})
    if customer_email and customer_email.lower() != order["customer_email"].lower():
        return json.dumps(
            {
                "error": "Email does not match this order. Ask the customer "
                "to confirm the email used at checkout."
            }
        )
    return json.dumps({"order_id": order_id.upper(), **order}, indent=2)


@tool
def kb_search(query: str, k: int = 4) -> str:
    """Semantic search over FAQ, refund, shipping, and warranty docs.

    Use for any question about policies, process, timing, eligibility, or
    "how do I…" — anything not specific to a single order. Returns the
    top `k` most relevant passages with their source filenames.
    """
    kb = _get_kb()
    hits = kb.similarity_search(query, k=k)
    if not hits:
        return "No relevant passages found in the knowledge base."
    blocks = []
    for i, doc in enumerate(hits, 1):
        src = doc.metadata.get("source", "unknown")
        blocks.append(f"[{i}] ({src})\n{doc.page_content.strip()}")
    return "\n\n".join(blocks)


@tool
def refund_policy_search(query: str) -> str:
    """Shortcut search restricted to the refund / returns policy.

    Use when the customer's question is clearly about refunds, returns,
    return windows, refund timing, or non-returnable items.
    """
    kb = _get_kb()
    # FAISS metadata filter: keep only refund_policy.md chunks
    hits = [
        d
        for d in kb.similarity_search(query, k=8)
        if d.metadata.get("source") == "refund_policy.md"
    ][:4]
    if not hits:
        return "No relevant refund-policy passages found."
    return "\n\n".join(d.page_content.strip() for d in hits)


@tool
def start_return(
    order_id: str,
    customer_email: str,
    reason: str,
    item_sku: Optional[str] = None,
) -> str:
    """Open a return request for a delivered order.

    Eligible when the order status is `delivered`. Creates a return ID and
    prepaid-label placeholder. For damaged/wrong items that need photo
    review, prefer `create_ticket` instead.
    """
    orders = _load_json(ORDERS_PATH, {})
    oid = order_id.strip().upper()
    order = orders.get(oid)
    if not order:
        return json.dumps({"error": f"Order {oid} not found."})
    if customer_email.lower() != order["customer_email"].lower():
        return json.dumps({"error": "Email does not match this order."})
    if order.get("status") != "delivered":
        return json.dumps(
            {
                "error": (
                    f"Order {oid} is '{order.get('status')}'. Returns are only "
                    "available after delivery. If the package is damaged in "
                    "transit, escalate with create_ticket."
                )
            }
        )

    returns = _load_json(RETURNS_PATH, [])
    ret = {
        "return_id": f"RTN-{uuid.uuid4().hex[:8].upper()}",
        "order_id": oid,
        "customer_email": customer_email.strip().lower(),
        "item_sku": item_sku,
        "reason": reason.strip(),
        "status": "label_created",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label_url": f"https://returns.meridiansupply.example/labels/{oid}",
    }
    returns.append(ret)
    _save_json(RETURNS_PATH, returns)
    return json.dumps(
        {
            "return_id": ret["return_id"],
            "message": (
                f"Return {ret['return_id']} created for {oid}. "
                f"Print the prepaid label at {ret['label_url']} and drop "
                "off within 14 days."
            ),
        },
        indent=2,
    )


@tool
def create_ticket(
    summary: str,
    customer_email: str,
    priority: str = "normal",
    order_id: Optional[str] = None,
) -> str:
    """Create a human support ticket and escalate the conversation.

    Call this when the customer's request cannot be resolved with the
    available tools — for example: refund disputes, damaged items needing
    visual review, account access issues, anything requiring a human, or
    any question where the knowledge base does not contain a confident
    answer. `priority` must be one of: low, normal, high, urgent.
    """
    priority = priority.lower()
    if priority not in {"low", "normal", "high", "urgent"}:
        priority = "normal"

    ticket = {
        "ticket_id": f"TCK-{uuid.uuid4().hex[:8].upper()}",
        "summary": summary.strip(),
        "customer_email": customer_email.strip(),
        "order_id": order_id.strip().upper() if order_id else None,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    tickets = _load_json(TICKETS_PATH, [])
    tickets.append(ticket)
    _save_json(TICKETS_PATH, tickets)
    return json.dumps(
        {
            "ticket_id": ticket["ticket_id"],
            "message": (
                f"Ticket {ticket['ticket_id']} created with priority "
                f"{ticket['priority']}. A human agent will follow up at "
                f"{ticket['customer_email']}."
            ),
        }
    )


ALL_TOOLS = [
    lookup_order,
    kb_search,
    refund_policy_search,
    start_return,
    create_ticket,
]
