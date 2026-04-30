from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.breakdowns import BreakdownValidationError, parse_provider_breakdown
from app.database import create_db_and_tables, get_session
from app.main import app
from app.repositories import create_project, list_breakdown_runs


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_db_and_tables(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    def override_get_session() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_mock_breakdown_endpoint_returns_validated_tasks(client: TestClient) -> None:
    response = client.post(
        "/api/breakdowns",
        json={"goal_text": "Launch a small Koma Planner demo"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["model"] == "mock-breakdown-v1"
    assert body["prompt_version"] == "breakdown-v1"
    assert body["breakdown_run_id"] is None
    assert [task["position"] for task in body["tasks"]] == [0, 1, 2, 3]
    assert body["tasks"][0]["title"] == "Clarify the goal"
    assert "Launch a small Koma Planner demo" in body["tasks"][0]["description"]


def test_breakdown_request_validation_is_clear(client: TestClient) -> None:
    response = client.post("/api/breakdowns", json={"goal_text": "   "})

    assert response.status_code == 422
    assert "goal_text" in str(response.json()["detail"])


def test_breakdown_rejects_unavailable_provider(client: TestClient) -> None:
    response = client.post(
        "/api/breakdowns",
        json={"goal_text": "Plan with a real provider later", "provider": "openai"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only the mock provider is available"


def test_breakdown_can_store_owner_scoped_metadata(
    client: TestClient,
    session: Session,
) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Stored breakdown",
        goal_text="Plan the saved project",
    )
    assert project.id is not None

    response = client.post(
        "/api/breakdowns",
        headers={"X-Koma-Owner-Id": "user-a"},
        json={"goal_text": project.goal_text, "project_id": project.id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["breakdown_run_id"] is not None

    runs = list_breakdown_runs(session, owner_id="user-a", project_id=project.id)
    assert len(runs) == 1
    assert runs[0].provider == "mock"
    assert runs[0].model == "mock-breakdown-v1"
    assert runs[0].prompt_version == "breakdown-v1"
    assert runs[0].input_goal == project.goal_text
    assert runs[0].raw_response is not None


def test_breakdown_rejects_cross_owner_project(
    client: TestClient,
    session: Session,
) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Private project",
        goal_text="Protect this project",
    )
    assert project.id is not None

    response = client.post(
        "/api/breakdowns",
        headers={"X-Koma-Owner-Id": "user-b"},
        json={"goal_text": "Try to attach elsewhere", "project_id": project.id},
    )

    assert response.status_code == 404
    assert list_breakdown_runs(session, owner_id="user-a", project_id=project.id) == []


def test_parse_provider_breakdown_normalizes_task_positions() -> None:
    tasks = parse_provider_breakdown(
        '{"tasks":[{"title":" First task ","position":99},{"title":"Second task","estimate_minutes":15}]}'
    )

    assert [task.title for task in tasks] == ["First task", "Second task"]
    assert [task.position for task in tasks] == [0, 1]
    assert tasks[1].estimate_minutes == 15


@pytest.mark.parametrize(
    "raw_response",
    [
        "not json",
        "{}",
        '{"tasks":[]}',
        '{"tasks":[{"title":"   "}]}',
        '{"tasks":[{"title":"Valid","estimate_minutes":-1}]}',
    ],
)
def test_parse_provider_breakdown_rejects_malformed_output(raw_response: str) -> None:
    with pytest.raises(BreakdownValidationError):
        parse_provider_breakdown(raw_response)
