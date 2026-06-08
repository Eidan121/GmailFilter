# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI-powered Gmail filtering and labeling tool. The flow: OAuth-connected Gmail accounts are scanned
in the background for "email floods" (senders generating high volume), Claude generates filter/label
suggestions for those senders, and the user reviews and accepts/dismisses suggestions in the web UI,
which then creates real Gmail filters and labels via the Gmail API.

This repo also has the Gmail MCP integration available directly in-session
(`mcp__claude_ai_Gmail__*` tools) for ad-hoc reading, searching, and labeling of threads —
independent of the app's own backend Gmail client.

## Project Structure

```
backend/    Python FastAPI app (uv-managed) — API, DB, OAuth, scanner daemon, AI suggestions
frontend/   TypeScript/React Vite app (pnpm-managed) — dashboard, filter/suggestion review UI
```

## Backend (`backend/app/`)

Stack: FastAPI, SQLAlchemy 2.0 + Alembic (SQLite), Pydantic v2, APScheduler, google-api-python-client,
Anthropic SDK (`claude-sonnet-4-6`).

- **routers/** — API endpoints
  - `accounts.py` — OAuth login/logout, account management (`/api/accounts`)
  - `filters.py` — CRUD for Gmail filters (`/api/accounts/{account_id}/filters`)
  - `labels.py` — Create/manage Gmail labels (`/api/accounts/{account_id}/labels`)
  - `suggestions.py` — AI-generated filter suggestions (`/api/suggestions`)
  - `scan.py` — Trigger/check scan status (`/api/scan`)
  - `events.py` — SSE stream for real-time updates (`/api/events/stream`)
- **models/** — SQLAlchemy models: `GmailAccount`, `FilterSuggestion` (status: pending/accepted/dismissed),
  `ScanResult`, `CachedFilter`
- **services/** — `filter_service.py`, `label_service.py`, `suggestion_service.py`, `oauth.py`
  (token exchange/refresh), `gmail_client.py` (Gmail API wrapper)
- **scanner/** — background daemon
  - `daemon.py` — APScheduler loop running `full_scan()` every `SCAN_INTERVAL_HOURS`
  - `flood_detector.py` — flags senders exceeding `FLOOD_THRESHOLD`
  - `ai_suggester.py` — calls Claude (tool use) to turn flood data into filter suggestions
  - `notifier.py` — pushes scan progress to the SSE queue consumed by `events.py`

## Frontend (`frontend/src/`)

Stack: React 18 + TypeScript, Vite, React Router 7, Zustand (state), Three.js / R3F (3D visuals).

- **pages/** — `Dashboard` (accounts/scan overview), `AddAccount` (OAuth redirect handler),
  `FilterManager`, `Suggestions` (review/accept/dismiss), `NotFound`
- **components/** — grouped by domain: `filters/`, `suggestions/`, `labels/`, `layout/`, `shared/`, `three/`
- **store/** — Zustand stores: `accountStore`, `filterStore`, `suggestionStore` (also wires up SSE events)
- **api/** — thin wrappers per resource (`accounts`, `filters`, `labels`, `suggestions`, `scan`, `events`)
  over a shared `client.ts`

## Dev Commands

### Backend
```bash
cd backend
uv sync                                           # install deps
uv run alembic upgrade head                       # run DB migrations
uv run alembic revision --autogenerate -m "msg"   # create a new migration
uv run uvicorn app.main:app --reload --port 8000  # API server
uv run python -m app.scanner.daemon               # background scanner (separate process)
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev        # Vite dev server → http://localhost:5173
pnpm build      # production build → frontend/dist/
```

### Docker (all services)
```bash
cp .env.example .env   # set ANTHROPIC_API_KEY (and optionally API_HOST/PORT, FRONTEND_ORIGIN,
                       # FLOOD_THRESHOLD, SCAN_INTERVAL_HOURS)
docker compose up --build
```
Services: `backend` (FastAPI, :8000), `scanner` (daemon), `frontend` (built app, :80).
They share the `gmail_data` volume mounted at `~/.gmail_filter_app` for OAuth tokens/DB.

## One-time OAuth Setup (operator only — end users never see this)
Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` in `.env`.
Obtain from: Google Cloud Console → APIs & Services → Credentials → Create OAuth 2.0 Client ID
→ type **Web application** → add authorized redirect URI `http://localhost:8000/api/accounts/callback`.
Required scopes: `gmail.readonly`, `gmail.labels`, `gmail.settings.basic`.
End users connecting their Gmail account just click "Connect with Google" in the UI and go through
Google's normal consent screen — they never interact with the client ID/secret.

## Architecture Notes
- Credentials stored at `~/.gmail_filter_app/` (`accounts.db`, `token.key`)
- Gmail OAuth tokens are stored **encrypted in the database** (`gmail_accounts.encrypted_token`,
  Fernet-encrypted with the key at `token.key` or `TOKEN_ENCRYPTION_KEY`), not on disk as files.
  Each time an account is (re)connected, Google forces a fresh consent screen and the stored token
  is replaced — old tokens don't persist across reconnects.
- Background scanner runs every `SCAN_INTERVAL_HOURS` (default 6h) via APScheduler; results pushed
  to the frontend over SSE (`/api/events/stream`) and consumed by `suggestionStore`
- Gmail's Filters API has **no update endpoint** — editing a filter means delete + recreate
  (`filter_service.py` handles this)
- Claude (`claude-sonnet-4-6`, set via `ANTHROPIC_API_KEY`) is called from `ai_suggester.py`
  with tool use to turn flood-detection data into structured filter suggestions
- DB is SQLite; migrations: `0001_initial.py`, `0002_db_backed_tokens.py` (moved tokens from
  files to an encrypted DB column)
