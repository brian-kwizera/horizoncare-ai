from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from database_setup import initialize_database
from knowledge_ingestion import ingest_document
from main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "HorizonCare AI is running"
    }


def test_ask_unrelated_question():
    initialize_database()

    # Ensure the knowledge base contains medical information.
    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
        url="https://www.who.int/health-topics/malaria",
    )

    # Ask a question unrelated to the available medical document.
    response = client.post(
        "/ask",
        json={
            "question": "What are the rules for scoring a football goal?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sources"] == []
    assert data["evidence"] == []
    assert (
        "does not have enough relevant evidence"
        in data["answer"]
    )


def test_ask():
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
        url="https://www.who.int/health-topics/malaria",
    )

    response = client.post(
        "/ask",
        json={
            "question": "What are the common symptoms of malaria?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What are the common symptoms of malaria?"
    assert "answer" in data
    assert "sources" in data
    assert "evidence" in data

    # The mock answer must not pretend to be AI-generated.
    assert "Mock mode is enabled" in data["answer"]
    assert "Malaria is an infectious disease" not in data["answer"]

    # Verify the source metadata.
    assert len(data["sources"]) >= 1

    source = data["sources"][0]

    assert source["title"] == "Malaria"
    assert source["publisher"] == "World Health Organization"
    assert source["url"] == (
        "https://www.who.int/health-topics/malaria"
    )
    assert source["similarity"] >= 0.60

    # Verify evidence is separate from the answer.
    assert len(data["evidence"]) >= 1

    passage = data["evidence"][0]

    assert passage["filename"] == "malaria.md"
    assert passage["content"]
    assert passage["similarity"] >= 0.60


def test_ask_openai_mode_success(monkeypatch):
    """Verify that in OpenAI mode, /ask returns a real AI answer and genuine DB citations."""
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
        url="https://www.who.int/health-topics/malaria",
    )

    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-mock-key")

    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Malaria causes acute fever, chills, and body aches."
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion

    mock_openai_cls = MagicMock(return_value=mock_client)
    import ai_service
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    response = client.post(
        "/ask",
        json={"question": "What are the common symptoms of malaria?"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["answer"] == "Malaria causes acute fever, chills, and body aches."
    assert not data["answer"].startswith("Mock mode is enabled")

    # Sources and evidence must still come from database retrieval
    assert len(data["sources"]) >= 1
    assert data["sources"][0]["title"] == "Malaria"
    assert data["sources"][0]["publisher"] == "World Health Organization"
    assert len(data["evidence"]) >= 1
    assert data["evidence"][0]["filename"] == "malaria.md"


def test_ask_api_error_does_not_leak_secrets(monkeypatch):
    """Verify that internal service errors return safe HTTP 500 details without leaking secrets."""
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
        url="https://www.who.int/health-topics/malaria",
    )

    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-key-999")

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError(
        "Internal exception containing super-secret-key-999"
    )

    mock_openai_cls = MagicMock(return_value=mock_client)
    import ai_service
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    response = client.post(
        "/ask",
        json={"question": "What are the common symptoms of malaria?"},
    )

    assert response.status_code == 500
    assert "super-secret-key-999" not in response.text
    data = response.json()
    assert data["detail"] == "The AI request could not be completed. Please try again later."


def test_ask_citations_come_from_retrieval_not_model(monkeypatch):
    """Verify that even if the AI model outputs hallucinated citations, response sources come strictly from retrieval."""
    initialize_database()

    ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
        url="https://www.who.int/health-topics/malaria",
    )

    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-mock-key")

    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    # Model hallucinating an invented URL and title in its prose answer
    mock_choice.message.content = "According to https://fake-health-site.com, malaria causes chills."
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion

    mock_openai_cls = MagicMock(return_value=mock_client)
    import ai_service
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    response = client.post(
        "/ask",
        json={"question": "What are the common symptoms of malaria?"},
    )

    assert response.status_code == 200
    data = response.json()

    # The structured sources MUST NOT contain the fabricated site
    source_urls = [s["url"] for s in data["sources"]]
    assert "https://fake-health-site.com" not in source_urls
    assert "https://www.who.int/health-topics/malaria" in source_urls