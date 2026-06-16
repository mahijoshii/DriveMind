from app.config import get_settings
from app.google.client import docs_service, drive_service
from app.models.db import User
from sqlalchemy.orm import Session

settings = get_settings()
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"


def list_google_docs(user: User, db: Session) -> list[dict]:
    service = drive_service(user, db)
    results = service.files().list(
        q=f"mimeType='{GOOGLE_DOC_MIME}' and trashed=false",
        fields="files(id,name,mimeType,webViewLink,viewedByMeTime)",
        pageSize=settings.max_docs_per_index,
        orderBy="viewedByMeTime desc",
    ).execute()
    return results.get("files", [])


def extract_doc_text(user: User, db: Session, document_id: str) -> str:
    service = docs_service(user, db)
    doc = service.documents().get(documentId=document_id).execute()
    parts: list[str] = []
    for item in doc.get("body", {}).get("content", []):
        para = item.get("paragraph")
        if not para:
            continue
        for element in para.get("elements", []):
            text = element.get("textRun", {}).get("content")
            if text:
                parts.append(text)
    return "".join(parts).strip()
