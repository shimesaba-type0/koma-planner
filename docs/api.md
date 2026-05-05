# API Contract

## English

### Current Decision

MVP 03 exposes the persisted project and task operations through FastAPI under
the `/api` prefix. MVP 04 adds the backend breakdown contract for turning a
rough goal into validated task suggestions.

Authentication is still deferred. Until authentication middleware exists, API
requests are scoped by the `X-Koma-Owner-Id` header. If the header is omitted,
the backend uses the temporary development owner `dev-user`. This keeps the
first public API aligned with the required `owner_id` data model without
building the later auth service in this issue.

### Project Endpoints

- `POST /api/projects`
  - Creates a project.
  - Accepts optional initial tasks so the frontend can save a generated todo
    list in one request.
- `GET /api/projects`
  - Lists projects for the current owner.
- `GET /api/projects/{project_id}`
  - Returns one project with its tasks.
- `PATCH /api/projects/{project_id}`
  - Updates editable project fields.
- `DELETE /api/projects/{project_id}`
  - Deletes the project and its related tasks and breakdown runs.

### Task Endpoints

- `POST /api/projects/{project_id}/tasks`
  - Creates a task in a project.
- `PATCH /api/projects/{project_id}/tasks/{task_id}`
  - Updates editable task fields, including status and position.
- `PATCH /api/projects/{project_id}/tasks/{task_id}/completion`
  - Checks or unchecks a task with a boolean `completed` field.
- `PATCH /api/projects/{project_id}/tasks/reorder`
  - Persists the exact task order for a project.
- `DELETE /api/projects/{project_id}/tasks/{task_id}`
  - Deletes a task and its descendants.

### Breakdown Endpoint

- `POST /api/breakdowns`
  - Accepts a rough `goal_text`.
  - Returns normalized task suggestions with stable `position` values.
  - Uses a local `mock` provider by default so development works without API
    credits.
  - Accepts optional `project_id`; when provided, a `BreakdownRun` metadata
    record is stored for the owner-scoped project.
  - MVP 06 frontend calls this endpoint without `project_id` for an unsaved
    workspace, then renders the returned suggestions as editable local todos.

Expected normalized task shape:

```json
{
  "title": "Write a small API contract",
  "description": "Optional details about the action",
  "acceptance_criteria": "Optional completion check",
  "position": 0,
  "estimate_minutes": 30
}
```

### Validation

Request bodies use typed schemas. Empty required text fields are rejected before
data reaches the repository layer. Missing owner-scoped records return `404`.
Invalid task reorder payloads return `400` because the task ID list must match
the project's current task set exactly. Malformed breakdown provider output is
rejected before tasks reach the frontend or database.

## Japanese

### 現在の決定

MVP 03 では、永続化済みの project / task 操作を FastAPI の `/api` prefix
配下で公開します。MVP 04 では、rough goal を validated task suggestions に変換する
backend breakdown contract を追加します。

認証 middleware はまだ後続に回します。それまでの API request は
`X-Koma-Owner-Id` header で owner scope を決めます。Header がない場合は、
開発用の一時 owner である `dev-user` を使います。これにより、この issue で
後続の auth service を作らずに、最初の public API を必須 `owner_id` data
model と揃えます。

### Project Endpoints

- `POST /api/projects`
  - Project を作成します。
  - Frontend が generated todo list を 1 request で保存できるように、
    initial tasks を任意で受け取ります。
- `GET /api/projects`
  - 現在の owner の projects を一覧します。
- `GET /api/projects/{project_id}`
  - 1 つの project と tasks を返します。
- `PATCH /api/projects/{project_id}`
  - Project の編集可能な fields を更新します。
- `DELETE /api/projects/{project_id}`
  - Project と関連する tasks / breakdown runs を削除します。

### Task Endpoints

- `POST /api/projects/{project_id}/tasks`
  - Project に task を作成します。
- `PATCH /api/projects/{project_id}/tasks/{task_id}`
  - Status や position を含む task の編集可能な fields を更新します。
- `PATCH /api/projects/{project_id}/tasks/{task_id}/completion`
  - Boolean の `completed` field で task を check / uncheck します。
- `PATCH /api/projects/{project_id}/tasks/reorder`
  - Project の task order を保存します。
- `DELETE /api/projects/{project_id}/tasks/{task_id}`
  - Task とその descendants を削除します。

### Breakdown Endpoint

- `POST /api/breakdowns`
  - Rough な `goal_text` を受け取ります。
  - Stable な `position` を持つ normalized task suggestions を返します。
  - Default では local `mock` provider を使うため、API credits なしで開発できます。
  - 任意の `project_id` を受け取ります。指定された場合、owner-scoped project に
    `BreakdownRun` metadata record を保存します。
  - MVP 06 frontend は、保存前 workspace では `project_id` なしでこの endpoint を
    呼び出し、返された suggestions を editable な local todo として表示します。

Expected normalized task shape:

```json
{
  "title": "Write a small API contract",
  "description": "Optional details about the action",
  "acceptance_criteria": "Optional completion check",
  "position": 0,
  "estimate_minutes": 30
}
```

### Validation

Request body は typed schema を使います。必須 text field が空の場合は、
repository layer に届く前に reject します。Owner scope 内に record がない場合は
`404` を返します。不正な task reorder payload は `400` を返します。Task ID list
は project の現在の task set と完全に一致する必要があります。Malformed な
breakdown provider output は、tasks が frontend や database に届く前に reject します。
