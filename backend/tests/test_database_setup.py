from database import get_connection
from database_setup import initialize_database


def test_database_schema():
    initialize_database()

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('documents', 'document_chunks')
                ORDER BY table_name;
                """
            )

            tables = [row[0] for row in cursor.fetchall()]

    assert tables == ["document_chunks", "documents"]