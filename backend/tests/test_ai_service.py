from unittest.mock import MagicMock
import pytest

import ai_service
from ai_service import build_grounded_prompt, generate_answer


def test_no_context_returns_evidence_warning():
    question = "What are the common symptoms of malaria?"
    answer = generate_answer(question)
    assert "does not have enough relevant evidence" in answer


def test_empty_context_returns_evidence_warning():
    answer = generate_answer(
        "What are the symptoms of malaria?",
        context="",
    )
    assert "does not have enough relevant evidence" in answer


def test_grounded_prompt_contains_question_and_context():
    prompt = build_grounded_prompt(
        "What are malaria symptoms?",
        "Malaria can cause fever and chills.",
    )
    assert "What are malaria symptoms?" in prompt
    assert "Malaria can cause fever and chills." in prompt
    assert "Use ONLY the healthcare information" in prompt
    assert "Do not diagnose the patient" in prompt
    assert "Do not prescribe medication" in prompt


def test_generate_answer_mock_mode(monkeypatch):
    monkeypatch.setenv("AI_MODE", "mock")
    answer = generate_answer(
        "What are the symptoms of malaria?",
        context="Malaria causes fever and headache.",
    )
    assert "Mock mode is enabled" in answer


def test_generate_answer_empty_context_does_not_call_openai(monkeypatch):
    """Ensure empty context short-circuits before OpenAI initialization or API calls."""
    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-mock")

    # If OpenAI is initialized, this mock will fail the test
    mock_openai_cls = MagicMock(side_effect=AssertionError("OpenAI client should not be called"))
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    answer = generate_answer(
        "What are the symptoms of malaria?",
        context="",
    )

    assert "does not have enough relevant evidence" in answer
    mock_openai_cls.assert_not_called()


def test_generate_answer_missing_api_key(monkeypatch):
    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        generate_answer(
            "What are the symptoms of malaria?",
            context="Some valid context.",
        )

    assert "OPENAI_API_KEY is not configured" in str(exc_info.value)


def test_generate_answer_openai_success(monkeypatch):
    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-mock")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Malaria symptoms include fever, chills, and headache."
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion

    mock_openai_cls = MagicMock(return_value=mock_client)
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    answer = generate_answer(
        "What are malaria symptoms?",
        context="Malaria causes fever, chills, and headache.",
    )

    assert answer == "Malaria symptoms include fever, chills, and headache."
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"
    assert any("Malaria causes fever" in m["content"] for m in call_kwargs["messages"])


def test_generate_answer_openai_responses_fallback(monkeypatch):
    """Verify fallback to client.responses.create if chat.completions is absent."""
    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-mock")

    mock_client = MagicMock(spec=["responses"])
    mock_response = MagicMock()
    mock_response.output_text = "Generated from responses API."
    mock_client.responses.create.return_value = mock_response

    mock_openai_cls = MagicMock(return_value=mock_client)
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    answer = generate_answer(
        "What are malaria symptoms?",
        context="Malaria causes fever.",
    )

    assert answer == "Generated from responses API."
    mock_client.responses.create.assert_called_once()


def test_generate_answer_openai_api_error(monkeypatch):
    monkeypatch.setenv("AI_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-mock")

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("Rate limit exceeded")

    mock_openai_cls = MagicMock(return_value=mock_client)
    monkeypatch.setattr(ai_service, "OpenAI", mock_openai_cls)

    with pytest.raises(RuntimeError) as exc_info:
        generate_answer(
            "What are malaria symptoms?",
            context="Malaria causes fever.",
        )

    assert "Rate limit exceeded" in str(exc_info.value)


def test_generate_answer_unsupported_mode(monkeypatch):
    monkeypatch.setenv("AI_MODE", "invalid_mode")

    with pytest.raises(ValueError) as exc_info:
        generate_answer("Question?", context="Context")

    assert "Unsupported AI_MODE" in str(exc_info.value)