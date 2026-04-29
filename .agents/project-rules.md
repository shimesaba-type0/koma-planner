# Project Rules

## Product Rules

- The app must let users start working from an AI breakdown without a separate import step.
- Generated tasks should be editable before and after saving.
- One task should represent one clear action whenever possible.
- The UI should make it easy to adjust task granularity.
- AI output must be validated and normalized before it becomes persisted project data.

## Engineering Rules

- Start with a monorepo-style layout:

```text
apps/
  web/
  api/
docs/
```

- Keep the backend readable for someone who is more comfortable with Python than JavaScript.
- Keep frontend state flows explicit and well named.
- Do not introduce a framework or service unless it directly supports the MVP.
- Prefer SQLite for the initial database.
- Design database records with future `user_id` or `workspace_id` support, even if auth ships after the first prototype.

## Security Rules

- Never log raw API keys.
- Never return stored API keys to the frontend after saving.
- Encrypt API keys before storing them if persisted on the backend.
- For the earliest local prototype, browser-local API key storage is acceptable only if clearly marked as temporary.

## AI Rules

- Ask AI providers for structured JSON.
- Validate JSON shape on the backend.
- Keep prompts versioned in code once implementation begins.
- Preserve the user's original goal text alongside generated tasks.
- Store enough metadata to explain which model generated a breakdown.
