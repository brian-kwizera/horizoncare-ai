import pytest
from pydantic import ValidationError

from response_models import AskResponse, SourceCitation


def test_structured_response_accepts_valid_source():
    response = AskResponse(
        question="What are malaria symptoms?",
        answer="Mock mode is enabled.",
        sources=[
            {
                "title": "Malaria",
                "publisher": "World Health Organization",
                "url": "https://www.who.int/health-topics/malaria",
                "similarity": 0.83,
            }
        ],
        evidence=[
            {
                "chunk_id": "malaria.md:0",
                "filename": "malaria.md",
                "content": "Malaria can cause fever and chills.",
                "similarity": 0.83,
            }
        ],
    )

    assert response.sources[0].title == "Malaria"
    assert response.evidence[0].filename == "malaria.md"


def test_source_rejects_invalid_similarity():
    with pytest.raises(ValidationError):
        SourceCitation(
            title="Malaria",
            publisher="World Health Organization",
            url=None,
            similarity=1.5,
        )