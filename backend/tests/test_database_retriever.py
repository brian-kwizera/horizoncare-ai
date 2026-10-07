from database_retriever import search_database
from knowledge_ingestion import ingest_document


def test_database_retriever():
    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    results = search_database(
        "What are the common symptoms of malaria?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"
    assert results[0]["source"] == "World Health Organization"
    assert results[0]["matches"] > 0