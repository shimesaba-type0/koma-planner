# Issue Implementation Workflow

## English

Use this flow for MVP issue implementation unless the user asks for a different
path.

1. Confirm the issue, dependencies, current branch, and clean working tree.
2. Create a dedicated `codex/` branch before editing.
3. Update or create project documentation first, including English and Japanese
   sections when product, architecture, data model, setup, security, or API
   decisions change.
4. Write focused tests before implementation.
5. Implement the smallest readable slice that satisfies the issue acceptance
   criteria.
6. Run local validation:
   - `npm run build:web`
   - `npm run test:api` with `apps/api/.venv/Scripts` first in `PATH`, or
     `apps/api/.venv/Scripts/python.exe -m pytest -p no:cacheprovider tests`
     directly on Windows.
7. Review the diff for behavior, validation, docs drift, and test coverage.
8. If problems appear, fix them and repeat test and review.
9. Stage only the intended issue files, commit, push, and open a draft PR.
10. Watch GitHub Actions.
11. If CI fails, inspect logs, fix locally, rerun tests, push, and watch CI
    again.
12. When local review and CI are clean, mark the PR ready, do a final review,
    squash merge, delete the remote branch, and update local `main`.

## Japanese

ユーザーから別の進め方を指定されない限り、MVP issue の実装ではこの流れを使います。

1. Issue、dependencies、current branch、clean working tree を確認する。
2. 編集前に専用の `codex/` branch を作る。
3. 最初に project documentation を更新または作成する。Product、architecture、
   data model、setup、security、API decision が変わる場合は English と Japanese
   の両方を書く。
4. 実装前に focused tests を書く。
5. Issue acceptance criteria を満たす、最小で読みやすい実装を作る。
6. Local validation を実行する:
   - `npm run build:web`
   - `apps/api/.venv/Scripts` を `PATH` の先頭にした `npm run test:api`、または
     Windows では `apps/api/.venv/Scripts/python.exe -m pytest -p no:cacheprovider tests`
     を直接実行する。
7. Diff を behavior、validation、docs drift、test coverage の観点で review する。
8. 問題があれば修正し、test と review を繰り返す。
9. 対象 issue の files だけを stage し、commit、push、draft PR 作成を行う。
10. GitHub Actions を監視する。
11. CI が失敗したら logs を確認し、local fix、test、push、CI 監視を繰り返す。
12. Local review と CI が clean になったら PR を ready にし、final review 後に
    squash merge、remote branch delete、local `main` update まで行う。
