from database import get_connection


def save_document(
    filename: str,
    title: str,
    source: str,
    url: str | None = None,
) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents
                    (filename, title, source, url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (filename)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    source = EXCLUDED.source,
                    url = EXCLUDED.url
                RETURNING id;
                """,
                (filename, title, source, url),
            )

            document_id = cursor.fetchone()[0]

        connection.commit()

    return document_id


def save_chunk(
    document_id: int,
    chunk_id: str,
    content: str,
    embedding: list[float] | None = None,
) -> None:
    embedding_value = (
        str(embedding)
        if embedding is not None
        else None
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO document_chunks
                    (document_id, chunk_id, content, embedding)
                VALUES (%s, %s, %s, %s::vector)
                ON CONFLICT (chunk_id)
                DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding;
                """,
                (
                    document_id,
                    chunk_id,
                    content,
                    embedding_value,
                ),
            )

        connection.commit()