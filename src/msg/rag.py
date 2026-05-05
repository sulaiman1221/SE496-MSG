"""Retrieval over the doctrine corpus.

Loads .txt files from a directory, splits each one into overlapping
word windows, embeds every window with OpenAI text-embedding-3-small,
and returns the top-k most similar windows for any query string.

The embedding index is built once and pickled to disk. Subsequent
runs call ``load()`` instead of ``build()`` and skip the API calls.

The class is small on purpose so the whole flow can be read in one
sitting: load text, chunk, embed, score by cosine similarity, return
top k.
"""

import math
import pickle
from pathlib import Path
from typing import Iterable

from openai import OpenAI


class DoctrineRAG:
    """In-memory retrieval over a small text corpus."""

    def __init__(
        self,
        corpus_dir: Path | str,
        index_path: Path | str,
        embedding_model: str = "text-embedding-3-small",
        chunk_size_words: int = 400,
        overlap_words: int = 50,
        client: OpenAI | None = None,
    ) -> None:
        if overlap_words >= chunk_size_words:
            raise ValueError("overlap_words must be smaller than chunk_size_words")
        self.corpus_dir = Path(corpus_dir)
        self.index_path = Path(index_path)
        self.embedding_model = embedding_model
        self.chunk_size_words = chunk_size_words
        self.overlap_words = overlap_words
        self._client = client or OpenAI()
        self._chunks: list[dict] = []
        self._embeddings: list[list[float]] = []

    # ------------------------------------------------------------------
    # Build / load
    # ------------------------------------------------------------------

    def build(self) -> int:
        """Read every .txt under corpus_dir, chunk, embed, save to disk.

        Returns the number of chunks indexed.
        """
        self._chunks = list(self._load_chunks())
        if not self._chunks:
            raise FileNotFoundError(f"no .txt files in {self.corpus_dir}")
        self._embeddings = self._embed([c["text"] for c in self._chunks])
        self._save()
        return len(self._chunks)

    def load(self) -> None:
        """Load a previously built index from index_path."""
        with self.index_path.open("rb") as fp:
            data = pickle.load(fp)
        self._chunks = data["chunks"]
        self._embeddings = data["embeddings"]

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def retrieve(self, query: str, k: int = 3) -> list[dict]:
        """Return the top-k chunks scored by cosine similarity to query.

        Each result is a dict with keys: source, chunk_index, text, score.
        """
        if not self._embeddings:
            raise RuntimeError("call build() or load() first")
        query_vec = self._embed([query])[0]
        scored = [
            {**chunk, "score": _cosine(query_vec, emb)}
            for chunk, emb in zip(self._chunks, self._embeddings, strict=True)
        ]
        scored.sort(key=lambda c: c["score"], reverse=True)
        return scored[:k]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_chunks(self) -> Iterable[dict]:
        """Yield one dict per overlapping word window across all .txt files."""
        step = self.chunk_size_words - self.overlap_words
        for path in sorted(self.corpus_dir.glob("*.txt")):
            words = path.read_text(encoding="utf-8").split()
            for i, start in enumerate(range(0, len(words), step)):
                window = words[start : start + self.chunk_size_words]
                if not window:
                    continue
                yield {
                    "source": path.name,
                    "chunk_index": i,
                    "text": " ".join(window),
                }
                if start + self.chunk_size_words >= len(words):
                    break

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=self.embedding_model, input=texts
        )
        return [item.embedding for item in response.data]

    def _save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("wb") as fp:
            pickle.dump(
                {"chunks": self._chunks, "embeddings": self._embeddings}, fp
            )


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
