from typing import Literal

from pydantic import BaseModel, Field


class MeResponse(BaseModel):
    id: int
    email: str
    name: str | None


class IndexStatusResponse(BaseModel):
    status: str
    message: str
    total: int
    processed: int


class IndexRequest(BaseModel):
    mode: Literal["recent_opened", "recent_modified", "owned_by_me", "shared_with_me"] = "recent_opened"


class DocumentResponse(BaseModel):
    id: int
    title: str
    web_url: str
    indexed_at: str


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class Citation(BaseModel):
    document_title: str
    document_url: str
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class FeedbackRequest(BaseModel):
    email: str | None = None
    message: str = Field(min_length=5, max_length=4000)
