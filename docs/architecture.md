# Architecture Notes

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
- Authentication when added

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

The first version can run locally. SaaS deployment and per-user app instances are deferred until the product experience is proven.
