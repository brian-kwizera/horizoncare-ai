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


def delete_chunks_by_document_id(document_id: int, cursor=None) -> None:
    """Delete all chunks belonging to a document."""
    if cursor is not None:
        cursor.execute(
            "DELETE FROM document_chunks WHERE document_id = %s;",
            (document_id,),
        )
        return

    with get_connection() as connection:
        with connection.cursor() as cur:
            cur.execute(
                "DELETE FROM document_chunks WHERE document_id = %s;",
                (document_id,),
            )
        connection.commit()


def save_document_and_chunks(
    filename: str,
    title: str,
    source: str,
    url: str | None,
    chunks: list[dict],
) -> int:
    """
    Atomically upsert the document and replace its chunks within a single transaction.
    If an error occurs, the transaction rolls back, leaving prior chunks intact.
    """
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

            cursor.execute(
                "DELETE FROM document_chunks WHERE document_id = %s;",
                (document_id,),
            )

            for chunk in chunks:
                embedding = chunk.get("embedding")
                embedding_value = (
                    str(embedding)
                    if embedding is not None
                    else None
                )
                cursor.execute(
                    """
                    INSERT INTO document_chunks
                        (document_id, chunk_id, content, embedding)
                    VALUES (%s, %s, %s, %s::vector);
                    """,
                    (
                        document_id,
                        chunk["chunk_id"],
                        chunk["content"],
                        embedding_value,
                    ),
                )

        connection.commit()

    return document_id