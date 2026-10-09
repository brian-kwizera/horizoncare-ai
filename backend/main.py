from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_service import generate_answer
from retriever import KnowledgeRetriever


load_dotenv()

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
            detail="Question cannot be empty.",
        )

    try:
        results = retriever.search(
            request.question,
            top_k=3,
        )

        # Build context for the answer generator.
        context = "\n\n".join(
            (
                f"Title: {result['title']}\n"
                f"Publisher: {result['source']}\n"
                f"URL: {result.get('url') or 'Not provided'}\n"
                f"Content: {result['content']}"
            )
            for result in results
        )

        answer = generate_answer(
            request.question,
            context,
        )

        # Keep retrieved evidence separate from the answer.
        evidence = [
            {
                "chunk_id": result["chunk_id"],
                "filename": result["filename"],
                "content": result["content"],
                "similarity": round(
                    float(result["similarity"]), 4
                ),
            }
            for result in results
        ]

        # Deduplicate citations when multiple chunks come
        # from the same source document.
        source_map = {}

        for result in results:
            source_key = (
                result.get("url") or result["filename"]
            )

            if source_key not in source_map:
                source_map[source_key] = {
                    "title": result["title"],
                    "publisher": result["source"],
                    "url": result.get("url"),
                    "similarity": round(
                        float(result["similarity"]), 4
                    ),
                }

        return {
            "question": request.question,
            "answer": answer,
            "sources": list(source_map.values()),
            "evidence": evidence,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI request failed: {error}",
        )