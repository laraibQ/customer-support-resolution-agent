"""Runtime settings for LLM providers and knowledge retrieval."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
INDEX_DIR = ROOT / "kb_index"
TFIDF_PATH = INDEX_DIR / "tfidf.pkl"

load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    provider: str
    api_key: str
    chat_model: str
    retrieval: str
    base_url: str | None


def load_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    retrieval = os.getenv("RETRIEVAL_BACKEND", os.getenv("EMBED_BACKEND", "tfidf")).strip().lower()

    if provider == "groq":
        key = os.getenv("GROQ_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            raise RuntimeError("Set GROQ_API_KEY in .env (LLM_PROVIDER=groq).")
        return Settings(
            provider="groq",
            api_key=key,
            chat_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            retrieval=retrieval or "tfidf",
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        )

    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key:
            raise RuntimeError("Set OPENAI_API_KEY in .env (LLM_PROVIDER=openai).")
        return Settings(
            provider="openai",
            api_key=key,
            chat_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            retrieval=retrieval or "tfidf",
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER={provider!r}. Use 'groq' or 'openai'."
    )


def build_chat_llm(temperature: float = 0):
    settings = load_settings()
    from langchain_openai import ChatOpenAI

    kwargs = {
        "model": settings.chat_model,
        "api_key": settings.api_key,
        "temperature": temperature,
        "max_tokens": 700,
        "timeout": 45,
        "max_retries": 1,
    }
    if settings.base_url:
        kwargs["base_url"] = settings.base_url
    return ChatOpenAI(**kwargs)
