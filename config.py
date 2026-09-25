"""Shared runtime config for LLM + embeddings providers."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    provider: str  # "nebius" | "openai"
    api_key: str
    chat_model: str
    embed_model: str
    base_url: str | None


def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "nebius").strip().lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return Settings(
            provider="openai",
            api_key=api_key,
            chat_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small"),
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )

    # Default: Nebius Token Factory (OpenAI-compatible)
    api_key = os.getenv("NEBIUS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "NEBIUS_API_KEY is required when LLM_PROVIDER=nebius "
            "(or set LLM_PROVIDER=openai and OPENAI_API_KEY)."
        )
    return Settings(
        provider="nebius",
        api_key=api_key,
        chat_model=os.getenv("NEBIUS_MODEL", "Qwen/Qwen3-30B-A3B"),
        embed_model=os.getenv("NEBIUS_EMBED_MODEL", "Qwen/Qwen3-Embedding-8B"),
        base_url=os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/"),
    )


def build_chat_model(temperature: float = 0.2):
    settings = get_settings()
    if settings.provider == "openai":
        from langchain_openai import ChatOpenAI

        kwargs = {
            "model": settings.chat_model,
            "api_key": settings.api_key,
            "temperature": temperature,
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
    if settings.provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        kwargs = {
            "model": settings.embed_model,
            "api_key": settings.api_key,
        }
        if settings.base_url:
            kwargs["base_url"] = settings.base_url
        return OpenAIEmbeddings(**kwargs)

    from langchain_nebius import NebiusEmbeddings

    return NebiusEmbeddings(
        model=settings.embed_model,
        api_key=settings.api_key,
    )
