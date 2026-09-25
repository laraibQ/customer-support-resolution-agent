"""Shared runtime config for LLM + embeddings providers."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    provider: str  # "groq" | "openai" | "nebius"
    api_key: str
    chat_model: str
    embed_backend: str  # "local" | "openai" | "nebius"
    embed_model: str
    base_url: str | None


def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    embed_backend = os.getenv("EMBED_BACKEND", "").strip().lower()

    if provider == "groq":
        api_key = (
            os.getenv("GROQ_API_KEY", "").strip()
            or os.getenv("OPENAI_API_KEY", "").strip()
        )
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is required when LLM_PROVIDER=groq"
            )
        # Groq has no embeddings API — default to fast TF-IDF (no Torch cold start).
        if not embed_backend:
            embed_backend = "tfidf"
        return Settings(
            provider="groq",
            api_key=api_key,
            chat_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            embed_backend=embed_backend,
            embed_model=os.getenv(
                "LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            base_url=os.getenv(
                "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
            ),
        )

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        if not embed_backend:
            embed_backend = "openai"
        return Settings(
            provider="openai",
            api_key=api_key,
            chat_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            embed_backend=embed_backend,
            embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )

    # Nebius Token Factory
    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "NEBIUS_API_KEY is required when LLM_PROVIDER=nebius "
            "(or set LLM_PROVIDER=groq / openai)."
        )
    if not embed_backend:
        embed_backend = "nebius"
    return Settings(
        provider="nebius",
        api_key=api_key,
        chat_model=os.getenv("NEBIUS_MODEL", "Qwen/Qwen3-30B-A3B"),
        embed_backend=embed_backend,
        embed_model=os.getenv("NEBIUS_EMBED_MODEL", "Qwen/Qwen3-Embedding-8B"),
        base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
    )


def build_chat_model(temperature: float = 0):
    settings = get_settings()

    if settings.provider in {"groq", "openai"}:
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

    from langchain_nebius import ChatNebius

    return ChatNebius(
        model=settings.chat_model,
        api_key=settings.api_key,
        temperature=temperature,
    )


def build_embeddings():
    settings = get_settings()

    if settings.embed_backend == "local":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=os.getenv(
                "LOCAL_EMBED_MODEL", settings.embed_model
            )
        )

    if settings.embed_backend == "openai" or settings.provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        kwargs = {
            "model": settings.embed_model,
            "api_key": settings.api_key,
        }
        if settings.base_url and settings.provider == "openai":
            kwargs["base_url"] = settings.base_url
        return OpenAIEmbeddings(**kwargs)

    from langchain_nebius import NebiusEmbeddings

    return NebiusEmbeddings(
        model=settings.embed_model,
        api_key=settings.api_key,
    )
