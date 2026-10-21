# ShiftPilot

ShiftPilot is a self-hostable employee scheduling MVP built with React + TypeScript, FastAPI, PostgreSQL, and Docker Compose.

## Included
- Employee directory with role and availability fields
- Weekly shift planner: create, list, and delete shifts
- Leave requests with approval/rejection workflow
- Attendance entries and CSV export
- Demo seed data on first startup
- API health endpoint and basic tests

## Run locally
Requirements: Docker Desktop / Docker Engine with Compose.

```bash
docker compose up --build
```
- Web app: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

The first startup creates tables and inserts demo data. This is an MVP starter, not yet hardened for public production: before selling/deploying publicly, add a production authentication provider, migrations, rate limiting, backups, and security review. Change `SECRET_KEY` and database credentials in `.env` before deployment.

## Demo login
The current MVP has no login screen and is intended for local evaluation only. Authentication and tenant isolation should be implemented before production use.

## Tests
```bash
cd backend
python -m pip install -r requirements.txt
pytest
```

## License
Copyright (c) 2026 ShiftPilot contributors. All rights reserved unless a separate license is provided. Do not redistribute commercially without adding your chosen license terms.
