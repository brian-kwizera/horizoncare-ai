from document_loader import load_documents


def test_load_documents():
    documents = load_documents()

    assert len(documents) >= 1
    assert documents[0]["filename"] == "malaria.md"
    assert "Malaria" in documents[0]["content"]