from functools import lru_cache

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models

from medibot.common import config

DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"

# LangChain nests our fields under "metadata" in the payload, so filters and
# payload indexes must use these dotted keys.
ACCESS_ROLES_KEY = "metadata.access_roles"
COLLECTION_KEY = "metadata.collection"


def create_collection(client: QdrantClient, recreate: bool = False) -> None:
    name = config.QDRANT_COLLECTION
    if client.collection_exists(name):
        if not recreate:
            return
        client.delete_collection(name)

    client.create_collection(
        collection_name=name,
        vectors_config={
            DENSE_VECTOR_NAME: models.VectorParams(
                size=config.EMBEDDING_DIM, distance=models.Distance.COSINE
            )
        },
        sparse_vectors_config={
            # BM25's IDF part needs corpus-wide statistics, so Qdrant computes it server-side
            SPARSE_VECTOR_NAME: models.SparseVectorParams(modifier=models.Modifier.IDF)
        },
    )
    for key in (ACCESS_ROLES_KEY, COLLECTION_KEY):
        client.create_payload_index(
            collection_name=name,
            field_name=key,
            field_schema=models.PayloadSchemaType.KEYWORD,
        )


@lru_cache
def get_dense_embedding() -> FastEmbedEmbeddings:
    # Cached: model loading is the slow part, so both stores share one instance
    return FastEmbedEmbeddings(model_name=config.EMBEDDING_MODEL)


@lru_cache
def get_sparse_embedding() -> FastEmbedSparse:
    return FastEmbedSparse(model_name=config.SPARSE_MODEL)


def get_vector_store(client: QdrantClient) -> QdrantVectorStore:
    """Hybrid store: dense + BM25 prefetches fused with RRF in one Qdrant query."""
    return QdrantVectorStore(
        client=client,
        collection_name=config.QDRANT_COLLECTION,
        embedding=get_dense_embedding(),
        sparse_embedding=get_sparse_embedding(),
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name=DENSE_VECTOR_NAME,
        sparse_vector_name=SPARSE_VECTOR_NAME,
    )


def get_dense_vector_store(client: QdrantClient) -> QdrantVectorStore:
    """Dense-only baseline on the same collection, used to compare against hybrid."""
    return QdrantVectorStore(
        client=client,
        collection_name=config.QDRANT_COLLECTION,
        embedding=get_dense_embedding(),
        retrieval_mode=RetrievalMode.DENSE,
        vector_name=DENSE_VECTOR_NAME,
    )
