from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db import Chunk, Document, Feedback, IndexJob, User
from app.models.schemas import MeResponse
from app.security import get_current_user

router = APIRouter(tags=["users"])


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return MeResponse(id=user.id, email=user.email, name=user.name)


@router.delete("/user/data")
def delete_user_data(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Chunk).filter(Chunk.user_id == user.id).delete()
    db.query(Document).filter(Document.user_id == user.id).delete()
    db.query(IndexJob).filter(IndexJob.user_id == user.id).delete()
    db.query(Feedback).filter(Feedback.user_id == user.id).update({"user_id": None})
    user.access_token_enc = None
    user.refresh_token_enc = None
    user.token_expiry = None
    db.commit()
    return {"ok": True, "message": "Indexed documents and stored Google tokens were deleted."}
