"""LangChain tools for the Meridian support agent."""
from __future__ import annotations

import json
from typing import Optional

from langchain_core.tools import tool

from meridian_support import kb, store


def _passages_to_text(passages: list[kb.Passage]) -> str:
    if not passages:
        return "No matching policy text was found."
    blocks = []
    for i, p in enumerate(passages, 1):
        blocks.append(f"[{i}] ({p.source})\n{p.text.strip()}")
    return "\n\n".join(blocks)


@tool
def get_order_details(order_id: str, customer_email: Optional[str] = None) -> str:
    """Fetch an order by ID (example: MG-4412).

    When the shopper provides an email, require an exact match so another
    customer's order is never revealed.
    """
    order = store.get_order(order_id)
    oid = order_id.strip().upper()
    if not order:
        return json.dumps({"error": f"No order found for {oid}."})
    if customer_email and customer_email.lower() != order["customer_email"].lower():
        return json.dumps(
            {
                "error": "That email does not match this order. Ask the shopper "
                "to confirm the checkout email."
            }
        )
    return json.dumps({"order_id": oid, **order}, indent=2)


@tool
def search_policies(query: str, limit: int = 4) -> str:
    """Search FAQ and policy docs for shipping, payments, warranty, and accounts."""
    return _passages_to_text(kb.search(query, k=limit))


@tool
def search_returns_policy(query: str) -> str:
    """Search only the returns & refunds policy."""
    hits = kb.search(query, k=4, source="returns.md")
    if not hits:
        return "No returns-policy passages matched."
    return "\n\n".join(p.text.strip() for p in hits)


@tool
def open_return_request(
    order_id: str,
    customer_email: str,
    reason: str,
    item_sku: Optional[str] = None,
) -> str:
    """Open a return for a delivered order and issue a prepaid label link."""
    order = store.get_order(order_id)
    oid = order_id.strip().upper()
    if not order:
        return json.dumps({"error": f"No order found for {oid}."})
    if customer_email.lower() != order["customer_email"].lower():
        return json.dumps({"error": "Email does not match this order."})
    if order.get("status") != "delivered":
        return json.dumps(
            {
                "error": (
                    f"Order {oid} is '{order.get('status')}'. Returns open only "
                    "after delivery. For transit damage, escalate to a human ticket."
                )
            }
        )
    record = store.create_return(
        order_id=oid,
        customer_email=customer_email,
        reason=reason,
        item_sku=item_sku,
    )
    return json.dumps(
        {
            "return_id": record["return_id"],
            "message": (
                f"Return {record['return_id']} is ready. Print the label at "
                f"{record['label_url']} and drop off within 14 days."
            ),
        },
        indent=2,
    )


@tool
def escalate_to_human(
    summary: str,
    customer_email: str,
    priority: str = "normal",
    order_id: Optional[str] = None,
) -> str:
    """Create a human support ticket when tools cannot finish the request."""
    ticket = store.create_ticket(
        summary=summary,
        customer_email=customer_email,
        priority=priority,
        order_id=order_id,
    )
    return json.dumps(
        {
            "ticket_id": ticket["ticket_id"],
            "message": (
                f"Ticket {ticket['ticket_id']} opened ({ticket['priority']}). "
                f"A teammate will email {ticket['customer_email']}."
            ),
        }
    )


TOOLSET = [
    get_order_details,
    search_policies,
    search_returns_policy,
    open_return_request,
    escalate_to_human,
]
