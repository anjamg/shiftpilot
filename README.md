# ShiftPilot

ShiftPilot is a self-hostable employee scheduling and attendance application built with React, TypeScript, FastAPI, SQLAlchemy, PostgreSQL, and Docker Compose.

> **Status:** MVP / development starter. It is not production-ready for sensitive employee data until authentication, authorization, database migrations, backups, and a security review are completed.

## Features

- Employee directory with role, department, and active status
- Weekly shift planner with create/list/delete API operations and time validation
- Leave requests with approval/rejection status workflow
- Attendance records and CSV export
- API health endpoint and OpenAPI docs
- Docker Compose setup with PostgreSQL health check
- Automated backend tests, coverage reporting, lint checks, frontend build, and dependency audits in GitHub Actions

## Architecture

```text
Browser (React + TypeScript + Vite)
            | HTTP / JSON
            v
      FastAPI REST API ---- SQLAlchemy ORM
                                  |
                                  v
                             PostgreSQL
```

- `frontend/`: browser application and Vite build
- `backend/app/main.py`: API routes and startup initialization
- `backend/app/schemas.py`: request validation and response schemas
- `backend/app/models.py`: SQLAlchemy data models
- `backend/app/database.py`: database engine and session dependency
- `backend/tests/`: API regression tests using an isolated SQLite database
- `.github/workflows/ci.yml`: automated checks on pushes and pull requests

## Requirements

- Docker Desktop or Docker Engine with the Compose plugin
- For development outside Docker: Python 3.11+ and Node.js 22+

## Run with Docker Compose

```bash
cp .env.example .env
# Edit .env and change all passwords before sharing or deploying the application.
docker compose up --build
```

Open:

- Web app: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health

The first API startup creates database tables and inserts sample employees and shifts if the employee table is empty. To stop the services, run `docker compose down`. To also delete the local database volume, run `docker compose down -v` (this permanently deletes local database data).

## Configuration

The root `.env.example` documents the Compose variables: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DATABASE_URL`, and `VITE_API_URL`. The API also supports `CORS_ORIGINS` as a comma-separated list; see `backend/.env.example` for local backend development. Never commit a real `.env` file or production secrets.

## Run backend tests

From the repository root:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
cd backend
python -m pytest
ruff check app tests
```

The test suite uses an isolated in-memory SQLite database and does not require a running PostgreSQL service. Coverage is reported by pytest-cov; the configured minimum is 65%.

## Build the frontend

```bash
cd frontend
npm install
npm run build
```

The frontend dependencies are declared in `frontend/package.json`. A generated npm lockfile should be committed once dependency installation can be completed in a network-enabled environment; CI currently installs from the manifest and runs the production build.

## Continuous integration

GitHub Actions runs backend tests with coverage, Ruff checks, a backend dependency audit, a frontend production build, and an npm audit on pushes and pull requests. See `.github/workflows/ci.yml` for the source of truth.

## Security and production checklist

Before using this for real employee data, implement and verify:

- Authentication and role-based authorization on every protected endpoint
- Tenant isolation if multiple organizations will use one deployment
- Database migrations (for example, Alembic) instead of relying on `create_all`
- Secure secret management, TLS, backups, restore drills, and retention policies
- Audit logs for schedule and leave-status changes
- Rate limiting, monitoring, and a documented incident response process
- A security review and tests against the intended deployment environment

## Contributing

1. Create a branch for one focused change.
2. Add or update tests for behavior changes.
3. Run the backend test suite and frontend production build locally.
4. Open a pull request describing the behavior changed and evidence from tests.
5. Do not include secrets, real employee data, or unrelated formatting changes.

## License

Copyright (c) 2026 ShiftPilot contributors. All rights reserved unless a separate license is provided. Add and review an explicit commercial license before distributing this repository to buyers.
