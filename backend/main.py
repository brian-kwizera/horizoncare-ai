from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "message": "HorizonCare AI is running"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    return {
        "question": request.question,
        "message": "HorizonCare received your question."
    }