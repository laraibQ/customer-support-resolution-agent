# Meridian Supply — Customer Support Resolution Agent

Portfolio project by [laraibQ](https://github.com/laraibQ): a support resolution
agent with policy retrieval, email-gated order lookup, return intake, and human
escalation.

**Repo:** https://github.com/laraibQ/customer-support-resolution-agent

**Stack:** LangChain tool-calling · TF-IDF retrieval · Streamlit · Groq (default)

---

## What I built

- Tool-calling agent (not a single-prompt chatbot)
- Local TF-IDF RAG over original Meridian policy docs
- Identity-gated order lookup
- Return creation + human ticket escalation
- Streamlit UI with live tool activity

### Resume bullets

- Built a Meridian Supply support agent with LangChain, Groq, and TF-IDF RAG.
- Implemented email-verified order lookup, return intake, and ticket escalation.
- Shipped a Streamlit demo with tool-trace visibility for walkthroughs.

---

## Setup

```bash
git clone https://github.com/laraibQ/customer-support-resolution-agent.git
cd customer-support-resolution-agent
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy env.example .env   # set GROQ_API_KEY
python ingest.py
streamlit run app.py --server.fileWatcherType none
# or: python main.py
```

Defaults (`meridian_support/settings.py`):

| Variable | Default |
| -------- | ------- |
| `LLM_PROVIDER` | `groq` |
| `GROQ_MODEL` | `openai/gpt-oss-20b` |
| `RETRIEVAL_BACKEND` | `tfidf` |

---

## Smoke tests

```bash
pytest -q
```

Streamlit: click **Track order** and confirm tool activity.  
CLI: ask “How long does ground shipping take?” then `exit`.

---

## Demo prompts

- `Where is MG-4412? Email alex@example.com`
- `How many days do I have to return unused items?`
- `Open a return for MG-4425, jordan@example.com, wrong size`
- `Package arrived cracked — escalate`

---

## Layout

```
.
├── app.py                 # Streamlit UI
├── main.py                # CLI
├── ingest.py              # Build TF-IDF index
├── meridian_support/      # Agent package
│   ├── settings.py
│   ├── kb.py
│   ├── store.py
│   ├── tools.py
│   └── agent.py
├── data/                  # Policies + sample orders
└── tests/
```

---

## Privacy

Sample orders/tickets/returns are fictional. Do not commit `.env` or real PII.
Reset `data/tickets.json` / `data/returns.json` before public screenshots.

---

## License

MIT © laraibQ — see [LICENSE](LICENSE).
