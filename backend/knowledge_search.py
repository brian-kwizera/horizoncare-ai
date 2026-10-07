import re

from document_chunker import chunk_documents
from document_loader import load_documents


def tokenize(text: str) -> set[str]:
    """Convert text into normalized words."""
    return set(re.findall(r"\b\w+\b", text.lower()))


def search_knowledge(query: str) -> list[dict]:
    query_words = tokenize(query)

    documents = load_documents()

    chunks = chunk_documents(
        documents,
        max_words=100,
        overlap=20,
    )

    results = []

    for chunk in chunks:
        content_words = tokenize(chunk["content"])

        matches = len(query_words & content_words)

        if matches > 0:
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "filename": chunk["filename"],
                    "content": chunk["content"],
                    "matches": matches,
                }
            )

    results.sort(
        key=lambda result: result["matches"],
        reverse=True,
    )

    return results