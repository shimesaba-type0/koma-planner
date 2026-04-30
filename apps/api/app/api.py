from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlmodel import Session

from app.database import get_session
from app.models import Project, Task, TaskStatus
from app.repositories import (
    create_project,
    create_task,
    delete_project,
    delete_task,
    get_project,
    list_projects,
    list_tasks,
    reorder_tasks,
    update_project,
    update_task,
)
from app.schemas import (
    ProjectCreate,
    ProjectDetailRead,
    ProjectRead,
    ProjectUpdate,
    TaskCompletionUpdate,
    TaskCreate,
    TaskRead,
    TaskReorder,
    TaskUpdate,
)


router = APIRouter(prefix="/api")


def get_owner_id(x_koma_owner_id: Annotated[str | None, Header()] = None) -> str:
    if x_koma_owner_id is None:
        return "dev-user"
    owner_id = x_koma_owner_id.strip()
    if not owner_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Koma-Owner-Id is required")
    return owner_id


OwnerId = Annotated[str, Depends(get_owner_id)]
DbSession = Annotated[Session, Depends(get_session)]


@router.post("/projects", response_model=ProjectDetailRead, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(payload: ProjectCreate, owner_id: OwnerId, session: DbSession) -> ProjectDetailRead:
    project = create_project(
        session,
        owner_id=owner_id,
        title=payload.title,
        goal_text=payload.goal_text,
        workspace_id=payload.workspace_id,
    )
    for task_payload in payload.tasks:
        task = create_task(
            session,
            owner_id=owner_id,
            project_id=_require_id(project),
            title=task_payload.title,
            description=task_payload.description,
            acceptance_criteria=task_payload.acceptance_criteria,
            parent_task_id=task_payload.parent_task_id,
            position=task_payload.position,
            estimate_minutes=task_payload.estimate_minutes,
        )
        if task is None:
            delete_project(session, owner_id=owner_id, project_id=_require_id(project))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid initial task")
    return _project_detail(session, owner_id=owner_id, project=project)


@router.get("/projects", response_model=list[ProjectRead])
def list_projects_endpoint(owner_id: OwnerId, session: DbSession) -> list[Project]:
    return list_projects(session, owner_id=owner_id)


@router.get("/projects/{project_id}", response_model=ProjectDetailRead)
def get_project_endpoint(project_id: int, owner_id: OwnerId, session: DbSession) -> ProjectDetailRead:
    project = _get_project_or_404(session, owner_id=owner_id, project_id=project_id)
    return _project_detail(session, owner_id=owner_id, project=project)


@router.patch("/projects/{project_id}", response_model=ProjectDetailRead)
def update_project_endpoint(
    project_id: int,
    payload: ProjectUpdate,
    owner_id: OwnerId,
    session: DbSession,
) -> ProjectDetailRead:
    project = update_project(
        session,
        owner_id=owner_id,
        project_id=project_id,
        title=payload.title,
        goal_text=payload.goal_text,
        status=payload.status,
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _project_detail(session, owner_id=owner_id, project=project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(project_id: int, owner_id: OwnerId, session: DbSession) -> Response:
    if not delete_project(session, owner_id=owner_id, project_id=project_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/projects/{project_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    project_id: int,
    payload: TaskCreate,
    owner_id: OwnerId,
    session: DbSession,
) -> Task:
    task = create_task(
        session,
        owner_id=owner_id,
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        acceptance_criteria=payload.acceptance_criteria,
        parent_task_id=payload.parent_task_id,
        position=payload.position,
        estimate_minutes=payload.estimate_minutes,
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project or parent task not found")
    return task


@router.patch("/projects/{project_id}/tasks/reorder", response_model=list[TaskRead])
def reorder_tasks_endpoint(
    project_id: int,
    payload: TaskReorder,
    owner_id: OwnerId,
    session: DbSession,
) -> list[Task]:
    _get_project_or_404(session, owner_id=owner_id, project_id=project_id)
    tasks = reorder_tasks(session, owner_id=owner_id, project_id=project_id, task_ids=payload.task_ids)
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task IDs must match the project tasks")
    return tasks


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    project_id: int,
    task_id: int,
    payload: TaskUpdate,
    owner_id: OwnerId,
    session: DbSession,
) -> Task:
    task = update_task(
        session,
        owner_id=owner_id,
        project_id=project_id,
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        acceptance_criteria=payload.acceptance_criteria,
        status=payload.status,
        position=payload.position,
        estimate_minutes=payload.estimate_minutes,
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/projects/{project_id}/tasks/{task_id}/completion", response_model=TaskRead)
def update_task_completion_endpoint(
    project_id: int,
    task_id: int,
    payload: TaskCompletionUpdate,
    owner_id: OwnerId,
    session: DbSession,
) -> Task:
    task = update_task(
        session,
        owner_id=owner_id,
        project_id=project_id,
        task_id=task_id,
        status=TaskStatus.DONE if payload.completed else TaskStatus.TODO,
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/projects/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(project_id: int, task_id: int, owner_id: OwnerId, session: DbSession) -> Response:
    if not delete_task(session, owner_id=owner_id, project_id=project_id, task_id=task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _project_detail(session: Session, *, owner_id: str, project: Project) -> ProjectDetailRead:
    return ProjectDetailRead.model_validate(
        {
            **ProjectRead.model_validate(project).model_dump(),
            "tasks": list_tasks(session, owner_id=owner_id, project_id=_require_id(project)),
        }
    )


def _get_project_or_404(session: Session, *, owner_id: str, project_id: int) -> Project:
    project = get_project(session, owner_id=owner_id, project_id=project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _require_id(project: Project) -> int:
    if project.id is None:
        raise RuntimeError("Project was not persisted")
    return project.id
