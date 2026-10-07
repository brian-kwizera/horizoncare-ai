from database import get_connection
from database_setup import initialize_database
from knowledge_ingestion import ingest_document


def test_ingest_malaria_document():
    initialize_database()

    document_id = ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    assert document_id > 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM document_chunks
                WHERE document_id = %s;
                """,
                (document_id,),
            )

            chunk_count = cursor.fetchone()[0]

    assert chunk_count > 0