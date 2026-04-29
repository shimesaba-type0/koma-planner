# Koma Planner Agent Guide

This file is the entry point for AI agents and human contributors working on Koma Planner.

## Product Intent

Koma Planner turns a rough natural-language goal into small, actionable todos that can be started immediately.

The product should feel less like a project-management suite and more like a workspace that appears the moment a user says what they want to do.

## Core Experience

1. The user enters a rough goal.
2. The app asks an AI provider to break it into small tasks.
3. The result becomes an editable todo list immediately.
4. The user can check, edit, reorder, add, delete, and regenerate tasks.
5. Projects are saved so the user can continue later.

## Initial Technical Direction

- Frontend: React
- Backend: FastAPI
- Database: SQLite
- ORM: SQLModel, unless the project later chooses plain SQLAlchemy
- AI integration: user-provided API keys

## Repository Guidance

- Keep the first version small and easy to understand.
- Prefer explicit data models over clever abstractions.
- Preserve a clean boundary between the React UI and the FastAPI backend.
- Treat AI output as untrusted data: validate it before saving or rendering.
- Keep docs current when decisions change.

## Supporting Rules

- Markdown style: `.agents/markdown.md`
- Project rules: `.agents/project-rules.md`
- Product brief: `docs/product-brief.md`
- Architecture notes: `docs/architecture.md`
- MVP scope: `docs/mvp-scope.md`
- Data model draft: `docs/data-model.md`
