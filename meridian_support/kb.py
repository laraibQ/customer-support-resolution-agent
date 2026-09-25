"""Knowledge base: chunk policies and retrieve with TF-IDF."""
from __future__ import annotations

import pickle
import re
from dataclasses import dataclass

from meridian_support.settings import DATA_DIR, INDEX_DIR, TFIDF_PATH


@dataclass
class Passage:
    source: str
    text: str


def _split_markdown(text: str, max_chars: int = 550, overlap: int = 60) -> list[str]:
    """Heading-aware markdown chunker."""
    parts = re.split(r"(?m)(?=^##\s)", text.strip())
    chunks: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= max_chars:
            chunks.append(part)
            continue
        start = 0
        while start < len(part):
            end = min(start + max_chars, len(part))
            chunks.append(part[start:end].strip())
            if end >= len(part):
                break
            start = max(0, end - overlap)
    return [c for c in chunks if c]


def collect_passages() -> list[Passage]:
    paths = sorted(DATA_DIR.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No Markdown policies in {DATA_DIR}")
    out: list[Passage] = []
    for path in paths:
        for chunk in _split_markdown(path.read_text(encoding="utf-8")):
            out.append(Passage(source=path.name, text=chunk))
    return out


def build_index() -> None:
    from sklearn.feature_extraction.text import TfidfVectorizer

    passages = collect_passages()
    texts = [p.text for p in passages]
    sources = [p.source for p in passages]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=12000)
    matrix = vectorizer.fit_transform(texts)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    TFIDF_PATH.write_bytes(
        pickle.dumps(
            {
                "vectorizer": vectorizer,
                "matrix": matrix,
                "texts": texts,
                "sources": sources,
            }
        )
    )
    print(f"Indexed {len(texts)} passages -> {TFIDF_PATH}")


_CACHE: dict | None = None


def _load() -> dict:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not TFIDF_PATH.exists():
        build_index()
    _CACHE = pickle.loads(TFIDF_PATH.read_bytes())
    return _CACHE


def search(query: str, *, k: int = 4, source: str | None = None) -> list[Passage]:
    from sklearn.metrics.pairwise import cosine_similarity

    store = _load()
    q = store["vectorizer"].transform([query])
    scores = cosine_similarity(q, store["matrix"]).ravel()
    order = scores.argsort()[::-1]
    hits: list[Passage] = []
    for idx in order:
        if scores[idx] <= 0:
            break
        src = store["sources"][idx]
        if source and src != source:
            continue
        hits.append(Passage(source=src, text=store["texts"][idx]))
        if len(hits) >= k:
            break
    return hits


if __name__ == "__main__":
    build_index()
