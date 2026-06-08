.PHONY: help setup setup-backend setup-frontend dev dev-backend dev-scanner dev-frontend \
        build build-frontend migrate db-reset lint lint-backend lint-frontend \
        docker docker-build docker-down docker-logs clean

# ── Default ────────────────────────────────────────────────────────────────────

help:
	@echo ""
	@echo "  GmailFilter — available targets"
	@echo ""
	@echo "  Setup"
	@echo "    make setup          Install all dependencies (backend + frontend)"
	@echo "    make setup-backend  Install Python deps with uv"
	@echo "    make setup-frontend Install Node deps with pnpm"
	@echo "    make migrate        Run Alembic DB migrations"
	@echo ""
	@echo "  Development"
	@echo "    make dev            Start all 3 services in parallel (requires tmux)"
	@echo "    make dev-backend    FastAPI server on :8000 (hot reload)"
	@echo "    make dev-scanner    Background flood scanner daemon"
	@echo "    make dev-frontend   Vite dev server on :5173"
	@echo ""
	@echo "  Build"
	@echo "    make build          Build frontend for production"
	@echo ""
	@echo "  Docker"
	@echo "    make docker         Build images and start all services"
	@echo "    make docker-build   Build Docker images only"
	@echo "    make docker-down    Stop and remove containers"
	@echo "    make docker-logs    Follow logs from all services"
	@echo ""
	@echo "  Lint"
	@echo "    make lint           Lint backend + frontend"
	@echo "    make lint-backend   Ruff + type-check Python"
	@echo "    make lint-frontend  ESLint + tsc"
	@echo ""
	@echo "  Misc"
	@echo "    make db-reset       Drop and re-run all migrations"
	@echo "    make clean          Remove build artefacts and caches"
	@echo ""

# ── Setup ──────────────────────────────────────────────────────────────────────

setup: setup-backend setup-frontend migrate
	@echo "✓ Setup complete"

setup-backend:
	cd backend && uv sync

setup-frontend:
	cd frontend && pnpm install

migrate:
	cd backend && uv run alembic upgrade head

# Create ~/.gmail_filter_app dirs + copy .env if missing
init-dirs:
	mkdir -p ~/.gmail_filter_app/tokens
	@test -f .env || (cp .env.example .env && echo "Created .env — set ANTHROPIC_API_KEY inside")

# ── Development ────────────────────────────────────────────────────────────────

dev: init-dirs
	@command -v tmux >/dev/null 2>&1 || (echo "tmux not found — run dev-backend / dev-scanner / dev-frontend in separate terminals" && exit 1)
	tmux new-session -d -s gmailfilter -n api    'make dev-backend'  \; \
	     new-window  -t gmailfilter -n scanner   'make dev-scanner'  \; \
	     new-window  -t gmailfilter -n frontend  'make dev-frontend' \; \
	     attach-session -t gmailfilter

dev-backend: init-dirs
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-scanner: init-dirs
	cd backend && uv run python -m app.scanner.daemon

dev-frontend:
	cd frontend && pnpm dev

# ── Build ──────────────────────────────────────────────────────────────────────

build: build-frontend

build-frontend:
	cd frontend && pnpm build

# ── Docker ─────────────────────────────────────────────────────────────────────

docker: init-dirs
	docker compose up --build

docker-build:
	docker compose build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ── Lint ───────────────────────────────────────────────────────────────────────

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run python -m py_compile $$(find app -name "*.py") && echo "✓ Backend syntax OK"

lint-frontend:
	cd frontend && pnpm lint && pnpm exec tsc -b --noEmit

# ── Misc ───────────────────────────────────────────────────────────────────────

db-reset:
	cd backend && uv run alembic downgrade base && uv run alembic upgrade head

clean:
	rm -rf frontend/dist frontend/node_modules/.vite
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
