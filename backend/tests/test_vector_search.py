from vector_search import VectorKnowledgeSearch


def test_vector_search_finds_malaria():
    searcher = VectorKnowledgeSearch()

    results = searcher.search(
        "What symptoms can malaria cause?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"
    assert results[0]["score"] > 0