from fastembed import TextEmbedding


MODEL_NAME = "BAAI/bge-small-en-v1.5"


class EmbeddingService:
    def __init__(self):
        self.model = TextEmbedding(model_name=MODEL_NAME)

    def embed_query(self, text: str) -> list[float]:
        vector = next(
            self.model.query_embed([text])
        )

        return vector.tolist()

    def embed_passage(self, text: str) -> list[float]:
        vector = next(
            self.model.passage_embed([text])
        )

        return vector.tolist()