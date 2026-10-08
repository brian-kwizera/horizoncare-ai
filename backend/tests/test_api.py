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
    response = client.post(
        "/ask",
        json={
            "question": "What are the rules for scoring a football goal?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["sources"] == []
    assert "does not have enough relevant evidence" in data["answer"]


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

    source = data["sources"][0]

    assert source["title"] == "Malaria"
    assert source["publisher"] == "World Health Organization"
    assert source["url"] == (
        "https://www.who.int/health-topics/malaria"
    )
    assert source["similarity"] >= 0.60