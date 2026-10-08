from pgvector_retriever import (
    DEFAULT_MIN_SIMILARITY,
    search_vectors,
)


class KnowledgeRetriever:
    def search(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = DEFAULT_MIN_SIMILARITY,
    ) -> list[dict]:
        return search_vectors(
            query,
            top_k=top_k,
            min_similarity=min_similarity,
        )