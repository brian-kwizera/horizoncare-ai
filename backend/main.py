from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_service import generate_answer
from retriever import KnowledgeRetriever


load_dotenv(override=True)

app = FastAPI(title="HorizonCare AI")
retriever = KnowledgeRetriever()


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
        results = retriever.search(
    request.question,
    top_k=3,
)

        # Build context for the AI service
        context = ""

        if results:
            context = "\n\n".join(
    (
        f"Title: {result['title']}\n"
        f"Publisher: {result['source']}\n"
        f"URL: {result['url']}\n"
        f"Similarity: {result['similarity']:.4f}\n"
        f"Content: {result['content']}"
    )
    for result in results[:3]
)

        # Generate the response
        answer = generate_answer(
            request.question,
            context,
        )

        # Return the sources used
        sources = [
    {
        "title": result["title"],
        "publisher": result["source"],
        "url": result["url"],
        "similarity": round(result["similarity"], 4),
    }
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