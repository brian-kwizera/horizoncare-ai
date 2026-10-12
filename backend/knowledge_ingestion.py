from pathlib import Path

from document_chunker import chunk_documents
from document_loader import KnowledgeMetadataError, load_documents
import document_repository
from embedding_service import EmbeddingService


def ingest_document(
    filename: str,
    title: str | None = None,
    source: str | None = None,
    url: str | None = None,
    knowledge_dir: Path | None = None,
) -> int:
    documents = load_documents(knowledge_dir=knowledge_dir)

    document = next(
        (
            item
            for item in documents
            if item["filename"] == filename
        ),
        None,
    )

    if document is None:
        raise FileNotFoundError(
            f"Knowledge document not found: {filename}"
        )

    metadata = document.get("metadata") or {}

    resolved_title = title if title is not None else metadata.get("title")
    resolved_source = source if source is not None else metadata.get("publisher")
    resolved_url = url if url is not None else metadata.get("source_url")

    if not resolved_title or not resolved_source:
        raise KnowledgeMetadataError(
            f"Missing required metadata for document '{filename}': title and source/publisher are required."
        )

    # 1. Chunk and compute embeddings before touching the database.
    chunks = chunk_documents([document])
    embedding_service = EmbeddingService()

    chunks_with_embeddings = []
    for chunk in chunks:
        embedding = embedding_service.embed_passage(
            chunk["content"]
        )
        chunks_with_embeddings.append(
            {
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "embedding": embedding,
            }
        )

    # 2. Atomically upsert document and replace chunks in a single transaction.
    document_id = document_repository.save_document_and_chunks(
        filename=filename,
        title=resolved_title,
        source=resolved_source,
        url=resolved_url,
        chunks=chunks_with_embeddings,
    )

    return document_id


def ingest_all_documents(
    knowledge_dir: Path | None = None,
) -> list[int]:
    documents = load_documents(knowledge_dir=knowledge_dir)
    ingested_ids = []

    for document in documents:
        document_id = ingest_document(
            filename=document["filename"],
            knowledge_dir=knowledge_dir,
        )
        ingested_ids.append(document_id)

    return ingested_ids