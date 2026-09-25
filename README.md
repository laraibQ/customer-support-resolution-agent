# Meridian Supply — Customer Support Resolution Agent

Portfolio project: a SaaS-style support agent that answers policy questions from a RAG knowledge base, looks up orders with email verification, starts returns, and escalates to human tickets when confidence is low.

**Stack:** LangChain tool-calling · FAISS RAG · Streamlit · **Groq** (default) / Nebius / OpenAI

Adapted from [awesome-ai-apps / customer_support_resolution_agent](https://github.com/Arindam200/awesome-ai-apps/tree/main/advance_ai_agents/customer_support_resolution_agent) (MIT) and customized for portfolio use. See [ARCHITECTURE.md](ARCHITECTURE.md) and [PHASES.md](PHASES.md).

---

## What this proves on a resume

- Built a **tool-calling LLM agent** (not a single-prompt chatbot)
- Implemented **RAG** over policy docs with local vector search (FAISS)
- Added **identity-gated** order lookup (email match before PII)
- Designed **human-in-the-loop escalation** with persistent tickets
- Shipped a **demo UI** that surfaces tool traces for explainability

### Suggested resume bullets

- Built a customer-support resolution agent with LangChain tool-calling, FAISS RAG, and confidence-based human escalation.
- Implemented order lookup with email verification, return initiation, and ticket persistence for unresolved issues.
- Delivered a Streamlit demo that visualizes agent tool calls for debugging and stakeholder demos; supports Nebius or OpenAI providers.

---

## Features

| Capability | How |
| ---------- | --- |
| Knowledge-grounded answers | FAISS over FAQ, refund, shipping, warranty Markdown |
| Order lookup | `lookup_order` + email gate |
| Returns | `start_return` for delivered orders |
| Escalation | `create_ticket` → `data/tickets.json` |
| Tool transparency | Live tool-trace panel in Streamlit |
| Provider flexibility | `LLM_PROVIDER=groq` (default) / `openai` / `nebius` |

---

## Tools

| Tool | Purpose |
| ---- | ------- |
| `lookup_order` | Status, items, tracking (email-verified) |
| `kb_search` | Semantic search across all policy docs |
| `refund_policy_search` | Refund/returns-only retrieval |
| `start_return` | Create return + prepaid label placeholder |
| `create_ticket` | Human escalation |

---

## Setup

### Prerequisites

- Python 3.10+
- Free [Groq](https://console.groq.com/) API key (default), or OpenAI / Nebius

### 1. Install

```bash
cd portfolio-projects/01-customer-support-resolution-agent
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -e .
```

### 2. Configure

```bash
copy env.example .env
# Edit .env — set GROQ_API_KEY (kept local; never commit .env)
```

Default stack:
- **Chat:** Groq `openai/gpt-oss-20b`
- **Embeddings:** local `sentence-transformers/all-MiniLM-L6-v2` (free, no API)

### 3. Build knowledge base (once)

```bash
python ingest.py
```

### 4. Run

```bash
streamlit run app.py
# or
python main.py
```

---

## Demo prompts

**Orders**

- `Where is MS-20481? My email is alex@example.com.`
- `Status of MS-20482 for priya@example.com`

**Policy**

- `How long does standard shipping take?`
- `What's your refund window for unused items?`
- `Does the daypack have a warranty?`

**Returns / escalation**

- `Start a return for MS-20483, email jordan@example.com, wrong size`
- `My package arrived broken — I need a human`

---

## Project layout

```
01-customer-support-resolution-agent/
├── agent.py           # LangChain agent + system prompt
├── tools.py           # Order / RAG / return / ticket tools
├── ingest.py          # Build FAISS index from data/*.md
├── config.py          # Nebius / OpenAI provider switch
├── app.py             # Streamlit UI + tool trace
├── main.py            # CLI
├── data/              # KB docs + sample orders / tickets / returns
├── ARCHITECTURE.md
├── PHASES.md
└── env.example
```

---

## License

MIT (upstream awesome-ai-apps). Customizations in this folder are part of the portfolio workspace.
