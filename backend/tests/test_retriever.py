from database_setup import initialize_database
from knowledge_ingestion import ingest_document
from retriever import KnowledgeRetriever


def test_retriever_finds_malaria_semantically():
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    retriever = KnowledgeRetriever()

    results = retriever.search(
        "What signs might a person experience after infection?"
    )

    assert len(results) >= 1
    assert results[0]["filename"] == "malaria.md"
    assert results[0]["similarity"] > 0