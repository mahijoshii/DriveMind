from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db import Document, User
from app.models.schemas import DocumentResponse
from app.security import get_current_user

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=list[DocumentResponse])
def documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == user.id).order_by(Document.id.asc()).all()
    return [DocumentResponse(id=d.id, title=d.title, web_url=d.web_url, indexed_at=d.indexed_at.isoformat()) for d in docs]
