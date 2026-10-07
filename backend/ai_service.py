import os

from openai import OpenAI


def generate_answer(
    question: str,
    context: str = "",
) -> str:
    """
    Generate an answer using the configured AI mode.

    AI_MODE=mock  -> local response, no API call
    AI_MODE=openai -> use OpenAI API
    """

    mode = os.getenv("AI_MODE", "mock").lower()

    if mode == "mock":
        if context:
            return (
                "HorizonCare found relevant information in its "
                "knowledge base.\n\n"
                f"Question: {question}\n\n"
                f"Retrieved information:\n{context}"
            )

        return (
            "HorizonCare is currently running in local mock mode. "
            "No relevant knowledge was found.\n\n"
            f"Your question was: {question}"
        )

    if mode == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        client = OpenAI(api_key=api_key)

        prompt = question

        if context:
            prompt = (
                "Use the following retrieved healthcare information "
                "as context when answering the user's question.\n\n"
                f"CONTEXT:\n{context}\n\n"
                f"QUESTION:\n{question}"
            )

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
            instructions=(
                "You are HorizonCare AI, a healthcare information "
                "assistant prototype. Provide clear general health "
                "information. Do not claim to diagnose a patient, "
                "prescribe medication, or replace a qualified "
                "healthcare professional. Be transparent when the "
                "provided context is insufficient."
            ),
            input=prompt,
        )

        return response.output_text

    raise ValueError(
        f"Unsupported AI_MODE: {mode}. "
        "Use 'mock' or 'openai'."
    )