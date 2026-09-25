# Meridian Supply — Customer Support Resolution Agent

SaaS-style support agent that answers policy questions from a local knowledge
base, looks up orders with email verification, starts returns, and escalates to
human tickets when confidence is low.

**Stack:** LangChain tool-calling · TF-IDF RAG (default) · Streamlit · **Groq** (default), with optional OpenAI / Nebius

This repository is an **adapted and extended** version of the MIT-licensed
[customer_support_resolution_agent](https://github.com/Arindam200/awesome-ai-apps/tree/main/advance_ai_agents/customer_support_resolution_agent)
demo from [awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps). See [NOTICE](NOTICE), [ARCHITECTURE.md](ARCHITECTURE.md), and [PHASES.md](PHASES.md).

---

## Skills demonstrated

Honest framing for portfolios: this is a **customized derivative**, not a green-field product.

- Tool-calling LLM agent (LangChain), not a single-prompt chatbot
- Retrieval-augmented answers over policy Markdown (TF-IDF by default; optional FAISS)
- Identity-gated order lookup (email match before exposing order details)
- Human-in-the-loop escalation with persistent tickets
- Demo UI that surfaces tool traces for explainability

### Example resume bullets (keep accurate)

- Extended an open-source LangChain support-agent starter with Groq, TF-IDF RAG, return initiation, and a Streamlit tool-trace UI.
- Implemented email-verified order lookup and ticket escalation against sample commerce data.
- Documented architecture, smoke tests, and provider configuration for local demos.

---

## Features

| Capability | How |
| ---------- | --- |
| Knowledge-grounded answers | TF-IDF over FAQ, refund, shipping, warranty Markdown (`EMBED_BACKEND=tfidf`) |
| Order lookup | `lookup_order` + email gate |
| Returns | `start_return` for delivered orders |
| Escalation | `create_ticket` → `data/tickets.json` |
| Tool transparency | Live tool-trace panel in Streamlit |
| Providers | `LLM_PROVIDER=groq` (default) / `openai` / `nebius` |

---

## Tools

| Tool | Purpose |
| ---- | ------- |
| `lookup_order` | Status, items, tracking (email-verified) |
| `kb_search` | Retrieval across all policy docs |
| `refund_policy_search` | Refund/returns-only retrieval |
| `start_return` | Create return + prepaid label placeholder |
| `create_ticket` | Human escalation |

---

## Privacy (demo data)

- `data/orders.json`, `data/tickets.json`, and `data/returns.json` are **fictional sample data** for demos.
- Do not put real customer PII in this repo.
- Tickets/returns created in a live demo are written locally; they are gitignored patterns under `kb_index/` for indexes — keep `.env` and any real secrets out of git.
- Before sharing screenshots or deploying publicly, clear or reset `data/tickets.json` and `data/returns.json` if they contain session-generated records.

---

## Setup

### Prerequisites

- Python 3.10+
- Free [Groq](https://console.groq.com/) API key (default), or OpenAI / Nebius

### 1. Install

```bash
git clone <your-repo-url> meridian-support-agent
cd meridian-support-agent
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[nebius]"   # Nebius chat/embeddings
pip install -e ".[faiss]"    # FAISS + local HF embeddings path
```

### 2. Configure

```bash
copy env.example .env
# Edit .env — set GROQ_API_KEY (local only; never commit .env)
```

Default stack (matches `config.py`):

| Setting | Default |
| ------- | ------- |
| `LLM_PROVIDER` | `groq` |
| Chat model | `GROQ_MODEL=openai/gpt-oss-20b` |
| Retrieval | `EMBED_BACKEND=tfidf` |

### 3. Build knowledge base (once)

```bash
python ingest.py
```

### 4. Run

Streamlit UI:

```bash
streamlit run app.py
# recommended flags for local demos:
# streamlit run app.py --server.fileWatcherType none
```

CLI:

```bash
python main.py
```

---

## Smoke tests

**Automated (no API key):**

```bash
pytest -q
```

**Manual Streamlit:** open the UI → click **Track order** → confirm a tool call appears in **Agent activity**.

**Manual CLI:**

```bash
python main.py
# You: How long does standard shipping take?
# Expect a short policy-grounded answer, then type exit
```

**Manual Groq e2e (needs `.env`):** ask a policy question and an order lookup with a sample email from the sidebar.

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
.
├── agent.py           # LangChain agent + system prompt
├── tools.py           # Order / RAG / return / ticket tools
├── ingest.py          # Build TF-IDF (default) or FAISS index from data/*.md
├── config.py          # Groq / OpenAI / Nebius provider switch
├── app.py             # Streamlit UI + tool trace
├── main.py            # CLI
├── data/              # KB docs + sample orders / tickets / returns
├── tests/             # Tool unit tests
├── ARCHITECTURE.md
├── PHASES.md
├── NOTICE             # Upstream attribution
├── LICENSE
└── env.example
```

---

## License

MIT — see [LICENSE](LICENSE) and [NOTICE](NOTICE) for upstream attribution.
