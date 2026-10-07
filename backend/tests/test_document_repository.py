from database import get_connection
from database_setup import initialize_database
from document_repository import save_document, save_chunk


def test_save_document_and_chunk():
    initialize_database()

    document_id = save_document(
        filename="test.md",
        title="Test Document",
        source="Test Source",
    )

    save_chunk(
        document_id=document_id,
        chunk_id="test.md:0",
        content="This is a test chunk.",
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.filename, c.chunk_id, c.content
                FROM documents d
                JOIN document_chunks c
                    ON c.document_id = d.id
                WHERE d.filename = %s;
                """,
                ("test.md",),
            )

            row = cursor.fetchone()

    assert row == (
        "test.md",
        "test.md:0",
        "This is a test chunk.",
    )