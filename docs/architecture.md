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
- AI provider calls
- AI response validation
- API key storage and encryption when backend persistence is enabled
- Consume authenticated user identity when auth is added

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
- AI provider calls
- AI response validation
- API key storage and encryption when backend persistence is enabled
- 認証追加後は、認証済み user identity を受け取って project data を owner ごとに扱う

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
