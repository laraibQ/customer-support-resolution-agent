# Architecture — Meridian Support Agent

Original design for the Meridian Supply support resolution demo.

## Flow

```
Shopper message
      │
      ▼
 Streamlit (app.py) or CLI (main.py)
      │
      ▼
 LangChain agent (meridian_support.agent)
  Chat model via Groq OpenAI-compatible API
      │ tool calls
      ▼
 meridian_support.tools
  ├─ get_order_details     → store (orders.json)
  ├─ search_policies       → kb TF-IDF index
  ├─ search_returns_policy → kb filtered
  ├─ open_return_request   → store (returns.json)
  └─ escalate_to_human     → store (tickets.json)
```

## Packages

| Module | Role |
| ------ | ---- |
| `settings.py` | Env loading, Groq/OpenAI chat client |
| `kb.py` | Markdown chunking + TF-IDF build/search |
| `store.py` | Orders / tickets / returns persistence |
| `tools.py` | LangChain `@tool` wrappers |
| `agent.py` | System instructions + `create_agent` |

## Escalation

Call `escalate_to_human` when retrieval is weak, the shopper wants a person,
fraud is alleged, or damaged goods need photo review.

## Retrieval

Default `RETRIEVAL_BACKEND=tfidf` keeps demos fast (no Torch). Index path:
`kb_index/tfidf.pkl` (gitignored).
