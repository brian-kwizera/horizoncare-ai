from document_chunker import chunk_text, chunk_documents


def test_chunk_text():
    text = "one two three four five six"

    chunks = chunk_text(
        text,
        max_words=3,
        overlap=1,
    )

    assert chunks == [
        "one two three",
        "three four five",
        "five six",
    ]


def test_chunk_documents():
    documents = [
        {
            "filename": "malaria.md",
            "content": (
                "Malaria is an infectious disease. "
                "It can cause fever and chills."
            ),
        }
    ]

    chunks = chunk_documents(
        documents,
        max_words=5,
        overlap=1,
    )

    assert len(chunks) > 0
    assert chunks[0]["filename"] == "malaria.md"
    assert chunks[0]["chunk_id"] == "malaria.md:0"