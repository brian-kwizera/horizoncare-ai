from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from document_chunker import chunk_documents
from document_loader import load_documents


class VectorKnowledgeSearch:
    def __init__(
        self,
        max_words: int = 100,
        overlap: int = 20,
    ):
        documents = load_documents()

        self.chunks = chunk_documents(
            documents,
            max_words=max_words,
            overlap=overlap,
        )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
        )

        if self.chunks:
            texts = [
                chunk["content"]
                for chunk in self.chunks
            ]

            self.matrix = self.vectorizer.fit_transform(texts)
        else:
            self.matrix = None

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        if not query.strip() or not self.chunks:
            return []

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.matrix,
        )[0]

        ranked_indexes = similarities.argsort()[::-1]

        results = []

        for index in ranked_indexes[:top_k]:
            score = float(similarities[index])

            if score <= 0:
                continue

            chunk = self.chunks[index]

            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "filename": chunk["filename"],
                    "content": chunk["content"],
                    "score": score,
                }
            )

        return results