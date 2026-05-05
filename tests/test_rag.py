"""Tests for the doctrine RAG module."""

from unittest.mock import MagicMock

import pytest

from msg.rag import DoctrineRAG, _cosine


# ---------------------------------------------------------------------------
# Cosine similarity
# ---------------------------------------------------------------------------


def test_cosine_orthogonal_is_zero():
    assert _cosine([1, 0, 0], [0, 1, 0]) == 0.0


def test_cosine_identical_is_one():
    assert _cosine([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)


def test_cosine_opposite_is_minus_one():
    assert _cosine([1, 0], [-1, 0]) == pytest.approx(-1.0)


def test_cosine_zero_vector_is_zero():
    # Avoid division by zero. Score is undefined; we treat it as 0.
    assert _cosine([0, 0, 0], [1, 2, 3]) == 0.0


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------


def test_overlap_must_be_smaller_than_chunk_size(tmp_path):
    with pytest.raises(ValueError):
        DoctrineRAG(
            corpus_dir=tmp_path,
            index_path=tmp_path / "idx.pkl",
            chunk_size_words=10,
            overlap_words=10,
        )


# ---------------------------------------------------------------------------
# Chunking and retrieval
# ---------------------------------------------------------------------------


def _fake_client_with_embeddings(vectors: list[list[float]]) -> MagicMock:
    """Return a MagicMock that emulates openai.OpenAI for embeddings."""
    client = MagicMock()

    def fake_create(model, input):
        # Return one fake vector per input string.
        chosen = vectors[: len(input)]
        return MagicMock(data=[MagicMock(embedding=v) for v in chosen])

    client.embeddings.create.side_effect = fake_create
    return client


def test_build_creates_chunks_for_a_single_file(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "doc.txt").write_text(" ".join(["word"] * 100))

    client = _fake_client_with_embeddings([[1.0, 0.0, 0.0]] * 50)
    rag = DoctrineRAG(
        corpus_dir=corpus,
        index_path=tmp_path / "idx.pkl",
        chunk_size_words=20,
        overlap_words=5,
        client=client,
    )
    n = rag.build()

    # 100 words, step = 15, chunks roughly at starts 0,15,30,45,60,75,90
    # The last chunk includes word 100, so loop breaks → 7 chunks.
    assert n == 7


def test_build_raises_when_corpus_is_empty(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    rag = DoctrineRAG(
        corpus_dir=corpus,
        index_path=tmp_path / "idx.pkl",
        client=MagicMock(),
    )
    with pytest.raises(FileNotFoundError):
        rag.build()


def test_retrieve_returns_top_k_sorted_by_score(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "a.txt").write_text("alpha " * 50)
    (corpus / "b.txt").write_text("beta " * 50)

    # Three chunks expected (small docs). Hand-crafted vectors so
    # retrieval order is predictable.
    client = _fake_client_with_embeddings(
        [
            [1.0, 0.0],  # chunk 0 from a.txt
            [0.0, 1.0],  # chunk 1 from b.txt
            [0.5, 0.5],  # query
            [0.5, 0.5],  # query (called again on retrieve)
        ]
    )
    rag = DoctrineRAG(
        corpus_dir=corpus,
        index_path=tmp_path / "idx.pkl",
        chunk_size_words=200,
        overlap_words=10,
        client=client,
    )
    rag.build()
    results = rag.retrieve("test", k=2)

    assert len(results) == 2
    assert results[0]["score"] >= results[1]["score"]
    assert {r["source"] for r in results} == {"a.txt", "b.txt"}


def test_retrieve_before_build_or_load_raises(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    rag = DoctrineRAG(
        corpus_dir=corpus,
        index_path=tmp_path / "idx.pkl",
        client=MagicMock(),
    )
    with pytest.raises(RuntimeError):
        rag.retrieve("anything")


def test_load_round_trip(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "doc.txt").write_text("alpha beta gamma " * 20)

    client = _fake_client_with_embeddings([[1.0, 0.0]] * 10)
    rag1 = DoctrineRAG(
        corpus_dir=corpus,
        index_path=tmp_path / "idx.pkl",
        chunk_size_words=30,
        overlap_words=5,
        client=client,
    )
    rag1.build()

    rag2 = DoctrineRAG(
        corpus_dir=corpus,
        index_path=tmp_path / "idx.pkl",
        client=MagicMock(),
    )
    rag2.load()
    assert rag2._chunks == rag1._chunks
    assert rag2._embeddings == rag1._embeddings
