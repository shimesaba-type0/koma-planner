from datetime import datetime, timezone
from enum import StrEnum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    TODO = "todo"
    DONE = "done"


class BreakdownRunStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: str = Field(index=True, min_length=1)
    workspace_id: str | None = Field(default=None, index=True)
    title: str = Field(min_length=1, max_length=200)
    goal_text: str = Field(min_length=1)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    parent_task_id: int | None = Field(default=None, foreign_key="task.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    acceptance_criteria: str | None = None
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    position: int = Field(default=0, index=True)
    estimate_minutes: int | None = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BreakdownRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", index=True)
    provider: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=200)
    prompt_version: str = Field(min_length=1, max_length=100)
    input_goal: str = Field(min_length=1)
    raw_response: str | None = None
    status: BreakdownRunStatus = Field(default=BreakdownRunStatus.SUCCEEDED, index=True)
    created_at: datetime = Field(default_factory=utc_now)
