# AgentNexus — Claude Code Instructions

## What this project is
Professional agent collaboration SaaS platform ("dating app for AI agents").
This is an open-source project — code must be clean, documented, and production-ready.

## Stack
- **Backend**: FastAPI 0.110 + Python 3.11 + SQLAlchemy (async) + Alembic + PostgreSQL 15
- **Cache/Queue**: Redis 7 + Celery
- **Vector DB**: Qdrant (for matching embeddings)
- **Object Storage**: MinIO (S3-compatible)
- **Frontend**: Next.js 14 (App Router) + TypeScript 5.4 + Tailwind CSS + shadcn/ui
- **Auth**: Ed25519 cryptographic keypair (PyNaCl backend, jose frontend)
- **Infrastructure**: Docker Compose (local), GitHub Actions CI/CD

## Commands
- Install all: `pnpm install && cd backend && pip install -r requirements.txt`
- Dev (both): `pnpm dev`
- Dev (frontend only): `cd frontend && pnpm dev`
- Dev (backend only): `cd backend && uvicorn app.main:app --reload --port 8000`
- Tests (frontend): `cd frontend && pnpm test`
- Tests (backend): `cd backend && pytest -v`
- Lint (frontend): `cd frontend && pnpm lint`
- Lint (backend): `cd backend && ruff check .`
- Format (backend): `cd backend && ruff format .`
- Typecheck (frontend): `cd frontend && pnpm type-check`
- Docker start: `docker-compose up -d`
- Docker stop: `docker-compose down`
- DB migrate: `cd backend && alembic upgrade head`
- New migration: `cd backend && alembic revision --autogenerate -m "description"`

## File locations
```
frontend/src/app/              → Next.js pages (App Router)
frontend/src/components/       → React components
frontend/src/lib/              → Utilities, API clients, types
backend/app/api/v1/endpoints/  → FastAPI route handlers
backend/app/models/            → SQLAlchemy ORM models
backend/app/schemas/           → Pydantic request/response schemas
backend/app/services/          → Business logic (matching, orchestrator, etc.)
backend/app/core/              → Config, database connection, middleware
backend/tests/                 → pytest tests
```

## Architecture rules
1. All database operations must be async (use AsyncSession)
2. All HTTP calls must be async (use httpx, not requests)
3. Business logic belongs in services/, not in endpoint handlers
4. Endpoint handlers should be thin — validate input, call service, return response
5. Every new DB table needs a corresponding Alembic migration
6. Every new API endpoint needs a Pydantic schema for input and output
7. All agent messages must pass through backend/app/services/orchestrator/safety.py
8. No raw tool sharing between agents — use proposal workflow only

## Coding conventions

### Python
- Type hints on all function parameters and return types
- Async/await for all I/O operations (DB, HTTP, Redis, Qdrant)
- Docstrings on all public functions and classes
- f-strings for string formatting
- Use `logger = logging.getLogger(__name__)` for logging
- Raise HTTPException with appropriate status codes
- Never catch bare `Exception` — be specific

### TypeScript/React
- TypeScript strict mode — no `any` types
- Functional components only (no class components)
- Custom hooks for reusable stateful logic
- Tailwind CSS for all styling — no inline styles, no CSS modules
- shadcn/ui components preferred over building from scratch
- React Query (TanStack) for all server state
- Zustand for client-only state
- Named exports for components (not default exports, except pages)

## Safety requirements
- Never commit .env files or secrets
- Rate limiting required on all public endpoints
- Input validation via Pydantic (backend) and Zod (frontend)
- Agent messages must be sanitized before storage
- Prompt injection patterns must be detected and flagged

## Do NOT modify
- backend/venv/ — virtual environment
- frontend/node_modules/ — dependencies  
- frontend/.next/ — build cache
- *.env files — edit manually, never commit
- alembic/versions/ — only generate via alembic commands

## PR / commit standards
- Conventional commits: feat:, fix:, docs:, refactor:, test:, chore:
- All tests must pass before commit
- No commented-out code
- No TODO comments without a GitHub issue reference

## When you're unsure about something
Ask before implementing. It's better to clarify than to refactor.
