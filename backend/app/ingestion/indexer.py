import logging

from sqlalchemy.orm import Session

from app.embeddings.providers import dumps_vector, get_embedding_provider
from app.google.drive import extract_doc_text, filter_label, list_google_docs
from app.ingestion.chunker import chunk_text
from app.models.db import Chunk, Document, IndexJob, User, utcnow

logger = logging.getLogger(__name__)


def latest_job(db: Session, user_id: int) -> IndexJob:
    job = db.query(IndexJob).filter(IndexJob.user_id == user_id).order_by(IndexJob.id.desc()).first()
    if not job:
        job = IndexJob(user_id=user_id, status="idle", message="Drive has not been indexed yet.")
        db.add(job)
        db.commit()
        db.refresh(job)
    return job


def index_drive_for_user(user_id: int, session_factory, mode: str = "recent_opened") -> None:
    db: Session = session_factory()
    try:
        label = filter_label(mode)
        user = db.get(User, user_id)
        if not user:
            return
        job = latest_job(db, user_id)
        job.status = "running"
        job.message = f"Finding Google Docs {label} in Drive."
        job.processed = 0
        job.total = 0
        job.updated_at = utcnow()
        db.commit()

        files = list_google_docs(user, db, mode)
        job.total = len(files)
        job.message = f"Found {len(files)} Google Docs {label}."
        db.commit()

        db.query(Chunk).filter(Chunk.user_id == user_id).delete()
        db.query(Document).filter(Document.user_id == user_id).delete()
        db.commit()

        embedder = get_embedding_provider()
        for file in files:
            try:
                text = extract_doc_text(user, db, file["id"])
                chunks = chunk_text(text)
                doc = Document(
                    user_id=user_id,
                    google_file_id=file["id"],
                    title=file.get("name", "Untitled"),
                    web_url=file.get("webViewLink", ""),
                    mime_type=file.get("mimeType", ""),
                )
                db.add(doc)
                db.flush()
                vectors = embedder.embed(chunks) if chunks else []
                for idx, (content, vector) in enumerate(zip(chunks, vectors)):
                    db.add(Chunk(user_id=user_id, document_id=doc.id, content=content, embedding_json=dumps_vector(vector), position=idx))
                job.processed += 1
                job.message = f"Indexed {job.processed} of {job.total} documents."
                job.updated_at = utcnow()
                db.commit()
            except Exception:
                logger.exception("Failed to index a Google Doc", extra={"user_id": user_id, "file_id": file.get("id")})
                job.message = "Some documents could not be indexed. Check backend logs for file IDs."
                db.commit()

        job.status = "complete"
        job.message = "Indexing complete."
        job.updated_at = utcnow()
        db.commit()
    except Exception:
        logger.exception("Drive indexing failed", extra={"user_id": user_id})
        job = latest_job(db, user_id)
        job.status = "error"
        job.message = "Indexing failed. Please try again or reconnect Google."
        job.updated_at = utcnow()
        db.commit()
    finally:
        db.close()
