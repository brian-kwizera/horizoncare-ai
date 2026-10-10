from pgvector_retriever import merge_adjacent_chunks


def make_chunk(
    chunk_id: str,
    content: str,
    similarity: float,
    filename: str = "dengue.md",
) -> dict:
    return {
        "chunk_id": chunk_id,
        "filename": filename,
        "title": filename.removesuffix(".md").title(),
        "source": "World Health Organization",
        "url": "https://example.org/source",
        "content": content,
        "similarity": similarity,
    }


def test_adjacent_chunks_merge_without_duplicate_words():
    results = [
        make_chunk(
            "dengue.md:1",
            "delta epsilon zeta eta theta",
            0.89,
        ),
        make_chunk(
            "dengue.md:0",
            "alpha beta gamma delta epsilon zeta",
            0.79,
        ),
    ]

    merged = merge_adjacent_chunks(results)

    assert len(merged) == 1
    assert merged[0]["chunk_id"] == "dengue.md:0-1"
    assert merged[0]["content"] == (
        "alpha beta gamma delta epsilon zeta eta theta"
    )
    assert merged[0]["similarity"] == 0.89


def test_non_adjacent_chunks_are_not_merged():
    results = [
        make_chunk("dengue.md:0", "First passage.", 0.89),
        make_chunk("dengue.md:2", "Third passage.", 0.75),
    ]

    merged = merge_adjacent_chunks(results)

    assert len(merged) == 2
    assert {item["chunk_id"] for item in merged} == {
        "dengue.md:0",
        "dengue.md:2",
    }