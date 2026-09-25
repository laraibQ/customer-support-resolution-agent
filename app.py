"""Streamlit UI for Meridian Support."""
from __future__ import annotations

import json

import streamlit as st

from meridian_support.agent import create_support_agent
from meridian_support.settings import load_settings
from meridian_support import store

DEMOS = [
    ("Track order", "Where is order MG-4412? My email is alex@example.com."),
    ("Returns window", "How many days do I have to return an unused item?"),
    ("Start return", "Open a return for MG-4425, email jordan@example.com, reason: wrong size."),
    ("Escalate", "My package arrived cracked. Please escalate to a human."),
]

STATUS = {
    "shipped": "Shipped",
    "processing": "Processing",
    "delivered": "Delivered",
    "cancelled": "Cancelled",
}


def _answer_text(content) -> str:
    if isinstance(content, list):
        return "".join(
            p.get("text", str(p)) if isinstance(p, dict) else str(p) for p in content
        )
    return str(content)


def _tool_trace(messages) -> list[dict]:
    steps: list[dict] = []
    for msg in messages:
        kind = getattr(msg, "type", None) or msg.__class__.__name__
        if kind in {"ai", "AIMessage"}:
            for call in getattr(msg, "tool_calls", None) or []:
                steps.append({"kind": "call", "name": call.get("name"), "args": call.get("args", {})})
        elif kind in {"tool", "ToolMessage"}:
            body = getattr(msg, "content", "")
            if isinstance(body, list):
                body = json.dumps(body)
            text = str(body)
            if len(text) > 480:
                text = text[:480] + "…"
            steps.append({"kind": "result", "name": getattr(msg, "name", "tool"), "content": text})
    return steps


def _styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, .stApp { font-family: "DM Sans", "Segoe UI", sans-serif !important; background:#F3F5F7 !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] > div:first-child { background:#12201C !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] h4 {
  color:#EAF3EF !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * { color:#A8D5C6 !important; opacity:1 !important; }
[data-testid="stSidebar"] .stButton > button {
  background:#1B6B5A !important; color:#fff !important; border:1px solid #2A8F78 !important; font-weight:600 !important;
}
.hero {
  background: linear-gradient(135deg,#12201C 0%,#1B6B5A 72%,#247A68 100%);
  border-radius:18px; padding:1.4rem 1.5rem 1.25rem; margin:0.2rem 0 1rem 0;
}
.hero-kicker { color:#B7E0D2 !important; font-size:0.72rem !important; letter-spacing:0.14em; text-transform:uppercase; font-weight:700 !important; margin:0 0 0.35rem 0 !important; }
.hero-title { color:#FFFFFF !important; font-size:1.75rem !important; margin:0 0 0.4rem 0 !important; font-weight:700 !important; }
.hero-sub { color:#E4F2EC !important; margin:0 !important; max-width:44rem; font-size:0.95rem !important; line-height:1.5 !important; }
.hero-chips { margin-top:0.9rem; display:flex; flex-wrap:wrap; gap:0.4rem; }
.hero-chip { color:#fff !important; border:1px solid rgba(255,255,255,0.35); background:rgba(255,255,255,0.14); border-radius:999px; padding:0.22rem 0.7rem; font-size:0.75rem; font-weight:600; }
.pill { display:inline-block; background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.16); color:#D7EFE6 !important; border-radius:8px; padding:0.35rem 0.55rem; font-size:0.8rem; font-family:ui-monospace,Consolas,monospace; margin:0.15rem 0 0.55rem 0; }
[data-testid="stMain"] .stButton > button {
  background:#fff !important; color:#12201C !important; border:1px solid #C5D0CA !important; border-radius:11px !important; font-weight:600 !important;
}
div[data-testid="stChatMessage"] { background:#fff !important; border:1px solid #D5DEE6 !important; border-radius:14px !important; }
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] p { color:#3F524B !important; opacity:1 !important; }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def _agent():
    return create_support_agent(debug=False)


st.set_page_config(page_title="Meridian Support", page_icon="M", layout="wide")
_styles()

try:
    settings = load_settings()
    runtime = f"{settings.provider} · {settings.chat_model}"
except Exception as exc:  # noqa: BLE001
    st.error(f"Config error: {exc}")
    st.info("Copy env.example to .env and set GROQ_API_KEY.")
    st.stop()

orders = store.list_orders()
tickets = store.list_tickets()
returns = store.list_returns()

with st.sidebar:
    st.markdown("### Meridian Supply")
    st.caption("Support console")
    st.markdown("**Runtime**")
    st.markdown(f'<div class="pill">{runtime}</div>', unsafe_allow_html=True)
    st.markdown("**Retrieval**")
    st.markdown(f'<div class="pill">{settings.retrieval}</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("#### Sample orders")
    for oid, order in orders.items():
        st.markdown(f"**{oid}** — {STATUS.get(order['status'], order['status'])}")
        st.caption(order["customer_email"].replace("@", "＠"))
    st.divider()
    st.markdown("#### Tickets")
    if not tickets:
        st.caption("None yet.")
    else:
        for t in tickets[-6:]:
            st.markdown(f"**{t['ticket_id']}** · {t['priority']}")
            st.caption(t["summary"])
    st.markdown("#### Returns")
    if not returns:
        st.caption("None yet.")
    else:
        for r in returns[-6:]:
            st.markdown(f"**{r['return_id']}** · {r['order_id']}")
            st.caption(r["status"])
    st.divider()
    if st.button("Reset conversation", use_container_width=True):
        for key in ("messages", "history", "trace", "pending"):
            st.session_state.pop(key, None)
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "trace" not in st.session_state:
    st.session_state.trace = []

st.markdown(
    f"""
<div class="hero">
  <p class="hero-kicker" style="color:#B7E0D2!important;">Customer support</p>
  <p class="hero-title" style="color:#FFFFFF!important;">Meridian Supply Support</p>
  <p class="hero-sub" style="color:#E4F2EC!important;">
    Resolution agent with policy retrieval, email-gated order lookup, return
    intake, and human escalation.
  </p>
  <div class="hero-chips">
    <span class="hero-chip" style="color:#fff!important;">LangChain tools</span>
    <span class="hero-chip" style="color:#fff!important;">TF-IDF RAG</span>
    <span class="hero-chip" style="color:#fff!important;">Escalation</span>
    <span class="hero-chip" style="color:#fff!important;">{runtime}</span>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
c1.metric("Orders", len(orders))
c2.metric("Tickets", len(tickets))
c3.metric("Returns", len(returns))

st.subheader("Try a scenario")
cols = st.columns(4)
for col, (label, text) in zip(cols, DEMOS):
    with col:
        if st.button(label, key=f"d_{label}", use_container_width=True):
            st.session_state.pending = text

left, right = st.columns([1.55, 1.0], gap="large")

with left:
    st.subheader("Conversation")
    st.caption("Ask about shipping, returns, warranty, or a sample order.")
    if not st.session_state.messages:
        st.info("Try a scenario button, or ask about MG-4412 with alex@example.com.")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.session_state.pop("pending", None) or st.chat_input("Message Meridian Support…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Working…"):
                try:
                    result = _agent().invoke(
                        {"messages": st.session_state.history + [("human", prompt)]}
                    )
                    answer = _answer_text(result["messages"][-1].content)
                    st.session_state.trace = _tool_trace(result["messages"])
                except Exception as exc:  # noqa: BLE001
                    answer = f"Error: `{exc}`"
                    st.error(answer)
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.history.extend([("human", prompt), ("ai", answer)])
        st.rerun()

with right:
    st.subheader("Tool activity")
    st.caption("Last-turn tool calls.")
    if not st.session_state.trace:
        st.write("No activity yet.")
    else:
        for i, step in enumerate(st.session_state.trace, 1):
            if step["kind"] == "call":
                with st.expander(f"{i}. `{step['name']}`", expanded=True):
                    st.json(step["args"])
            else:
                with st.expander(f"{i}. result `{step['name']}`", expanded=False):
                    st.code(step["content"], language="json")
    with st.container(border=True):
        st.markdown("**Capabilities**")
        st.markdown(
            "- Policy retrieval\n"
            "- Email-verified order lookup\n"
            "- Return creation\n"
            "- Human ticket escalation"
        )

st.caption("Meridian Supply support — sample data only. API keys stay in local .env.")
