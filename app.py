"""Professional Streamlit UI for Meridian Supply support agent."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from config import get_settings

ROOT = Path(__file__).parent
ORDERS_PATH = ROOT / "data" / "orders.json"
TICKETS_PATH = ROOT / "data" / "tickets.json"
RETURNS_PATH = ROOT / "data" / "returns.json"

STATUS_LABEL = {
    "shipped": "Shipped",
    "processing": "Processing",
    "delivered": "Delivered",
    "cancelled": "Cancelled",
}

DEMO_PROMPTS = [
    ("Track order", "Where is order MS-20481? My email is alex@example.com."),
    ("Refund policy", "What's your refund window for unused items?"),
    ("Start a return", "Start a return for MS-20483, email jordan@example.com, reason: wrong size."),
    ("Escalate issue", "My package arrived broken. Please escalate this to a human."),
]


def _load_list(path: Path) -> list:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _normalize_answer(answer) -> str:
    if isinstance(answer, list):
        return "".join(
            part.get("text", str(part)) if isinstance(part, dict) else str(part)
            for part in answer
        )
    return str(answer)


def _extract_tool_trace(messages) -> list[dict]:
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
            if len(preview) > 500:
                preview = preview[:500] + "…"
            trace.append(
                {
                    "kind": "result",
                    "name": getattr(msg, "name", "tool"),
                    "content": preview,
                }
            )
    return trace


def _get_agent():
    """Cached agent — avoid rebuilding the LLM client every turn."""

    @st.cache_resource(show_spinner=False)
    def _cached_agent():
        from agent import build_agent

        return build_agent(verbose=False)

    return _cached_agent()


def _inject_styles() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, .stApp {
  font-family: "DM Sans", "Segoe UI", sans-serif !important;
  background: #F3F5F7 !important;
}

[data-testid="stHeader"] { background: transparent !important; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] > div:first-child {
  background: #12201C !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
  color: #EAF3EF !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
  color: #A8D5C6 !important;
  opacity: 1 !important;
}
/* Email auto-links were dark blue on dark bg — force readable */
[data-testid="stSidebar"] a {
  color: #9FD5C4 !important;
  text-decoration: none !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: #1B6B5A !important;
  color: #FFFFFF !important;
  border: 1px solid #2A8F78 !important;
  font-weight: 600 !important;
}

/* ---- Hero: inline colors beat Streamlit theme overrides ---- */
.hero {
  background: linear-gradient(135deg, #12201C 0%, #1B6B5A 72%, #247A68 100%) !important;
  border-radius: 18px;
  padding: 1.45rem 1.55rem 1.3rem;
  margin: 0.2rem 0 1rem 0;
  border: 1px solid rgba(255,255,255,0.08);
}
.hero-kicker {
  color: #B7E0D2 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 700 !important;
  margin: 0 0 0.4rem 0 !important;
}
.hero-title {
  color: #FFFFFF !important;
  font-size: 1.75rem !important;
  line-height: 1.2 !important;
  margin: 0 0 0.45rem 0 !important;
  font-weight: 700 !important;
}
.hero-sub {
  color: #E4F2EC !important;
  margin: 0 !important;
  max-width: 44rem;
  font-size: 0.95rem !important;
  line-height: 1.5 !important;
  font-weight: 400 !important;
}
.hero-chips {
  margin-top: 0.95rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.hero-chip {
  color: #FFFFFF !important;
  border: 1px solid rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.14);
  border-radius: 999px;
  padding: 0.22rem 0.7rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.runtime-pill {
  display: inline-block;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.16);
  color: #D7EFE6 !important;
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  font-size: 0.8rem;
  font-family: ui-monospace, Consolas, monospace;
  margin: 0.15rem 0 0.55rem 0;
}

[data-testid="stMain"] .stButton > button {
  background: #FFFFFF !important;
  color: #12201C !important;
  border: 1px solid #C5D0CA !important;
  border-radius: 11px !important;
  font-weight: 600 !important;
}
[data-testid="stMain"] .stButton > button:hover {
  border-color: #1B6B5A !important;
  color: #1B6B5A !important;
}

div[data-testid="stChatMessage"] {
  background: #FFFFFF !important;
  border: 1px solid #D5DEE6 !important;
  border-radius: 14px !important;
}

/* Main captions / helper text — stronger contrast */
[data-testid="stMain"] [data-testid="stCaptionContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {
  color: #3F524B !important;
  opacity: 1 !important;
}
[data-testid="stMain"] .stButton > button p {
  color: #12201C !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Meridian Supply | Support Agent",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

_inject_styles()

try:
    settings = get_settings()
    provider_label = f"{settings.provider} · {settings.chat_model}"
except Exception as exc:  # noqa: BLE001
    st.error(f"Configuration error: {exc}")
    st.info("Create a `.env` file from `env.example` and set `GROQ_API_KEY`.")
    st.stop()

orders = json.loads(ORDERS_PATH.read_text(encoding="utf-8"))
tickets = _load_list(TICKETS_PATH)
returns = _load_list(RETURNS_PATH)

with st.sidebar:
    st.markdown("### Meridian Supply")
    st.caption("Support operations console")
    st.markdown("**Runtime**")
    st.markdown(
        f'<div class="runtime-pill">{provider_label}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Embeddings**")
    st.markdown(
        f'<div class="runtime-pill">{settings.embed_backend}</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("#### Sample orders")
    for oid, order in orders.items():
        status = STATUS_LABEL.get(order["status"], order["status"])
        email = order["customer_email"].replace("@", "＠")
        st.markdown(f"**{oid}** — {status}")
        st.caption(email)
    st.divider()
    st.markdown("#### Open tickets")
    if not tickets:
        st.caption("No tickets yet.")
    else:
        for t in tickets[-6:]:
            st.markdown(f"**{t['ticket_id']}** · {t['priority']}  \n{t['summary']}")
    st.markdown("#### Returns")
    if not returns:
        st.caption("No returns yet.")
    else:
        for r in returns[-6:]:
            st.markdown(f"**{r['return_id']}** · {r['order_id']}  \n`{r['status']}`")
    st.divider()
    if st.button("Reset conversation", use_container_width=True):
        for key in ("messages", "history", "last_trace", "pending_prompt"):
            st.session_state.pop(key, None)
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = []
if "last_trace" not in st.session_state:
    st.session_state.last_trace = []

# Inline styles on every hero text node so theme CSS cannot wash them out
st.markdown(
    f"""
<div class="hero">
  <p class="hero-kicker" style="color:#B7E0D2!important;">Portfolio live demo</p>
  <p class="hero-title" style="color:#FFFFFF!important;">Meridian Supply Support</p>
  <p class="hero-sub" style="color:#E4F2EC!important;">
    AI resolution agent with RAG over policy docs, identity-gated order lookup,
    return initiation, and confidence-aware human escalation.
  </p>
  <div class="hero-chips">
    <span class="hero-chip" style="color:#FFFFFF!important;">LangChain tools</span>
    <span class="hero-chip" style="color:#FFFFFF!important;">FAISS RAG</span>
    <span class="hero-chip" style="color:#FFFFFF!important;">Human escalation</span>
    <span class="hero-chip" style="color:#FFFFFF!important;">{provider_label}</span>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
m1.metric("Orders in demo DB", len(orders))
m2.metric("Tickets opened", len(tickets))
m3.metric("Returns filed", len(returns))

st.subheader("Try a scenario")
demo_cols = st.columns(4)
for col, (label, text) in zip(demo_cols, DEMO_PROMPTS):
    with col:
        if st.button(label, key=f"demo_{label}", use_container_width=True):
            st.session_state.pending_prompt = text

col_chat, col_ops = st.columns([1.55, 1.0], gap="large")

with col_chat:
    st.subheader("Customer conversation")
    st.caption("Ask about shipping, refunds, warranties, or a sample order.")

    if not st.session_state.messages:
        st.info(
            "Start with a demo scenario above, or ask: "
            "Where is MS-20481? Email alex@example.com"
        )

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.session_state.pop("pending_prompt", None) or st.chat_input(
        "Message Meridian Support…"
    )

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Looking up policies and tools…"):
                try:
                    agent = _get_agent()
                    turn_messages = st.session_state.history + [("human", prompt)]
                    result = agent.invoke({"messages": turn_messages})
                    answer = _normalize_answer(result["messages"][-1].content)
                    st.session_state.last_trace = _extract_tool_trace(result["messages"])
                except Exception as exc:  # noqa: BLE001
                    answer = f"Sorry — the agent hit an error: `{exc}`"
                    st.error(answer)
            st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.history.extend([("human", prompt), ("ai", answer)])
        st.rerun()

with col_ops:
    st.subheader("Agent activity")
    st.caption("Live tool calls from the last turn — useful in interviews.")

    if not st.session_state.last_trace:
        st.write("No tool activity yet. Send a message to see tools fire.")
    else:
        for i, step in enumerate(st.session_state.last_trace, 1):
            if step["kind"] == "call":
                with st.expander(f"{i}. Called `{step['name']}`", expanded=True):
                    st.json(step["args"])
            else:
                with st.expander(f"{i}. Result from `{step['name']}`", expanded=False):
                    st.code(step["content"], language="json")

    with st.container(border=True):
        st.markdown("**What this demo shows**")
        st.markdown(
            "- Grounded answers from policy RAG\n"
            "- Email-verified order lookups\n"
            "- Return creation for delivered orders\n"
            "- Ticket escalation when confidence is low"
        )

st.caption("Meridian Supply — portfolio demo. Sample data only. API keys stay server-side.")
