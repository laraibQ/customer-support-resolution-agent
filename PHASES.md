# Work Plan — Customer Support Resolution Agent

Portfolio project adapted from [awesome-ai-apps / customer_support_resolution_agent](https://github.com/Arindam200/awesome-ai-apps/tree/main/advance_ai_agents/customer_support_resolution_agent).

## Phase 0 — Bootstrap ✅
- Create dedicated folder under `portfolio-projects/`
- Fetch upstream source into this folder

## Phase 1 — Architecture & skeleton ✅
- Map modules: ingest → tools → agent → UI/CLI
- Document stack and escalation rules
- Add env template, gitignore, provider config

## Phase 2 — Customize for portfolio credibility ✅
- Rebrand to **Meridian Supply** (original domain data)
- Expand KB + order fixtures (+ warranty policy)
- Dual LLM provider: Nebius **or** OpenAI
- Extra tool: `start_return`
- Streamlit UI shows tool calls (demo-ready)

## Phase 3 — Runnable path ✅
- ✅ venv + `pip install -e .`
- ✅ `.env` configured for Groq + local embeddings (gitignored)
- ✅ `python ingest.py` — FAISS index built
- ⏳ Streamlit UI — run `streamlit run app.py` locally

## Phase 4 — Documentation ✅
- Portfolio README + ARCHITECTURE.md
- Resume bullet points

## Phase 5 — Verify & harden 🔄
- ✅ Tool smoke tests (order / return / ticket) without LLM
- 🔄 Groq e2e chat smoke test
