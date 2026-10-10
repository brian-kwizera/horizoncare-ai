from database import get_connection
from embedding_service import EmbeddingService


DEFAULT_MIN_SIMILARITY = 0.72
MAX_CHUNK_OVERLAP_WORDS = 20


def vector_literal(vector: list[float]) -> str:
    """Convert a Python vector into pgvector's text format."""
    return "[" + ",".join(str(value) for value in vector) + "]"


def _chunk_position(chunk_id: str) -> tuple[str, int] | None:
    """Extract the filename and chunk index from a chunk ID."""
    filename, separator, index_text = chunk_id.rpartition(":")

    if not separator:
        return None

    try:
        return filename, int(index_text)
    except ValueError:
        return None


def _merge_overlapping_text(first: str, second: str) -> str:
    """Join adjacent chunks without repeating overlapping words."""
    first_words = first.split()
    second_words = second.split()

    max_overlap = min(
        MAX_CHUNK_OVERLAP_WORDS,
        len(first_words),
        len(second_words),
    )

    for overlap in range(max_overlap, 2, -1):
        if first_words[-overlap:] == second_words[:overlap]:
            return " ".join(first_words + second_words[overlap:])

    return f"{first.strip()} {second.strip()}".strip()


def merge_adjacent_chunks(results: list[dict]) -> list[dict]:
    """Merge consecutive chunks from the same document."""
    chunks_by_filename: dict[str, list[tuple[int, dict]]] = {}
    unindexed_results = []

    for result in results:
        position = _chunk_position(result.get("chunk_id", ""))

        if position is None:
            unindexed_results.append(dict(result))
            continue

        filename, index = position
        chunks_by_filename.setdefault(filename, []).append(
            (index, dict(result))
        )

    merged_results = list(unindexed_results)

    for filename, indexed_chunks in chunks_by_filename.items():
        indexed_chunks.sort(key=lambda item: item[0])

        if not indexed_chunks:
            continue

        start_index, current = indexed_chunks[0]
        end_index = start_index

        for index, next_chunk in indexed_chunks[1:]:
            if index == end_index:
                continue

            if index == end_index + 1:
                current["content"] = _merge_overlapping_text(
                    current["content"],
                    next_chunk["content"],
                )
                current["similarity"] = max(
                    float(current["similarity"]),
                    float(next_chunk["similarity"]),
                )
                end_index = index
                current["chunk_id"] = (
                    f"{filename}:{start_index}-{end_index}"
                )
            else:
                merged_results.append(current)
                start_index = index
                end_index = index
                current = dict(next_chunk)

        merged_results.append(current)

    merged_results.sort(
        key=lambda result: float(result["similarity"]),
        reverse=True,
    )

    return merged_results


def _load_adjacent_chunks(
    results: list[dict],
    query_vector: str,
) -> list[dict]:
    """Load neighboring chunks as context for qualifying search results."""
    matched_ids = {result["chunk_id"] for result in results}
    neighbor_ids = set()

    for result in results:
        position = _chunk_position(result["chunk_id"])

        if position is None:
            continue

        filename, index = position

        if index > 0:
            neighbor_ids.add(f"{filename}:{index - 1}")

        neighbor_ids.add(f"{filename}:{index + 1}")

    neighbor_ids.difference_update(matched_ids)

    if not neighbor_ids:
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
                    d.url,
                    dc.content,
                    1 - (dc.embedding <=> %s::vector)
                        AS similarity
                FROM document_chunks dc
                JOIN documents d
                    ON d.id = dc.document_id
                WHERE dc.embedding IS NOT NULL
                  AND dc.chunk_id = ANY(%s);
                """,
                (query_vector, sorted(neighbor_ids)),
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


def search_vectors(
    query: str,
    top_k: int = 3,
    min_similarity: float = DEFAULT_MIN_SIMILARITY,
) -> list[dict]:
    if not query.strip() or top_k <= 0:
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

    matched_results = [
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

    if not matched_results:
        return []

    # Adjacent chunks provide context but do not independently
    # qualify as relevant matches.
    neighbors = _load_adjacent_chunks(
        matched_results,
        query_vector,
    )

    combined = {
        result["chunk_id"]: result
        for result in matched_results
    }

    for neighbor in neighbors:
        combined.setdefault(neighbor["chunk_id"], neighbor)

    return merge_adjacent_chunks(list(combined.values()))