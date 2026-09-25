"""Build a FAISS knowledge base from /data Markdown docs.

Run once before starting the agent:

    python ingest.py

The index is written to ./kb_index/ and reloaded by tools.kb_search.
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownTextSplitter

from config import build_embeddings, get_settings

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
INDEX_DIR = ROOT / "kb_index"


def build_index() -> None:
    settings = get_settings()
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

    print(
        f"Embedding {len(texts)} chunks from {len(docs_paths)} docs "
        f"via {settings.provider} / {settings.embed_model}..."
    )
    store = FAISS.from_texts(texts, build_embeddings(), metadatas=metadatas)

    INDEX_DIR.mkdir(exist_ok=True)
    store.save_local(str(INDEX_DIR))
    print(f"Saved FAISS index to {INDEX_DIR}")


def load_index() -> FAISS:
    if not INDEX_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at {INDEX_DIR}. Run `python ingest.py` first."
        )
    return FAISS.load_local(
        str(INDEX_DIR),
        build_embeddings(),
        allow_dangerous_deserialization=True,
    )


if __name__ == "__main__":
    build_index()
