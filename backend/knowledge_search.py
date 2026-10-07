import re

from document_loader import load_documents


def tokenize(text: str) -> set[str]:
    """Convert text into normalized words."""
    return set(re.findall(r"\b\w+\b", text.lower()))


def search_knowledge(query: str) -> list[dict]:
    query_words = tokenize(query)
    documents = load_documents()

    results = []

    for document in documents:
        content_words = tokenize(document["content"])

        matches = len(query_words & content_words)

        if matches > 0:
            results.append(
                {
                    "filename": document["filename"],
                    "content": document["content"],
                    "matches": matches,
                }
            )

    results.sort(
        key=lambda document: document["matches"],
        reverse=True,
    )

    return results