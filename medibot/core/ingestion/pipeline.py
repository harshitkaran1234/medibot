import uuid
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from langchain_core.documents import Document
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from qdrant_client import QdrantClient
from transformers import AutoTokenizer

from medibot.common import config, logger
from medibot.core.ingestion.metadata import MediBotMetaExtractor
from medibot.core.rbac import Collection
from medibot.core.vector_store import create_collection, get_vector_store

SUPPORTED_SUFFIXES = {".pdf", ".md"}


def find_documents(data_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in Path(data_dir).rglob("*")
        if path.suffix.lower() in SUPPORTED_SUFFIXES and path.parent.name in list(Collection)
    )


def build_chunker() -> HybridChunker:
    # Same tokenizer as the embedding model, so "fits in max_tokens" means the same
    # thing to the chunker and to the embedder (no silent truncation).
    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(config.EMBEDDING_MODEL),
        max_tokens=config.CHUNK_MAX_TOKENS,
    )
    return HybridChunker(tokenizer=tokenizer, merge_peers=True)


def load_chunks(paths: list[Path]) -> list[Document]:
    converter = DocumentConverter()  # shared so layout/table models load only once
    chunker = build_chunker()
    meta_extractor = MediBotMetaExtractor()

    chunks: list[Document] = []
    for path in paths:
        logger.info(f"Parsing {path}")
        loader = DoclingLoader(
            file_path=str(path),
            converter=converter,
            export_type=ExportType.DOC_CHUNKS,
            chunker=chunker,
            meta_extractor=meta_extractor,
        )
        # page_content is chunker.contextualize(chunk): heading path + chunk text
        docs = loader.load()
        for index, doc in enumerate(docs):
            doc.metadata["chunk_index"] = index
        chunks.extend(docs)
        logger.info(f"  -> {len(docs)} chunks")
    return chunks


def point_id(doc: Document) -> str:
    # Deterministic: re-ingesting the same chunk overwrites it instead of duplicating it
    key = f"{doc.metadata['source_document']}:{doc.metadata['chunk_index']}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def ingest(recreate: bool = True) -> list[Document]:
    chunks = load_chunks(find_documents(config.DATA_DIR))

    client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY or None)
    create_collection(client, recreate=recreate)
    vector_store = get_vector_store(client)

    logger.info(f"Embedding and upserting {len(chunks)} chunks (dense + sparse)")
    vector_store.add_documents(chunks, ids=[point_id(doc) for doc in chunks])
    client.close()
    return chunks
