# Architecture — Meridian Supply Support Agent

## Goal

Demonstrate a production-shaped **customer support AI agent**: grounded retrieval answers, identity-gated order lookup, return initiation, and confidence-aware human escalation — with a visible tool trace for demos.

## System diagram

```
Customer message
      │
      ▼
┌─────────────────┐
│  Streamlit UI   │  ← shows tool trace (calls + results)
│  or CLI (main)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LangChain agent │  create_agent + system prompt rules
│ Chat via Groq   │  default: openai/gpt-oss-20b
│ (OpenAI/Nebius  │  optional via LLM_PROVIDER
│  compatible)    │
└────────┬────────┘
         │ tool calls
         ▼
┌──────────────────────────────────────────────┐
│ Tools                                        │
│  lookup_order         → data/orders.json     │
│  kb_search            → TF-IDF (data/*.md)   │
│  refund_policy_search → TF-IDF filtered      │
│  start_return         → data/returns.json    │
│  create_ticket        → data/tickets.json    │
└──────────────────────────────────────────────┘
```

Optional path: `EMBED_BACKEND=local` (or other non-`tfidf` values) builds/loads a FAISS index instead — see `ingest.py` and optional extra `.[faiss]`.

## Providers (`config.py`)

| `LLM_PROVIDER` | Chat | Default retrieval |
| -------------- | ---- | ----------------- |
| `groq` (default) | Groq OpenAI-compatible API | `tfidf` |
| `openai` | OpenAI (or compatible `OPENAI_BASE_URL`) | `openai` embeddings unless overridden |
| `nebius` | Nebius Token Factory | Nebius embeddings unless overridden |

`EMBED_BACKEND` can override retrieval: `tfidf` (fast, no Torch), `local` / FAISS+HF, `openai`, `nebius`.

## Why this structure

| Layer | Responsibility |
| ----- | -------------- |
| `config.py` | Provider switch so demos are not locked to one vendor |
| `ingest.py` | One-time KB build (TF-IDF pickle or FAISS) |
| `tools.py` | Side-effectful business actions; keep agent logic out of prompts |
| `agent.py` | System prompt + tool registration; escalation policy lives here |
| `app.py` | Demo surface: chat + live tool trace + ticket/return sidebars |

## Escalation policy (explicit)

The agent **must** call `create_ticket` when:

- KB retrieval is insufficient / low confidence
- Customer asks for a human, alleges fraud, or is clearly upset
- Damaged/wrong item needs photo review
- A tool error cannot be fixed in one retry

## What changed vs the upstream starter

Documented differences (still a derivative — see [NOTICE](NOTICE)):

1. Meridian Supply branding + warranty KB doc
2. Extra `start_return` tool with eligibility checks
3. Groq-first config + TF-IDF default for fast local demos
4. Tool-trace panel in the Streamlit UI
5. Tests, pinned deps, and expanded documentation

## Upstream credit

Adapted from [Arindam200/awesome-ai-apps — customer_support_resolution_agent](https://github.com/Arindam200/awesome-ai-apps/tree/main/advance_ai_agents/customer_support_resolution_agent) (MIT).
