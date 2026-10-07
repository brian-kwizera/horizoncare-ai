from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from dotenv import load_dotenv

from ai_service import generate_answer


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
        answer = generate_answer(request.question)

        return {
            "question": request.question,
            "answer": answer
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI request failed: {str(error)}"
        )