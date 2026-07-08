from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.providers import get_ai_provider
from app.database import get_db
from app.models.db import User
from app.models.schemas import Citation, QueryRequest, QueryResponse
from app.retrieval.search import best_excerpt, retrieve_chunks
from app.security import get_current_user
from app.utils.rate_limit import InMemoryRateLimiter

router = APIRouter(tags=["query"])
rate_limit = InMemoryRateLimiter(limit=30, window_seconds=60)


@router.post("/query", response_model=QueryResponse, dependencies=[Depends(rate_limit)])
def query(payload: QueryRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    limit = 10 if payload.document_id else 5
    matches = retrieve_chunks(db, user.id, payload.question, limit=limit, document_id=payload.document_id)
    citations = [
        Citation(
            document_title=chunk.document.title,
            document_url=chunk.document.web_url,
            excerpt=best_excerpt(payload.question, chunk.content),
            score=round(float(score), 4),
        )
        for chunk, score in matches
    ]
    answer = get_ai_provider().answer(payload.question, citations)
    return QueryResponse(answer=answer, citations=citations)
