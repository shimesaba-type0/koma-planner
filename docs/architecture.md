# Architecture Notes

## English

## Initial Stack

- React frontend
- FastAPI backend
- SQLite database
- SQLModel ORM
- User-provided AI API keys

## Proposed Layout

```text
koma-planner/
  AGENTS.md
  .agents/
    markdown.md
    project-rules.md
  apps/
    web/
    api/
  docs/
    product-brief.md
    architecture.md
    mvp-scope.md
    data-model.md
```

## Local App Structure

- `apps/web`: React + Vite frontend.
- `apps/api`: FastAPI backend.
- `docs/development.md`: local run commands and environment notes.

## Frontend Responsibilities

- Goal input
- Project list and project detail screens
- Todo interaction: check, edit, add, delete, reorder
- Breakdown review and regeneration controls
- API key settings screen or modal

## Backend Responsibilities

- Project persistence
- Task persistence
- Project and task API endpoints
- AI provider calls
- AI response validation
- API key storage and encryption when backend persistence is enabled
- Consume authenticated user identity when auth is added

## MVP 03 API Direction

Until authentication middleware is added, FastAPI endpoints use the
`X-Koma-Owner-Id` request header as a temporary owner scope bridge. Requests
without the header use `dev-user`. This is intentionally local-prototype
behavior; network-accessible deployments still require real authentication
before private project data is exposed.

See `docs/api.md` for the current endpoint contract.

## AI Breakdown Flow

```text
User goal
  -> frontend sends breakdown request
  -> backend loads provider settings
  -> backend calls AI provider
  -> backend validates structured response
  -> backend returns normalized tasks
  -> frontend renders tasks as editable todos
  -> user saves project
```

## Early Deployment Assumption

The first version can run locally, but persisted data should still be scoped as private user data. Any network-accessible deployment should require login. Authentication will be implemented later in a separate self-hosted service, while Koma Planner keeps owner-scoped project records.

## Japanese

### 初期スタック

- React frontend
- FastAPI backend
- SQLite database
- SQLModel ORM
- User-provided AI API keys

### 提案レイアウト

```text
koma-planner/
  AGENTS.md
  .agents/
    markdown.md
    project-rules.md
  apps/
    web/
    api/
  docs/
    product-brief.md
    architecture.md
    mvp-scope.md
    data-model.md
```

### ローカルアプリ構成

- `apps/web`: React + Vite frontend.
- `apps/api`: FastAPI backend.
- `docs/development.md`: local run commands and environment notes.

### Frontend の責務

- Goal input
- Project list and project detail screens
- Todo interaction: check, edit, add, delete, reorder
- Breakdown review and regeneration controls
- API key settings screen or modal

### Backend の責務

- Project persistence
- Task persistence
- Project and task API endpoints
- AI provider calls
- AI response validation
- API key storage and encryption when backend persistence is enabled
- 認証追加後は、認証済み user identity を受け取って project data を owner ごとに扱う

### MVP 03 API 方針

認証 middleware を追加するまでは、FastAPI endpoints は `X-Koma-Owner-Id`
request header を一時的な owner scope bridge として使います。Header がない場合は
`dev-user` を使います。これは local prototype 用の挙動です。Network-accessible
deployment では、private project data を公開する前に real authentication が必要です。

現在の endpoint contract は `docs/api.md` を参照してください。

### AI Breakdown Flow

```text
User goal
  -> frontend sends breakdown request
  -> backend loads provider settings
  -> backend calls AI provider
  -> backend validates structured response
  -> backend returns normalized tasks
  -> frontend renders tasks as editable todos
  -> user saves project
```

### 初期 deployment 方針

最初の version は local で動かせればよいですが、永続化データは最初から private user data として owner ごとにスコープします。ネットワークからアクセスできる deployment では login 必須にします。認証は後続で別の self-hosted service として実装し、Koma Planner は owner-scoped な project records を持ちます。
