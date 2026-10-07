from database import get_connection


def save_document(
    filename: str,
    title: str,
    source: str,
) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (filename, title, source)
                VALUES (%s, %s, %s)
                ON CONFLICT (filename)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    source = EXCLUDED.source
                RETURNING id;
                """,
                (filename, title, source),
            )

            document_id = cursor.fetchone()[0]

        connection.commit()

    return document_id


def save_chunk(
    document_id: int,
    chunk_id: str,
    content: str,
) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO document_chunks
                    (document_id, chunk_id, content)
                VALUES (%s, %s, %s)
                ON CONFLICT (chunk_id)
                DO UPDATE SET
                    content = EXCLUDED.content;
                """,
                (document_id, chunk_id, content),
            )

        connection.commit()