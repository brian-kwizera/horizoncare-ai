from pgvector_retriever import search_vectors


class KnowledgeRetriever:
    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        return search_vectors(
            query,
            top_k=top_k,
        )