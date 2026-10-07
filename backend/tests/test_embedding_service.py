import numpy as np

from embedding_service import EmbeddingService


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)

    return float(
        np.dot(a, b)
        / (np.linalg.norm(a) * np.linalg.norm(b))
    )


def test_embedding_service():
    service = EmbeddingService()

    question = service.embed_query(
        "What symptoms can malaria cause?"
    )

    relevant = service.embed_passage(
        "Malaria can cause fever, chills, headache, and weakness."
    )

    unrelated = service.embed_passage(
        "A football team won a match by scoring three goals."
    )

    assert len(question) == 384
    assert len(relevant) == 384
    assert len(unrelated) == 384

    relevant_similarity = cosine_similarity(
        question,
        relevant,
    )

    unrelated_similarity = cosine_similarity(
        question,
        unrelated,
    )

    assert relevant_similarity > unrelated_similarity