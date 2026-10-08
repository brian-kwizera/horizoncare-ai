from knowledge_ingestion import ingest_document


document_id = ingest_document(
    filename="malaria.md",
    title="Malaria",
    source="World Health Organization",
    url="https://www.who.int/health-topics/malaria",
)

print(f"Malaria document ingested with ID: {document_id}")