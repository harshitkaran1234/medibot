"""Parse, chunk and index all MediAssist documents into Qdrant.

Run once before starting the API (first run downloads Docling + embedding models):
    poetry run python scripts/ingest.py
"""

from collections import Counter, defaultdict

from medibot.core.ingestion import ingest


def print_summary(chunks) -> None:
    by_document: dict[str, Counter] = defaultdict(Counter)
    for chunk in chunks:
        by_document[chunk.metadata["source_document"]][chunk.metadata["chunk_type"]] += 1

    print(f"\n{'document':<32} {'collection':<10} chunks  types")
    for chunk in chunks:
        name = chunk.metadata["source_document"]
        if name in by_document:
            types = dict(by_document.pop(name))
            print(
                f"{name:<32} {chunk.metadata['collection']:<10} {sum(types.values()):>6}  {types}"
            )

    print(f"\nTotal chunks: {len(chunks)}")
    tables = [c for c in chunks if c.metadata["chunk_type"] == "table"]
    if tables:
        print("\nSample table chunk:\n" + "-" * 60)
        print(tables[0].metadata)
        print(tables[0].page_content[:600])


if __name__ == "__main__":
    print_summary(ingest(recreate=True))
