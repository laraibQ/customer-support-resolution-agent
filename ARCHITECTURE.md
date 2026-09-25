# Architecture

## Request path

```
User message
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
  ├─ get_order_details       → store (orders.json)
  ├─ search_policies         → kb TF-IDF index
  ├─ search_returns_policy   → kb filtered
  ├─ open_return_request     → store (returns.json)
  └─ escalate_to_human       → store (tickets.json)
```

## Modules

| Module | Responsibility |
| ------ | -------------- |
| `settings.py` | Configuration and chat client |
| `kb.py` | Markdown chunking and TF-IDF retrieval |
| `store.py` | Orders, tickets, and returns persistence |
| `tools.py` | LangChain tool wrappers |
| `agent.py` | System prompt and agent construction |

## Escalation

`escalate_to_human` is used when retrieval is insufficient, the shopper requests
a person, fraud is alleged, or damaged goods need photo review.

## Retrieval

Default backend is TF-IDF (`RETRIEVAL_BACKEND=tfidf`). Index file:
`kb_index/tfidf.pkl` (gitignored; built by `ingest.py` or on first search).
