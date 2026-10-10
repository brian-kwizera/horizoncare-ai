from knowledge_ingestion import ingest_document


documents = [
    {
        "filename": "malaria.md",
        "title": "Malaria",
        "source": "World Health Organization",
        "url": "https://www.who.int/health-topics/malaria",
    },
    {
        "filename": "dengue.md",
        "title": "Dengue",
        "source": "World Health Organization",
        "url": (
            "https://www.who.int/en/news-room/fact-sheets/"
            "detail/dengue-and-severe-dengue"
        ),
    },
]

for document in documents:
    document_id = ingest_document(**document)

    print(
        f"Ingested {document['filename']} "
        f"with document ID: {document_id}"
    )