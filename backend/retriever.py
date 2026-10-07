from database_retriever import search_database


class KnowledgeRetriever:
    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        return search_database(
            query,
            top_k=top_k,
        )