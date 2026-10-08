from ai_service import build_grounded_prompt, generate_answer


def test_no_context_returns_evidence_warning():
    question = "What are the common symptoms of malaria?"

    answer = generate_answer(question)

    assert "does not have enough relevant evidence" in answer

    def test_no_context_returns_evidence_warning():
        answer = generate_answer(
        "What are the symptoms of malaria?",
        context="",
    )

    assert "does not have enough relevant evidence" in answer

    def test_grounded_prompt_contains_question_and_context():
        from ai_service import build_grounded_prompt

    prompt = build_grounded_prompt(
        "What are malaria symptoms?",
        "Malaria can cause fever and chills.",
    )

    assert "What are malaria symptoms?" in prompt
    assert "Malaria can cause fever and chills." in prompt
    assert "Use ONLY the healthcare information" in prompt