from database import get_connection
from embedding_service import EmbeddingService


DEFAULT_MIN_SIMILARITY = 0.60


def vector_literal(vector: list[float]) -> str:
    """Convert a Python vector into pgvector's text format."""
    return "[" + ",".join(str(value) for value in vector) + "]"


def search_vectors(
    query: str,
    top_k: int = 3,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
) -> list[dict]:
    if not query.strip():
        return []

    embedding_service = EmbeddingService()

    query_embedding = embedding_service.embed_query(query)
    query_vector = vector_literal(query_embedding)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    dc.chunk_id,
                    d.filename,
                    d.title,
                    d.source,
                    d.url,
                    dc.content,
                    1 - (dc.embedding <=> %s::vector)
                        AS similarity
                FROM document_chunks dc
                JOIN documents d
                    ON d.id = dc.document_id
                WHERE dc.embedding IS NOT NULL
                  AND 1 - (dc.embedding <=> %s::vector) >= %s
                ORDER BY dc.embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_vector,
                    query_vector,
                    min_similarity,
                    query_vector,
                    top_k,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "chunk_id": row[0],
            "filename": row[1],
            "title": row[2],
            "source": row[3],
            "url": row[4],
            "content": row[5],
            "similarity": float(row[6]),
        }
        for row in rows
    ]