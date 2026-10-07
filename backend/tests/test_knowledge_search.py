from knowledge_search import search_knowledge


def test_search_finds_malaria_document():
    results = search_knowledge(
        "What are the common symptoms of malaria?"
    )
    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"
    assert results[0]["matches"] > 0