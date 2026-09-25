# Architecture — Meridian Supply Support Agent

## Goal

Demonstrate a production-shaped **customer support AI agent**: grounded RAG answers, identity-gated order lookup, return initiation, and confidence-aware human escalation — with a visible tool trace for demos/interviews.

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
│ (ChatNebius or  │
│  ChatOpenAI)    │
└────────┬────────┘
         │ tool calls
         ▼
┌──────────────────────────────────────────────┐
│ Tools                                        │
│  lookup_order      → data/orders.json        │
│  kb_search         → FAISS (data/*.md)       │
│  refund_policy_search → FAISS filtered       │
│  start_return      → data/returns.json       │
│  create_ticket     → data/tickets.json       │
└──────────────────────────────────────────────┘
```

## Why this structure

| Layer | Responsibility |
| ----- | -------------- |
| `config.py` | Provider switch (Nebius / OpenAI) so the project is runnable without vendor lock-in |
| `ingest.py` | One-time embedding of Markdown KB into local FAISS |
| `tools.py` | Side-effectful business actions; keep agent logic out of prompts |
| `agent.py` | System prompt + tool registration; escalation policy lives here |
| `app.py` | Demo surface: chat + live tool trace + ticket/return sidebars |

## Escalation policy (explicit)

The agent **must** call `create_ticket` when:

- KB retrieval is insufficient / low confidence
- Customer asks for a human, alleges fraud, or is clearly upset
- Damaged/wrong item needs photo review
- A tool error cannot be fixed in one retry

## Portfolio differentiators vs upstream demo

1. Rebranded domain + warranty KB doc
2. Extra `start_return` tool with eligibility checks
3. Dual LLM/embeddings provider
4. Tool-trace panel in the UI (interview-friendly)
5. Architecture + resume bullets documented

## Upstream credit

Adapted from [Arindam200/awesome-ai-apps — customer_support_resolution_agent](https://github.com/Arindam200/awesome-ai-apps/tree/main/advance_ai_agents/customer_support_resolution_agent) (MIT).
