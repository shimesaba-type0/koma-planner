# Data Model

## English

### Current Decision

Koma Planner should treat project data as private user data from the first persisted schema. The MVP may use a fixed development owner such as `dev-user`, but persisted projects must still be scoped by a required `owner_id`.

Authentication is intentionally not implemented in MVP 02. A later self-hosted auth service should own login, sessions, and MFA, then provide an authenticated user identity to Koma Planner. Koma Planner maps that identity to `owner_id` and, later, `workspace_id`.

TOTP is the likely first MFA candidate because it is mature and small enough to implement. WebAuthn/passkeys remain a possible later improvement.

### Entities

#### Project

Represents a saved goal and its task list.

Fields:

- `id`
- `owner_id`
- `workspace_id`
- `title`
- `goal_text`
- `status`
- `created_at`
- `updated_at`

#### Task

Represents one actionable todo item in a project.

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

#### BreakdownRun

Records an AI generation event.

Fields:

- `id`
- `project_id`
- `provider`
- `model`
- `prompt_version`
- `input_goal`
- `raw_response`
- `status`
- `created_at`

### Deferred Entities

#### User

User accounts are deferred to a later self-hosted authentication service. Koma Planner should not store password credentials in its own application database.

#### ApiKey

Provider credential storage is deferred until the API key configuration flow. If backend persistence is added later, keys must be encrypted and must never be returned to the frontend after saving.

### Notes

- `owner_id` is required so network-accessible deployments do not start from globally visible project data.
- `workspace_id` is optional for now and leaves room for team or multi-workspace support.
- `parent_task_id` allows later subtask support without requiring it in the first UI.
- `position` keeps manual ordering stable.
- `BreakdownRun` makes AI behavior easier to debug later.

## Japanese

### 現在の決定

Koma Planner は、永続化する最初のスキーマからプロジェクトデータをユーザーのプライベートデータとして扱います。MVP 中は `dev-user` のような固定開発用 owner を使ってもよいですが、保存される project は必ず `owner_id` でスコープされる必要があります。

MVP 02 では認証そのものは実装しません。後続で self-hosted な認証サービスを別途作り、ログイン、セッション、MFA をそのサービスに持たせます。Koma Planner は、その認証サービスから受け取ったユーザー identity を `owner_id`、将来的には `workspace_id` に紐づけます。

MFA は後で決めますが、最初の候補は実装が比較的小さく、枯れている TOTP です。WebAuthn/passkey は将来の改善候補として残します。

### エンティティ

#### Project

保存された goal と task list を表します。

フィールド:

- `id`
- `owner_id`
- `workspace_id`
- `title`
- `goal_text`
- `status`
- `created_at`
- `updated_at`

#### Task

Project 内の 1 つの実行可能な todo を表します。

フィールド:

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

#### BreakdownRun

AI による task breakdown の生成イベントを記録します。

フィールド:

- `id`
- `project_id`
- `provider`
- `model`
- `prompt_version`
- `input_goal`
- `raw_response`
- `status`
- `created_at`

### 後回しにするエンティティ

#### User

ユーザーアカウントは、後続で作る self-hosted な認証サービスに任せます。Koma Planner 本体のアプリケーション DB には password credential を保存しません。

#### ApiKey

AI provider の credential 保存は API key 設定フローまで後回しにします。将来 backend に保存する場合は暗号化し、保存済み key を frontend に返してはいけません。

### 補足

- `owner_id` は必須です。ネットワークからアクセスできる deployment で、project data が全体公開扱いになる設計から始めないためです。
- `workspace_id` は現時点では任意です。将来の team や multi-workspace support の余地を残します。
- `parent_task_id` は、最初の UI に subtask を要求せずに将来の subtask support を可能にします。
- `position` は手動並び替えの順序を安定させます。
- `BreakdownRun` は AI の挙動を後から調べやすくします。
