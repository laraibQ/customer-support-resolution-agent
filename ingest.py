"""Build a local knowledge base from /data Markdown docs.

Default for Groq demos: TF-IDF (instant, no Torch).
Optional: FAISS + HuggingFace / API embeddings via EMBED_BACKEND.

    python ingest.py
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import MarkdownTextSplitter

from config import get_settings

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
INDEX_DIR = ROOT / "kb_index"
TFIDF_PATH = INDEX_DIR / "tfidf_kb.pkl"
_TFIDF_CACHE: dict | None = None


def _chunk_docs() -> tuple[list[str], list[dict]]:
    docs_paths = sorted(DATA_DIR.glob("*.md"))
    if not docs_paths:
        raise SystemExit(f"No Markdown docs found in {DATA_DIR}")

    splitter = MarkdownTextSplitter(chunk_size=600, chunk_overlap=80)
    texts: list[str] = []
    metadatas: list[dict] = []
    for path in docs_paths:
        raw = path.read_text(encoding="utf-8")
        for chunk in splitter.split_text(raw):
            texts.append(chunk)
            metadatas.append({"source": path.name})
    return texts, metadatas


def build_tfidf_index() -> None:
    from sklearn.feature_extraction.text import TfidfVectorizer

    texts, metadatas = _chunk_docs()
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=12000,
    )
    matrix = vectorizer.fit_transform(texts)
    INDEX_DIR.mkdir(exist_ok=True)
    payload = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "texts": texts,
        "metadatas": metadatas,
    }
    TFIDF_PATH.write_bytes(pickle.dumps(payload))
    print(f"Saved TF-IDF index ({len(texts)} chunks) to {TFIDF_PATH}")


def load_tfidf_index() -> dict:
    global _TFIDF_CACHE
    if _TFIDF_CACHE is not None:
        return _TFIDF_CACHE
    if not TFIDF_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at {TFIDF_PATH}. Run `python ingest.py` first."
        )
    _TFIDF_CACHE = pickle.loads(TFIDF_PATH.read_bytes())
    return _TFIDF_CACHE


def search_tfidf(query: str, k: int = 4, source: str | None = None) -> list[tuple[str, str]]:
    """Return list of (source, text) hits."""
    from sklearn.metrics.pairwise import cosine_similarity

    kb = load_tfidf_index()
    q = kb["vectorizer"].transform([query])
    scores = cosine_similarity(q, kb["matrix"]).ravel()
    order = scores.argsort()[::-1]
    hits: list[tuple[str, str]] = []
    for idx in order:
        if scores[idx] <= 0:
            break
        meta = kb["metadatas"][idx]
        src = meta.get("source", "unknown")
        if source and src != source:
            continue
        hits.append((src, kb["texts"][idx]))
        if len(hits) >= k:
            break
    return hits


def build_faiss_index() -> None:
    from langchain_community.vectorstores import FAISS

    from config import build_embeddings

    settings = get_settings()
    texts, metadatas = _chunk_docs()
    print(
        f"Embedding {len(texts)} chunks via {settings.provider} / {settings.embed_model}..."
    )
    store = FAISS.from_texts(texts, build_embeddings(), metadatas=metadatas)
    INDEX_DIR.mkdir(exist_ok=True)
    store.save_local(str(INDEX_DIR))
    print(f"Saved FAISS index to {INDEX_DIR}")


def load_faiss_index():
    from langchain_community.vectorstores import FAISS

    from config import build_embeddings

    if not (INDEX_DIR / "index.faiss").exists():
        raise FileNotFoundError(
            f"FAISS index not found in {INDEX_DIR}. Run `python ingest.py` with EMBED_BACKEND=local."
        )
    return FAISS.load_local(
        str(INDEX_DIR),
        build_embeddings(),
        allow_dangerous_deserialization=True,
    )


def build_index() -> None:
    settings = get_settings()
    backend = settings.embed_backend or "tfidf"
    if backend in {"tfidf", "local-fast"}:
        build_tfidf_index()
    else:
        build_faiss_index()


def load_index():
    """Compatibility helper used by tools (FAISS path)."""
    return load_faiss_index()


if __name__ == "__main__":
    build_index()
