# Markdown Rules

## Style

- Use concise headings.
- Prefer short paragraphs over deeply nested lists.
- Use fenced code blocks for file trees, commands, JSON, and schemas.
- Keep product decisions explicit and dated when they may change.

## Task Docs

When writing task or design docs, separate:

- decided facts
- open questions
- deferred ideas

This keeps early exploration from hardening into accidental requirements.

## File Trees

Use this style:

```text
koma-planner/
  apps/
    web/
    api/
  docs/
```

## Terminology

- Use "task" for an individual actionable todo.
- Use "project" for a saved user goal and its task set.
- Use "breakdown" for AI-generated decomposition.
- Avoid calling the product a Gantt or WBS tool unless discussing things it intentionally avoids.
