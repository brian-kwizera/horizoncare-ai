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
    assert results[0]["similarity"] >= 0.60


def test_pgvector_rejects_unrelated_question():
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    results = search_vectors(
        "What are the rules for scoring a football goal?"
    )

    assert results == []


def test_malaria_query_excludes_dengue_chunks():
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
        url="https://www.who.int/health-topics/malaria",
    )

    ingest_document(
        filename="dengue.md",
        title="Dengue",
        source="World Health Organization",
        url=(
            "https://www.who.int/en/news-room/fact-sheets/"
            "detail/dengue-and-severe-dengue"
        ),
    )

    results = search_vectors(
        "What are the common symptoms of malaria?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"
    assert all(
        result["filename"] == "malaria.md"
        for result in results
    )
    assert all(
        result["similarity"] >= 0.72
        for result in results
    )