# Contributing to ShiftPilot

- Keep changes focused and explain the user-visible behavior.
- Add regression tests for bug fixes and tests for new behavior.
- Run `cd backend && python -m pytest` and `ruff check app tests` before opening a pull request.
- Run `cd frontend && npm install && npm run build` for frontend changes.
- Never commit `.env` files, credentials, or real employee data.
- Prefer small, reviewable pull requests over broad unrelated changes.
