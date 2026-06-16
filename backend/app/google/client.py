from datetime import datetime, timezone

from fastapi import HTTPException, status
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from requests.exceptions import HTTPError
from sqlalchemy.orm import Session

from app.auth.google_oauth import SCOPES, refresh_access_token, token_expiry
from app.models.db import User
from app.security import decrypt_token, encrypt_token


def ensure_access_token(user: User, db: Session) -> str:
    expiry = user.token_expiry
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry and expiry > datetime.now(timezone.utc):
        token = decrypt_token(user.access_token_enc)
        if token:
            return token
    refresh = decrypt_token(user.refresh_token_enc)
    if not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token expired. Please sign in again.")
    try:
        refreshed = refresh_access_token(refresh)
    except HTTPError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token refresh failed. Please sign in again.")
    user.access_token_enc = encrypt_token(refreshed["access_token"])
    user.token_expiry = token_expiry(refreshed.get("expires_in"))
    db.commit()
    return refreshed["access_token"]


def google_credentials(user: User, db: Session) -> Credentials:
    return Credentials(token=ensure_access_token(user, db), scopes=SCOPES)


def drive_service(user: User, db: Session):
    return build("drive", "v3", credentials=google_credentials(user, db), cache_discovery=False)


def docs_service(user: User, db: Session):
    return build("docs", "v1", credentials=google_credentials(user, db), cache_discovery=False)
