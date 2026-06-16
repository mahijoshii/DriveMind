from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db import Feedback
from app.models.schemas import FeedbackRequest
from app.security import get_current_user

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
def submit_feedback(payload: FeedbackRequest, request: Request, db: Session = Depends(get_db)):
    user = None
    try:
        user = get_current_user(request, db)
    except Exception:
        user = None
    db.add(Feedback(user_id=user.id if user else None, email=payload.email, message=payload.message))
    db.commit()
    return {"ok": True, "message": "Thanks for helping improve DriveMind."}
