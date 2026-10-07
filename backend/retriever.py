from vector_search import VectorKnowledgeSearch


class KnowledgeRetriever:
    def __init__(self):
        self.searcher = VectorKnowledgeSearch()

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        return self.searcher.search(
            query,
            top_k=top_k,
        )