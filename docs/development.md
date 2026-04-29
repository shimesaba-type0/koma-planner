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

## MVP 01 Notes

This issue only creates the runnable application structure. Persistence, AI breakdowns, and todo editing are handled by later MVP issues.

## MVP 01 Definition Of Done

- `apps/web` exists and builds with `npm run build:web`.
- `apps/api` exists and exposes `GET /api/health`.
- Backend health behavior is covered by `npm run test:api`.
- Local run and verification commands are documented.
