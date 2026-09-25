"""Streamlit chat UI for the Meridian Supply support agent."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agent import build_agent
from config import get_settings

ROOT = Path(__file__).parent
ORDERS_PATH = ROOT / "data" / "orders.json"
TICKETS_PATH = ROOT / "data" / "tickets.json"
RETURNS_PATH = ROOT / "data" / "returns.json"


def _load_list(path: Path) -> list:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _extract_tool_trace(messages) -> list[dict]:
    """Pull tool name + args/content from LangChain message history."""
    trace: list[dict] = []
    for msg in messages:
        msg_type = getattr(msg, "type", None) or msg.__class__.__name__
        if msg_type in {"ai", "AIMessage"}:
            for call in getattr(msg, "tool_calls", None) or []:
                trace.append(
                    {
                        "kind": "call",
                        "name": call.get("name", "unknown"),
                        "args": call.get("args", {}),
                    }
                )
        elif msg_type in {"tool", "ToolMessage"}:
            content = getattr(msg, "content", "")
            if isinstance(content, list):
                content = json.dumps(content)
            preview = str(content)
            if len(preview) > 400:
                preview = preview[:400] + "…"
            trace.append(
                {
                    "kind": "result",
                    "name": getattr(msg, "name", "tool"),
                    "content": preview,
                }
            )
    return trace


st.set_page_config(page_title="Meridian Supply Support", page_icon="🛟", layout="wide")
st.title("Meridian Supply — Support Resolution Agent")
st.caption("LangChain tool-calling · RAG (FAISS) · human escalation · dual LLM provider")

try:
    settings = get_settings()
    provider_label = f"{settings.provider} / {settings.chat_model}"
except Exception as exc:  # noqa: BLE001 — show setup errors in UI
    st.error(f"Config error: {exc}")
    st.stop()

with st.sidebar:
    st.header("Runtime")
    st.markdown(f"**Provider:** `{provider_label}`")

    st.divider()
    st.header("Demo data")
    st.subheader("Sample orders")
    orders = json.loads(ORDERS_PATH.read_text(encoding="utf-8"))
    for oid, o in orders.items():
        st.markdown(f"**{oid}** — {o['status']} — `{o['customer_email']}`")

    st.divider()
    st.subheader("Tickets")
    tickets = _load_list(TICKETS_PATH)
    if not tickets:
        st.caption("No tickets yet.")
    else:
        for t in tickets[-10:]:
            st.markdown(
                f"- **{t['ticket_id']}** ({t['priority']}) — {t['summary']}"
            )

    st.subheader("Returns")
    returns = _load_list(RETURNS_PATH)
    if not returns:
        st.caption("No returns yet.")
    else:
        for r in returns[-10:]:
            st.markdown(
                f"- **{r['return_id']}** — {r['order_id']} — {r['status']}"
            )

    if st.button("Reset conversation"):
        st.session_state.pop("messages", None)
        st.session_state.pop("history", None)
        st.session_state.pop("last_trace", None)
        st.rerun()

if "agent" not in st.session_state:
    st.session_state.agent = build_agent(verbose=False)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "last_trace" not in st.session_state:
    st.session_state.last_trace = []

col_chat, col_trace = st.columns([1.4, 1.0])

with col_chat:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask about an order, refund, shipping, warranty…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Resolving…"):
                turn_messages = st.session_state.history + [("human", prompt)]
                result = st.session_state.agent.invoke({"messages": turn_messages})
                answer = result["messages"][-1].content
                if isinstance(answer, list):
                    answer = "".join(
                        part.get("text", str(part)) if isinstance(part, dict) else str(part)
                        for part in answer
                    )
                st.markdown(answer)
                st.session_state.last_trace = _extract_tool_trace(result["messages"])

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.history.extend([("human", prompt), ("ai", answer)])
        st.rerun()

with col_trace:
    st.subheader("Tool trace (last turn)")
    if not st.session_state.last_trace:
        st.caption("Send a message to see which tools the agent called.")
    else:
        for step in st.session_state.last_trace:
            if step["kind"] == "call":
                with st.expander(f"→ {step['name']}", expanded=True):
                    st.json(step["args"])
            else:
                with st.expander(f"← {step['name']} result", expanded=False):
                    st.code(step["content"], language="json")

    st.divider()
    st.markdown("**Try these**")
    st.code(
        "Where is MS-20481? Email alex@example.com\n"
        "What's your refund window?\n"
        "My package arrived broken — escalate please\n"
        "Start a return for MS-20483, email jordan@example.com, wrong size",
        language="text",
    )
