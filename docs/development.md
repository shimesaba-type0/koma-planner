# Development

## English

### Requirements

- Node.js 22 or newer
- npm
- Python 3.13 or newer

### Frontend

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

### Backend

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

### Verification

Frontend build and type check:

```powershell
npm run build:web
```

Frontend state tests:

```powershell
npm run test:web
```

Backend tests, after activating `apps/api/.venv`:

```powershell
npm run test:api
```

On Windows, if the global `npm` shim or Python path is not pointing at the virtual environment, run the backend tests directly:

```powershell
cd apps/api
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests
```

These same checks run in GitHub Actions for pull requests and pushes to `main`.

### MVP 04 Test Rationale

MVP 04 adds the breakdown contract before paid AI provider calls. Its backend
tests should cover deterministic mock breakdown output, malformed provider
output rejection, request validation, optional `BreakdownRun` metadata storage,
and owner-scoped project checks when a breakdown is attached to a project.

### MVP 06 Test Rationale

MVP 06 connects the initial workspace UI to the existing breakdown endpoint.
Frontend tests should cover the local workspace state transitions that are
independent of browser rendering: request start, successful task adoption,
empty breakdown results, understandable error state, and todo edits after
generation. `npm run build:web` remains the rendering and TypeScript integration
check.

### MVP 03 Test Rationale

MVP 03 exposes the existing persistence layer through FastAPI. Its backend
tests should cover owner-scoped project endpoints, project creation with
initial tasks, project reopen behavior, task editing, task completion toggles,
task reordering, task deletion, and clear validation/error responses.

### MVP 02 Test Rationale

MVP 02 adds the first persistence layer. Its backend tests cover database table creation, required owner scoping, project CRUD, task CRUD, and task reordering through internal repository functions.

### MVP 01 Test Rationale

MVP 01 is a scaffold ticket. It does not implement AI breakdowns, todo editing, persistence, authentication, or API key handling. Because of that, the test surface should prove that the two application entry points exist and can run, without pretending to validate product behavior that does not exist yet.

The frontend check is `npm run build:web`. This is necessary because it verifies that the React/Vite app compiles, TypeScript accepts the current source, and the production bundle can be produced from `apps/web`.

The backend check is `npm run test:api`, which currently covers `GET /api/health`. This is necessary because it verifies that the FastAPI app can be imported, the app router is wired, and the first API endpoint returns the expected response shape.

Together, these checks are sufficient for MVP 01 because the issue acceptance criteria are about runnable project structure:

- the frontend app exists and builds
- the backend app exists and responds
- local setup and verification commands are documented

They are intentionally not sufficient for later MVP issues. Future tickets should add tests for their own behavior, such as database persistence, AI output validation, todo editing, save/reopen flows, and error handling.

### MVP 01 Notes

This issue only creates the runnable application structure. Persistence, AI breakdowns, and todo editing are handled by later MVP issues.

### MVP 01 Definition Of Done

- `apps/web` exists and builds with `npm run build:web`.
- `apps/api` exists and exposes `GET /api/health`.
- Backend health behavior is covered by `npm run test:api`.
- Local run and verification commands are documented.

## Japanese

### 要件

- Node.js 22 以上
- npm
- Python 3.13 以上

### Frontend

```powershell
cd apps/web
npm install
npm run dev
```

React app は `http://127.0.0.1:5173` で起動します。

Repository root からは次の command も使えます。

```powershell
npm run dev:web
```

### Backend

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

FastAPI app は `http://127.0.0.1:8000` で起動します。

Repository root からは、`apps/api/.venv` を有効化した後に次の command も使えます。

```powershell
npm run dev:api
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

### Verification

Frontend build and type check:

```powershell
npm run build:web
```

Frontend state tests:

```powershell
npm run test:web
```

Backend tests は、`apps/api/.venv` を有効化した後に実行します。

```powershell
npm run test:api
```

Windows で global `npm` shim や Python path が virtual environment を見ていない場合は、backend tests を直接実行します。

```powershell
cd apps/api
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests
```

同じ check は、pull request と `main` への push で GitHub Actions でも実行されます。

### MVP 04 Test Rationale

MVP 04 は有料 AI provider call より先に breakdown contract を追加します。Backend
tests では、deterministic な mock breakdown output、malformed provider output の
rejection、request validation、任意の `BreakdownRun` metadata storage、breakdown を
project に紐づける場合の owner-scoped project checks を確認します。

### MVP 06 Test Rationale

MVP 06 は initial workspace UI を既存の breakdown endpoint に接続します。
Frontend tests では、browser rendering に依存しない local workspace state
transitions を確認します。具体的には request start、successful task adoption、
empty breakdown results、understandable error state、generation 後の todo edit を
対象にします。`npm run build:web` は引き続き rendering と TypeScript integration
の check として使います。

### MVP 03 Test Rationale

MVP 03 は既存の persistence layer を FastAPI から公開します。Backend tests では、
owner-scoped project endpoints、initial tasks 付き project creation、project
reopen behavior、task editing、task completion toggle、task reorder、task deletion、
明確な validation/error response を確認します。

### MVP 02 Test Rationale

MVP 02 は最初の persistence layer を追加します。Backend tests では、database table creation、必須の owner scoping、project CRUD、task CRUD、task reordering を internal repository functions 経由で確認します。

### MVP 01 Test Rationale

MVP 01 は scaffold ticket です。AI breakdown、todo editing、persistence、authentication、API key handling はまだ実装しません。そのため、test surface は frontend と backend の entry point が存在し、起動できることを確認する範囲に留めます。

Frontend check は `npm run build:web` です。React/Vite app が compile でき、TypeScript が current source を受け入れ、production bundle を `apps/web` から生成できることを確認します。

Backend check は `npm run test:api` です。現時点では `GET /api/health` を検証し、FastAPI app が import でき、router が wire され、最初の API endpoint が期待する response shape を返すことを確認します。

### MVP 01 Notes

この issue は runnable application structure だけを作ります。Persistence、AI breakdown、todo editing は後続の MVP issue で扱います。

### MVP 01 Definition Of Done

- `apps/web` exists and builds with `npm run build:web`.
- `apps/api` exists and exposes `GET /api/health`.
- Backend health behavior is covered by `npm run test:api`.
- Local run and verification commands are documented.
