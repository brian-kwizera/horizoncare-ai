from document_loader import load_documents


def test_load_documents():
    documents = load_documents()

    assert len(documents) >= 2

    documents_by_filename = {
        document["filename"]: document
        for document in documents
    }

    assert "malaria.md" in documents_by_filename
    assert "dengue.md" in documents_by_filename

    assert documents_by_filename["malaria.md"]["content"]
    assert documents_by_filename["dengue.md"]["content"]