# Data Model Draft

## Entities

### User

Deferred for the first local prototype, but the schema should leave room for it.

Fields:

- `id`
- `email`
- `display_name`
- `created_at`

### ApiKey

Stores provider credentials when backend persistence is enabled.

Fields:

- `id`
- `user_id`
- `provider`
- `encrypted_api_key`
- `default_model`
- `created_at`
- `updated_at`

### Project

Represents a saved goal and its task list.

Fields:

- `id`
- `user_id`
- `title`
- `goal_text`
- `status`
- `created_at`
- `updated_at`

### Task

Represents one actionable todo item.

Fields:

- `id`
- `project_id`
- `parent_task_id`
- `title`
- `description`
- `acceptance_criteria`
- `status`
- `position`
- `estimate_minutes`
- `created_at`
- `updated_at`

### BreakdownRun

Records an AI generation event.

Fields:

- `id`
- `project_id`
- `provider`
- `model`
- `prompt_version`
- `input_goal`
- `raw_response`
- `created_at`

## Notes

- `parent_task_id` allows later subtask support without requiring it in the first UI.
- `position` keeps manual ordering stable.
- `BreakdownRun` makes AI behavior easier to debug later.
- API keys must not be stored in plaintext in production-like modes.
