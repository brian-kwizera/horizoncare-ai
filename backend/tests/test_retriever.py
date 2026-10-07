from retriever import KnowledgeRetriever
from database_setup import initialize_database
from knowledge_ingestion import ingest_document


def test_retriever_finds_malaria():
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    retriever = KnowledgeRetriever()

    results = retriever.search(
        "What symptoms can malaria cause?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"