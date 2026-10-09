from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    title: str
    publisher: str
    url: str | None = None
    similarity: float = Field(ge=-1.0, le=1.0)


class EvidencePassage(BaseModel):
    chunk_id: str
    filename: str
    content: str
    similarity: float = Field(ge=-1.0, le=1.0)


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceCitation]
    evidence: list[EvidencePassage]