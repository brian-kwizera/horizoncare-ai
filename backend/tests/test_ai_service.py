from ai_service import generate_answer


def test_mock_mode_returns_question():
    question = "What are the common symptoms of malaria?"

    answer = generate_answer(question)

    assert "local mock mode" in answer
    assert question in answer