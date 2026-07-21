# DriveMind

DriveMind is an AI-powered Google Drive knowledge search app that turns private Google Docs into a searchable, cited knowledge base.

Users sign in with Google, index selected Google Docs, ask natural-language questions, and get grounded answers with citations that link back to the original Drive files.

## Demo

[Watch the DriveMind demo](https://drive.google.com/file/d/1COz-9pcUn4Zbc0Hsy5bFRFn6pqVQpxO3/view?usp=sharing)

## Product Walkthrough

| Step | Preview |
|------|---------|
| 1. Land on a privacy-first Google Drive search page. | <img src="docs/screenshots/landing.png" alt="DriveMind landing page" width="720"> |
| 2. Connect Google and index selected Drive documents. | <img src="docs/screenshots/dashboard-indexing.png" alt="DriveMind dashboard indexing view" width="720"> |
| 3. Review indexed docs and open the original Google files. | <img src="docs/screenshots/documents.png" alt="DriveMind indexed documents page" width="720"> |
| 4. Ask a question inside one selected document. | <img src="docs/screenshots/doc-search-summary.png" alt="DriveMind document-scoped search summary" width="720"> |
| 5. Verify answers with cited excerpts and Drive links. | <img src="docs/screenshots/citations.png" alt="DriveMind cited answer cards" width="720"> |
| 6. Search across all indexed docs for cross-document answers. | <img src="docs/screenshots/global-search.png" alt="DriveMind global document search" width="720"> |
| 7. Compare ranked citations from multiple documents. | <img src="docs/screenshots/global-citations.png" alt="DriveMind global search citations" width="720"> |
| 8. Delete indexed data and encrypted OAuth tokens from Settings. | <img src="docs/screenshots/settings.png" alt="DriveMind settings privacy controls" width="720"> |
| 9. Submit tester feedback from inside the beta app. | <img src="docs/screenshots/feedback.png" alt="DriveMind tester feedback form" width="720"> |

## Features

- Google OAuth 2.0 sign-in with read-only Drive and Docs scopes
- Google Drive indexing for Docs the user recently opened, modified, owns, or has shared
- Google Docs API text extraction, chunking, embeddings, and retrieval
- AI answer generation with citations and excerpts
- Document-scoped search and global Drive search
- Delete indexed data and OAuth tokens from Settings
- Tester feedback form
- Docker-ready backend and frontend

## Tech Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL, SQLite fallback
- Frontend: React, TypeScript, Vite
- Google APIs: OAuth 2.0, Drive API, Docs API
- AI: provider abstraction for dummy local mode, OpenAI, or Gemini
- Embeddings: provider abstraction with local fallback
- Search: pgvector-ready architecture with Python cosine similarity fallback
- Deployment: Docker, docker-compose, Vercel-friendly frontend

## Local Setup

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Local URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/health`

## Required Environment Variables

```bash
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
DATABASE_URL=sqlite:///./drivemind.db
AI_PROVIDER=dummy
EMBEDDING_PROVIDER=dummy
APP_ENV=local
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

Optional:

```bash
OPENAI_API_KEY=
GEMINI_API_KEY=
```

## Google Cloud Setup

1. Create a Google Cloud project.
2. Enable Google Drive API and Google Docs API.
3. Configure the OAuth consent screen.
4. Add yourself under Test users while the app is in testing mode.
5. Create a Web OAuth client.
6. Add `http://localhost:8000/auth/callback` as an authorized redirect URI.
7. Copy the client ID and client secret into `backend/.env`.

Required scopes:

- `openid`
- `email`
- `profile`
- `https://www.googleapis.com/auth/drive.metadata.readonly`
- `https://www.googleapis.com/auth/documents.readonly`

## Deployment

- Backend: deploy the FastAPI service to Render, Railway, Fly.io, or another Docker/Python host.
- Database: use managed PostgreSQL in production.
- Frontend: deploy the `frontend` folder to Vercel and set `VITE_API_URL` to the backend URL.
- Google OAuth: add the production callback URL to Google Cloud before testing deployed login.

## Privacy Notes

- DriveMind requests read-only Google permissions.
- OAuth tokens are encrypted before storage.
- Document contents are not written to backend logs.
- Users can delete indexed documents, chunks, embeddings, and stored Google tokens.
- Dummy AI and embedding modes are available for local demos without paid API calls.

## Known Limitations

- The MVP indexes Google Docs only.
- Large Drive accounts should use a worker queue for production-scale indexing.
- Local search uses Python similarity; native pgvector retrieval is the next production hardening step.

## Future Improvements

- PDF, Slides, Sheets, and OCR support
- Incremental Drive sync
- Team workspaces
- Better reranking and citation highlighting
- Admin analytics without logging document contents

