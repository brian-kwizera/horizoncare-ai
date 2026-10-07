from typing import TypedDict


class DocumentChunk(TypedDict):
    chunk_id: str
    filename: str
    content: str


def chunk_text(
    text: str,
    max_words: int = 100,
    overlap: int = 20,
) -> list[str]:
    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def chunk_documents(
    documents: list[dict],
    max_words: int = 100,
    overlap: int = 20,
) -> list[DocumentChunk]:
    chunks = []

    for document in documents:
        text_chunks = chunk_text(
            document["content"],
            max_words=max_words,
            overlap=overlap,
        )

        for index, content in enumerate(text_chunks):
            chunks.append(
                {
                    "chunk_id": f"{document['filename']}:{index}",
                    "filename": document["filename"],
                    "content": content,
                }
            )

    return chunks