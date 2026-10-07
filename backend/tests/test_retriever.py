from retriever import KnowledgeRetriever


def test_retriever_finds_malaria():
    retriever = KnowledgeRetriever()

    results = retriever.search(
        "What symptoms can malaria cause?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"