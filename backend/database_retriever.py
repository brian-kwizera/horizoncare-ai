from database import get_connection


def search_database(query: str, top_k: int = 3) -> list[dict]:
    query_words = [
        word.lower().strip(".,!?;:\"'()[]")
        for word in query.split()
        if word.strip()
    ]

    if not query_words:
        return []

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    dc.chunk_id,
                    d.filename,
                    d.title,
                    d.source,
                    dc.content
                FROM document_chunks dc
                JOIN documents d
                    ON d.id = dc.document_id;
                """
            )

            rows = cursor.fetchall()

    results = []

    for row in rows:
        chunk_id, filename, title, source, content = row

        content_words = set(
            word.lower().strip(".,!?;:\"'()[]")
            for word in content.split()
        )

        matches = sum(
            1 for word in query_words
            if word in content_words
        )

        if matches > 0:
            results.append(
                {
                    "chunk_id": chunk_id,
                    "filename": filename,
                    "title": title,
                    "source": source,
                    "content": content,
                    "matches": matches,
                }
            )

    results.sort(
        key=lambda result: result["matches"],
        reverse=True,
    )

    return results[:top_k]