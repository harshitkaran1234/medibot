from pathlib import Path
from typing import Any

from docling.chunking import BaseChunk
from docling_core.types.doc import DocItemLabel, DoclingDocument
from langchain_docling.loader import BaseMetaExtractor

from medibot.core.rbac import Collection, roles_for_collection

HEADING_LABELS = {DocItemLabel.SECTION_HEADER, DocItemLabel.TITLE}


def get_chunk_type(labels: set[DocItemLabel]) -> str:
    # Precedence for mixed chunks: table > code > text.
    # "heading" only when the chunk is nothing but headings.
    if DocItemLabel.TABLE in labels:
        return "table"
    if DocItemLabel.CODE in labels:
        return "code"
    if labels and labels <= HEADING_LABELS:
        return "heading"
    return "text"


class MediBotMetaExtractor(BaseMetaExtractor):
    """Maps a Docling chunk to the assignment's metadata schema (drops the bulky dl_meta)."""

    def extract_chunk_meta(self, file_path: str, chunk: BaseChunk) -> dict[str, Any]:
        path = Path(file_path)
        collection = Collection(path.parent.name)  # folder name == collection name
        doc_items = chunk.meta.doc_items
        headings = chunk.meta.headings or []
        page_numbers = [prov.page_no for item in doc_items for prov in item.prov]

        # Store plain strings in the Qdrant payload, not enum objects
        return {
            "source_document": path.name,
            "collection": collection.value,
            "access_roles": [role.value for role in roles_for_collection(collection)],
            "section_title": headings[-1] if headings else path.stem,
            "chunk_type": get_chunk_type({item.label for item in doc_items}),
            "headings": headings,
            "page_no": min(page_numbers) if page_numbers else None,  # None for markdown
        }

    def extract_dl_doc_meta(self, file_path: str, dl_doc: DoclingDocument) -> dict[str, Any]:
        return {"source_document": Path(file_path).name}
