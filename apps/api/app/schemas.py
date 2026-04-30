from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.models import ProjectStatus, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    acceptance_criteria: str | None = None
    parent_task_id: int | None = None
    position: int | None = Field(default=None, ge=0)
    estimate_minutes: int | None = Field(default=None, ge=0)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        return _require_text(value, "title")


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    acceptance_criteria: str | None = None
    status: TaskStatus | None = None
    position: int | None = Field(default=None, ge=0)
    estimate_minutes: int | None = Field(default=None, ge=0)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _require_text(value, "title")


class TaskCompletionUpdate(BaseModel):
    completed: bool


class TaskReorder(BaseModel):
    task_ids: list[int] = Field(min_length=1)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    parent_task_id: int | None
    title: str
    description: str | None
    acceptance_criteria: str | None
    status: TaskStatus
    position: int
    estimate_minutes: int | None
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    goal_text: str = Field(min_length=1)
    workspace_id: str | None = None
    tasks: list[TaskCreate] = Field(default_factory=list)

    @field_validator("title", "goal_text")
    @classmethod
    def text_must_not_be_blank(cls, value: str, info: ValidationInfo) -> str:
        return _require_text(value, info.field_name)

    @field_validator("workspace_id")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _require_text(value, "workspace_id")


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    goal_text: str | None = Field(default=None, min_length=1)
    status: ProjectStatus | None = None

    @field_validator("title", "goal_text")
    @classmethod
    def text_must_not_be_blank(cls, value: str | None, info: ValidationInfo) -> str | None:
        if value is None:
            return None
        return _require_text(value, info.field_name)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: str
    workspace_id: str | None
    title: str
    goal_text: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectDetailRead(ProjectRead):
    tasks: list[TaskRead]


def _require_text(value: str, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} is required")
    return stripped
