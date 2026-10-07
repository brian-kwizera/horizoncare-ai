from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_service import generate_answer
from knowledge_search import search_knowledge


load_dotenv(override=True)

app = FastAPI(title="HorizonCare AI")


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "HorizonCare AI is running"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        # Search the HorizonCare knowledge base
        results = search_knowledge(request.question)

        # Build context for the AI service
        context = ""

        if results:
            context = "\n\n".join(
                f"Source: {result['filename']}\n"
                f"{result['content']}"
                for result in results[:3]
            )

        # Generate the response
        answer = generate_answer(
            request.question,
            context,
        )

        # Return the sources used
        sources = [
            result["filename"]
            for result in results[:3]
        ]

        return {
            "question": request.question,
            "answer": answer,
            "sources": sources,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI request failed: {str(error)}"
        )