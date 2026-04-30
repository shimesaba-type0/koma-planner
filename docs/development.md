# Development

## Requirements

- Node.js 22 or newer
- npm
- Python 3.13 or newer

## Frontend

```powershell
cd apps/web
npm install
npm run dev
```

The React app runs at `http://127.0.0.1:5173`.

From the repository root, you can also run:

```powershell
npm run dev:web
```

## Backend

```powershell
cd apps/api
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

The FastAPI app runs at `http://127.0.0.1:8000`.

From the repository root, after activating `apps/api/.venv`, you can also run:

```powershell
npm run dev:api
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

## Verification

Frontend build and type check:

```powershell
npm run build:web
```

Backend tests, after activating `apps/api/.venv`:

```powershell
npm run test:api
```

These same checks run in GitHub Actions for pull requests and pushes to `main` or `codex/**` branches.

## MVP 01 Test Rationale

MVP 01 is a scaffold ticket. It does not implement AI breakdowns, todo editing, persistence, authentication, or API key handling. Because of that, the test surface should prove that the two application entry points exist and can run, without pretending to validate product behavior that does not exist yet.

The frontend check is `npm run build:web`. This is necessary because it verifies that the React/Vite app compiles, TypeScript accepts the current source, and the production bundle can be produced from `apps/web`.

The backend check is `npm run test:api`, which currently covers `GET /api/health`. This is necessary because it verifies that the FastAPI app can be imported, the app router is wired, and the first API endpoint returns the expected response shape.

Together, these checks are sufficient for MVP 01 because the issue acceptance criteria are about runnable project structure:

- the frontend app exists and builds
- the backend app exists and responds
- local setup and verification commands are documented

They are intentionally not sufficient for later MVP issues. Future tickets should add tests for their own behavior, such as database persistence, AI output validation, todo editing, save/reopen flows, and error handling.

## MVP 01 Notes

This issue only creates the runnable application structure. Persistence, AI breakdowns, and todo editing are handled by later MVP issues.

## MVP 01 Definition Of Done

- `apps/web` exists and builds with `npm run build:web`.
- `apps/api` exists and exposes `GET /api/health`.
- Backend health behavior is covered by `npm run test:api`.
- Local run and verification commands are documented.
