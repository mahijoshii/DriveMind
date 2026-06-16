from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.ingestion.indexer import index_drive_for_user, latest_job
from app.models.db import Document, IndexJob, User
from app.models.schemas import DocumentResponse, IndexStatusResponse
from app.security import get_current_user

router = APIRouter(prefix="/drive", tags=["drive"])


@router.post("/index")
def start_index(background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = IndexJob(user_id=user.id, status="queued", message="Indexing job queued.", total=0, processed=0)
    db.add(job)
    db.commit()
    background_tasks.add_task(index_drive_for_user, user.id, SessionLocal)
    return {"ok": True, "message": "Indexing started."}


@router.get("/index/status", response_model=IndexStatusResponse)
def index_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = latest_job(db, user.id)
    return IndexStatusResponse(status=job.status, message=job.message, total=job.total, processed=job.processed)


@router.get("/documents", response_model=list[DocumentResponse])
def drive_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.user_id == user.id).order_by(Document.id.asc()).all()
    return [DocumentResponse(id=d.id, title=d.title, web_url=d.web_url, indexed_at=d.indexed_at.isoformat()) for d in docs]
