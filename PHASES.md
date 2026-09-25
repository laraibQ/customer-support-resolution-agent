# Project history — Meridian Support Agent

This repo started from the MIT-licensed
[customer_support_resolution_agent](https://github.com/Arindam200/awesome-ai-apps/tree/main/advance_ai_agents/customer_support_resolution_agent)
example in [awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps), then was customized for local demos and portfolio presentation. Upstream attribution: [NOTICE](NOTICE).

## Phase 0 — Bootstrap ✅

- Standalone project folder (repo root for this app)
- Started from upstream starter sources (MIT)

## Phase 1 — Architecture & skeleton ✅

- Modules: ingest → tools → agent → UI/CLI
- Documented stack and escalation rules
- Env template, gitignore, provider config

## Phase 2 — Customization ✅

- Meridian Supply branding and expanded KB (+ warranty)
- Providers: Groq (default), OpenAI, Nebius
- Extra tool: `start_return`
- Streamlit UI with tool-call visibility

## Phase 3 — Runnable path ✅

- venv + editable install
- `.env` for Groq + `EMBED_BACKEND=tfidf` (gitignored secrets)
- `python ingest.py` builds TF-IDF index
- Streamlit / CLI entrypoints

## Phase 4 — Documentation ✅

- README, ARCHITECTURE, NOTICE, LICENSE
- Honest skills / resume framing (derivative, not from-scratch)

## Phase 5 — Verify & harden ✅

- Tool unit tests (order / return / ticket)
- Documented smoke-test path for Streamlit + CLI
- Latency: TF-IDF path avoids Torch cold-start on RAG tools
