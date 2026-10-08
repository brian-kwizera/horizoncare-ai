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

    embedding = [0.1] * 384

    save_chunk(
        document_id=document_id,
        chunk_id="test.md:0",
        content="This is a test chunk.",
        embedding=embedding,
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    d.filename,
                    c.chunk_id,
                    c.content,
                    c.embedding::text
                FROM documents d
                JOIN document_chunks c
                    ON c.document_id = d.id
                WHERE d.filename = %s;
                """,
                ("test.md",),
            )

            row = cursor.fetchone()

    assert row[0] == "test.md"
    assert row[1] == "test.md:0"
    assert row[2] == "This is a test chunk."
    assert row[3].startswith("[0.1")