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
- Design database records with required owner scoping from the first schema, even if full authentication ships later.

## Documentation Rules

- Keep project documentation available in both English and Japanese.
- When adding or changing a product, architecture, data model, setup, or security decision, update the English and Japanese versions in the same change.
- Bilingual documentation may live in the same file as clearly labeled English and Japanese sections, or in paired files with matching names.
- If implementation choices differ from existing docs, update the docs before or alongside the code change.

## ドキュメントルール

- Project documentation は English と Japanese の両方を用意する。
- Product、architecture、data model、setup、security に関する決定を追加または変更した場合は、同じ変更内で English と Japanese の両方を更新する。
- Bilingual documentation は、同じ file 内に English / Japanese section を明示して書いてもよいし、対応する paired files として分けてもよい。
- 実装方針が既存 docs とずれる場合は、code change の前、または同じ change の中で docs を更新する。

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
