"""Build the doctrine RAG index.

Reads every .txt file under docs/corpus/, embeds the chunks with the
OpenAI embedding API, and writes the result to .cache/rag_index.pkl.

Run once after changing the corpus, or whenever the cache is missing.

Requires OPENAI_API_KEY in the environment.
"""

from pathlib import Path

from msg.rag import DoctrineRAG


def main() -> None:
    here = Path(__file__).resolve().parents[1]
    corpus = here / "docs" / "corpus"
    index = here / ".cache" / "rag_index.pkl"

    rag = DoctrineRAG(corpus_dir=corpus, index_path=index)
    n = rag.build()
    size_kb = index.stat().st_size / 1024
    print(f"indexed {n} chunks from {corpus}")
    print(f"wrote {index} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
