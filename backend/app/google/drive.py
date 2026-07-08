from app.config import get_settings
from app.google.client import docs_service, drive_service
from app.models.db import User
from sqlalchemy.orm import Session

settings = get_settings()
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"


FILTERS = {
    "recent_opened": {
        "label": "recently opened",
        "query": f"mimeType='{GOOGLE_DOC_MIME}' and trashed=false",
        "order_by": "viewedByMeTime desc",
    },
    "recent_modified": {
        "label": "recently modified",
        "query": f"mimeType='{GOOGLE_DOC_MIME}' and trashed=false",
        "order_by": "modifiedTime desc",
    },
    "owned_by_me": {
        "label": "owned by you",
        "query": f"mimeType='{GOOGLE_DOC_MIME}' and trashed=false and 'me' in owners",
        "order_by": "modifiedTime desc",
    },
    "shared_with_me": {
        "label": "shared with you",
        "query": f"mimeType='{GOOGLE_DOC_MIME}' and trashed=false and sharedWithMe=true",
        "order_by": "viewedByMeTime desc",
    },
}


def filter_label(mode: str) -> str:
    return FILTERS.get(mode, FILTERS["recent_opened"])["label"]


def list_google_docs(user: User, db: Session, mode: str = "recent_opened") -> list[dict]:
    selected = FILTERS.get(mode, FILTERS["recent_opened"])
    service = drive_service(user, db)
    results = service.files().list(
        q=selected["query"],
        fields="files(id,name,mimeType,webViewLink,viewedByMeTime,modifiedTime,owners)",
        pageSize=settings.max_docs_per_index,
        orderBy=selected["order_by"],
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
