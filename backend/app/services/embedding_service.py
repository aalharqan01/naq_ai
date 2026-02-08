"""Embedding service — converts text to vectors and stores in ChromaDB."""

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger("dhakira.embedding")

# Lazy-loaded resources
_chroma_client = None
_collection = None
_embedding_fn = None


def _get_embedding_fn():
    """Load the multilingual embedding model."""
    global _embedding_fn
    if _embedding_fn is None:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model,
        )
        logger.info("Embedding model loaded")
    return _embedding_fn


def _get_collection():
    """Get or create the ChromaDB collection."""
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _collection = _chroma_client.get_or_create_collection(
            name=settings.chroma_collection_name,
            embedding_function=_get_embedding_fn(),
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"ChromaDB collection '{settings.chroma_collection_name}' ready "
            f"({_collection.count()} vectors)"
        )
    return _collection


def chunk_text(text: str, doc_id: int, metadata: Optional[dict] = None) -> list[dict]:
    """Split text into overlapping chunks suitable for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        separators=["\n\n", "\n", ".", "،", " ", ""],  # Arabic comma included
    )

    chunks = splitter.split_text(text)
    result = []

    for i, chunk in enumerate(chunks):
        chunk_meta = {
            "document_id": str(doc_id),
            "chunk_index": i,
            "total_chunks": len(chunks),
            **(metadata or {}),
        }
        result.append(
            {
                "id": f"doc{doc_id}_chunk{i}",
                "text": chunk,
                "metadata": chunk_meta,
            }
        )

    return result


def embed_document(doc_id: int, text: str, metadata: Optional[dict] = None) -> int:
    """
    Chunk, embed, and store a document's text in ChromaDB.

    Returns the number of chunks created.
    """
    collection = _get_collection()

    # Remove existing chunks for this document (re-processing)
    existing = collection.get(where={"document_id": str(doc_id)})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        logger.info(f"Removed {len(existing['ids'])} existing chunks for doc {doc_id}")

    chunks = chunk_text(text, doc_id, metadata)

    if not chunks:
        logger.warning(f"No chunks generated for document {doc_id}")
        return 0

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )

    logger.info(f"Embedded document {doc_id}: {len(chunks)} chunks stored")
    return len(chunks)


def search_similar(query: str, top_k: int | None = None, filters: Optional[dict] = None) -> list[dict]:
    """
    Search for chunks most similar to the query.

    Returns list of {id, text, metadata, distance}.
    """
    collection = _get_collection()
    k = top_k or settings.rag_top_k

    query_params = {
        "query_texts": [query],
        "n_results": min(k, collection.count()) if collection.count() > 0 else k,
    }
    if filters:
        query_params["where"] = filters

    if collection.count() == 0:
        return []

    results = collection.query(**query_params)

    output = []
    for i in range(len(results["ids"][0])):
        output.append(
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
            }
        )

    return output


def get_vector_count() -> int:
    """Return total number of vectors in the collection."""
    try:
        return _get_collection().count()
    except Exception:
        return 0
