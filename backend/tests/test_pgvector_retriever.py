from database_setup import initialize_database
from knowledge_ingestion import ingest_document
from pgvector_retriever import search_vectors


def test_pgvector_finds_malaria():
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    results = search_vectors(
        "What symptoms can malaria cause?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"
    assert results[0]["similarity"] > 0