from document_chunker import chunk_documents
from document_loader import load_documents
from document_repository import save_chunk, save_document


def ingest_document(
    filename: str,
    title: str,
    source: str,
) -> int:
    documents = load_documents()

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

    document_id = save_document(
        filename=filename,
        title=title,
        source=source,
    )

    chunks = chunk_documents([document])

    for chunk in chunks:
        save_chunk(
            document_id=document_id,
            chunk_id=chunk["chunk_id"],
            content=chunk["content"],
        )

    return document_id