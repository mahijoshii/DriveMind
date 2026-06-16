from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routes import auth, documents, drive, feedback, query, users
from app.utils.logging import configure_logging

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="DriveMind API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "env": settings.app_env}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(drive.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(feedback.router)
