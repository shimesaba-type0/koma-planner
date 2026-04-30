from collections.abc import Sequence

from sqlmodel import Session, col, select

from app.models import BreakdownRun, BreakdownRunStatus, Project, ProjectStatus, Task, TaskStatus, utc_now


def create_project(
    session: Session,
    *,
    owner_id: str,
    title: str,
    goal_text: str,
    workspace_id: str | None = None,
) -> Project:
    _require_text(owner_id, "owner_id")
    _require_text(title, "title")
    _require_text(goal_text, "goal_text")
    project = Project(
        owner_id=owner_id,
        workspace_id=workspace_id,
        title=title,
        goal_text=goal_text,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def list_projects(session: Session, *, owner_id: str) -> list[Project]:
    statement = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .order_by(col(Project.updated_at).desc(), col(Project.id).desc())
    )
    return list(session.exec(statement).all())


def get_project(session: Session, *, owner_id: str, project_id: int) -> Project | None:
    statement = select(Project).where(Project.id == project_id, Project.owner_id == owner_id)
    return session.exec(statement).first()


def update_project(
    session: Session,
    *,
    owner_id: str,
    project_id: int,
    title: str | None = None,
    goal_text: str | None = None,
    status: ProjectStatus | None = None,
) -> Project | None:
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        return None

    if title is not None:
        project.title = title
    if goal_text is not None:
        project.goal_text = goal_text
    if status is not None:
        project.status = status
    project.updated_at = utc_now()

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, *, owner_id: str, project_id: int) -> bool:
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        return False

    for breakdown_run in list_breakdown_runs(session, owner_id=owner_id, project_id=project_id):
        session.delete(breakdown_run)
    for task in _tasks_children_first(list_tasks(session, owner_id=owner_id, project_id=project_id)):
        session.delete(task)
    session.delete(project)
    session.commit()
    return True


def create_task(
    session: Session,
    *,
    owner_id: str,
    project_id: int,
    title: str,
    description: str | None = None,
    acceptance_criteria: str | None = None,
    parent_task_id: int | None = None,
    position: int | None = None,
    estimate_minutes: int | None = None,
) -> Task | None:
    _require_text(title, "title")
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        return None
    if parent_task_id is not None:
        parent_task = _get_task(
            session,
            owner_id=owner_id,
            project_id=project_id,
            task_id=parent_task_id,
        )
        if parent_task is None:
            return None

    task_position = position if position is not None else _next_task_position(session, project_id)
    task = Task(
        project_id=project_id,
        parent_task_id=parent_task_id,
        title=title,
        description=description,
        acceptance_criteria=acceptance_criteria,
        position=task_position,
        estimate_minutes=estimate_minutes,
    )
    session.add(task)
    project.updated_at = utc_now()
    session.add(project)
    session.commit()
    session.refresh(task)
    return task


def list_tasks(session: Session, *, owner_id: str, project_id: int) -> list[Task]:
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        return []

    statement = (
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(col(Task.position), col(Task.id))
    )
    return list(session.exec(statement).all())


def update_task(
    session: Session,
    *,
    owner_id: str,
    project_id: int,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    acceptance_criteria: str | None = None,
    status: TaskStatus | None = None,
    position: int | None = None,
    estimate_minutes: int | None = None,
) -> Task | None:
    task = _get_task(session, owner_id=owner_id, project_id=project_id, task_id=task_id)
    if task is None:
        return None

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if acceptance_criteria is not None:
        task.acceptance_criteria = acceptance_criteria
    if status is not None:
        task.status = status
    if position is not None:
        task.position = position
    if estimate_minutes is not None:
        task.estimate_minutes = estimate_minutes
    task.updated_at = utc_now()

    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is not None:
        project.updated_at = utc_now()
        session.add(project)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def reorder_tasks(
    session: Session,
    *,
    owner_id: str,
    project_id: int,
    task_ids: Sequence[int],
) -> list[Task] | None:
    tasks = list_tasks(session, owner_id=owner_id, project_id=project_id)
    task_by_id = {task.id: task for task in tasks}
    if len(task_ids) != len(set(task_ids)) or set(task_ids) != set(task_by_id):
        return None

    for position, task_id in enumerate(task_ids):
        task = task_by_id[task_id]
        task.position = position
        task.updated_at = utc_now()
        session.add(task)

    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is not None:
        project.updated_at = utc_now()
        session.add(project)

    session.commit()
    return list_tasks(session, owner_id=owner_id, project_id=project_id)


def delete_task(session: Session, *, owner_id: str, project_id: int, task_id: int) -> bool:
    tasks = list_tasks(session, owner_id=owner_id, project_id=project_id)
    task_by_id = {task.id: task for task in tasks}
    if task_id not in task_by_id:
        return False

    for task in _tasks_children_first(tasks, root_task_id=task_id):
        session.delete(task)
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is not None:
        project.updated_at = utc_now()
        session.add(project)
    session.commit()
    return True


def create_breakdown_run(
    session: Session,
    *,
    owner_id: str,
    project_id: int,
    provider: str,
    model: str,
    prompt_version: str,
    input_goal: str,
    raw_response: str | None = None,
    status: BreakdownRunStatus = BreakdownRunStatus.SUCCEEDED,
) -> BreakdownRun | None:
    _require_text(provider, "provider")
    _require_text(model, "model")
    _require_text(prompt_version, "prompt_version")
    _require_text(input_goal, "input_goal")

    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        return None

    breakdown_run = BreakdownRun(
        project_id=project_id,
        provider=provider,
        model=model,
        prompt_version=prompt_version,
        input_goal=input_goal,
        raw_response=raw_response,
        status=status,
    )
    session.add(breakdown_run)
    project.updated_at = utc_now()
    session.add(project)
    session.commit()
    session.refresh(breakdown_run)
    return breakdown_run


def list_breakdown_runs(session: Session, *, owner_id: str, project_id: int) -> list[BreakdownRun]:
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        return []

    statement = (
        select(BreakdownRun)
        .where(BreakdownRun.project_id == project_id)
        .order_by(col(BreakdownRun.created_at).desc(), col(BreakdownRun.id).desc())
    )
    return list(session.exec(statement).all())


def _get_task(session: Session, *, owner_id: str, project_id: int, task_id: int) -> Task | None:
    if get_project(session, owner_id=owner_id, project_id=project_id) is None:
        return None

    statement = select(Task).where(Task.id == task_id, Task.project_id == project_id)
    return session.exec(statement).first()


def _next_task_position(session: Session, project_id: int) -> int:
    statement = select(Task).where(Task.project_id == project_id)
    tasks = session.exec(statement).all()
    if not tasks:
        return 0
    return max(task.position for task in tasks) + 1


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} is required")


def _tasks_children_first(tasks: Sequence[Task], root_task_id: int | None = None) -> list[Task]:
    children_by_parent: dict[int | None, list[Task]] = {}
    task_by_id = {task.id: task for task in tasks}
    for task in tasks:
        children_by_parent.setdefault(task.parent_task_id, []).append(task)

    def visit(task: Task) -> list[Task]:
        ordered: list[Task] = []
        for child in children_by_parent.get(task.id, []):
            ordered.extend(visit(child))
        ordered.append(task)
        return ordered

    if root_task_id is not None:
        root_task = task_by_id.get(root_task_id)
        return visit(root_task) if root_task is not None else []

    ordered_tasks: list[Task] = []
    for task in tasks:
        if task.parent_task_id not in task_by_id:
            ordered_tasks.extend(visit(task))
    return ordered_tasks
