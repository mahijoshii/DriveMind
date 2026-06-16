import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.google_oauth import build_auth_url, exchange_code, fetch_userinfo, token_expiry
from app.config import get_settings
from app.database import get_db
from app.models.db import User
from app.security import create_session_token, encrypt_token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/login")
def login(response: Response):
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID is not configured")
    state = secrets.token_urlsafe(24)
    response = RedirectResponse(build_auth_url(state))
    response.set_cookie("oauth_state", state, httponly=True, samesite="lax", secure=settings.app_env == "production", max_age=600)
    return response


@router.get("/callback")
def callback(code: str, state: str, request: Request, db: Session = Depends(get_db)):
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    tokens = exchange_code(code)
    profile = fetch_userinfo(tokens["access_token"])
    user = db.query(User).filter(User.google_sub == profile["sub"]).first()
    if not user:
        user = User(google_sub=profile["sub"], email=profile["email"], name=profile.get("name"))
        db.add(user)
    user.email = profile["email"]
    user.name = profile.get("name")
    user.access_token_enc = encrypt_token(tokens.get("access_token"))
    if tokens.get("refresh_token"):
        user.refresh_token_enc = encrypt_token(tokens.get("refresh_token"))
    user.token_expiry = token_expiry(tokens.get("expires_in"))
    db.commit()
    db.refresh(user)

    redirect = RedirectResponse(f"{settings.frontend_url}/dashboard")
    redirect.set_cookie("drivemind_session", create_session_token(user.id), httponly=True, samesite="lax", secure=settings.app_env == "production", max_age=60 * 60 * 24 * 7)
    redirect.delete_cookie("oauth_state")
    return redirect
