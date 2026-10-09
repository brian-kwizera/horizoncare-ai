import os

from openai import OpenAI


def build_grounded_prompt(
    question: str,
    context: str,
) -> str:
    return f"""
Use ONLY the healthcare information provided in the
KNOWLEDGE CONTEXT below to answer the user's question.

Rules:
- Do not invent information that is not supported by the context.
- If the context does not contain enough information to answer,
  clearly say that the available knowledge base does not provide
  enough information.
- Do not diagnose the patient.
- Do not prescribe medication.
- Do not replace a qualified healthcare professional.

KNOWLEDGE CONTEXT:
{context}

USER QUESTION:
{question}
""".strip()


def generate_answer(
    question: str,
    context: str = "",
) -> str:
    """
    Generate an evidence-grounded answer.

    AI_MODE=mock   -> local evidence response
    AI_MODE=openai -> use OpenAI API
    """

    mode = os.getenv("AI_MODE", "mock").lower()

    if not context.strip():
        return (
            "HorizonCare does not have enough relevant evidence "
            "in its knowledge base to answer this question."
        )

    if mode == "mock":
     return (
        "Mock mode is enabled. Relevant evidence was retrieved, "
        "but no AI-generated summary was produced."
    )

    if mode == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
            instructions=(
                "You are HorizonCare AI, a healthcare information "
                "assistant prototype. Answer only from the supplied "
                "knowledge context. Be transparent when the evidence "
                "is insufficient. Do not diagnose, prescribe, or "
                "replace a qualified healthcare professional."
            ),
            input=build_grounded_prompt(
                question,
                context,
            ),
        )

        return response.output_text

    raise ValueError(
        f"Unsupported AI_MODE: {mode}. "
        "Use 'mock' or 'openai'."
    )