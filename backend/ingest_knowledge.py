from knowledge_ingestion import ingest_all_documents


if __name__ == "__main__":
    print("Scanning and ingesting knowledge documents...")
    document_ids = ingest_all_documents()
    print(
        f"Successfully ingested {len(document_ids)} document(s): {document_ids}"
    )