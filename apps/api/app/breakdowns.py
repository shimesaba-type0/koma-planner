import json
from pydantic import BaseModel, Field, ValidationError, field_validator


PROMPT_VERSION = "breakdown-v1"
MOCK_PROVIDER = "mock"
MOCK_MODEL = "mock-breakdown-v1"


class BreakdownValidationError(ValueError):
    pass


class NormalizedBreakdownTask(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    acceptance_criteria: str | None = None
    position: int = Field(ge=0)
    estimate_minutes: int | None = Field(default=None, ge=0)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title is required")
        return stripped

    @field_validator("description", "acceptance_criteria")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class _ProviderTask(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    acceptance_criteria: str | None = None
    position: int | None = Field(default=None, ge=0)
    estimate_minutes: int | None = Field(default=None, ge=0)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title is required")
        return stripped

    @field_validator("description", "acceptance_criteria")
    @classmethod
    def optional_text_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class _ProviderBreakdown(BaseModel):
    tasks: list[_ProviderTask] = Field(min_length=1)


def build_mock_provider_response(goal_text: str) -> str:
    goal = _require_text(goal_text, "goal_text")
    payload = {
        "tasks": [
            {
                "title": "Clarify the goal",
                "description": f"Restate the desired outcome for: {goal}",
                "acceptance_criteria": "The goal is specific enough to choose the next action.",
                "estimate_minutes": 10,
            },
            {
                "title": "List the first constraints",
                "description": "Identify time, budget, tools, and any hard requirements.",
                "acceptance_criteria": "At least three concrete constraints are written down.",
                "estimate_minutes": 15,
            },
            {
                "title": "Choose the smallest useful milestone",
                "description": "Pick a result that can prove progress without expanding scope.",
                "acceptance_criteria": "The milestone can be checked in one short review.",
                "estimate_minutes": 20,
            },
            {
                "title": "Start the first task",
                "description": "Do the smallest action that moves the milestone forward.",
                "acceptance_criteria": "There is visible progress or a clear blocker.",
                "estimate_minutes": 25,
            },
        ]
    }
    return json.dumps(payload)


def parse_provider_breakdown(raw_response: str) -> list[NormalizedBreakdownTask]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise BreakdownValidationError("Provider response must be valid JSON") from exc

    try:
        provider_breakdown = _ProviderBreakdown.model_validate(parsed)
    except ValidationError as exc:
        raise BreakdownValidationError("Provider response does not match the breakdown schema") from exc

    return [
        NormalizedBreakdownTask(
            title=task.title,
            description=task.description,
            acceptance_criteria=task.acceptance_criteria,
            position=position,
            estimate_minutes=task.estimate_minutes,
        )
        for position, task in enumerate(provider_breakdown.tasks)
    ]


def _require_text(value: str, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise BreakdownValidationError(f"{field_name} is required")
    return stripped
