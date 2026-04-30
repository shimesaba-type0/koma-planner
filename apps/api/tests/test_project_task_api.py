from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import create_db_and_tables, get_session
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_db_and_tables(engine)

    def override_get_session() -> Iterator[Session]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


def test_create_project_with_initial_tasks_and_reopen(client: TestClient) -> None:
    response = client.post(
        "/api/projects",
        headers={"X-Koma-Owner-Id": "user-a"},
        json={
            "title": "Launch MVP",
            "goal_text": "Launch a small planner MVP",
            "tasks": [
                {
                    "title": "Draft the API",
                    "description": "Write the first endpoint contract",
                    "acceptance_criteria": "Endpoints are documented",
                    "estimate_minutes": 30,
                },
                {"title": "Build the endpoints"},
            ],
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["id"] is not None
    assert created["owner_id"] == "user-a"
    assert created["title"] == "Launch MVP"
    assert [task["title"] for task in created["tasks"]] == [
        "Draft the API",
        "Build the endpoints",
    ]
    assert [task["position"] for task in created["tasks"]] == [0, 1]
    assert created["tasks"][0]["status"] == "todo"

    list_response = client.get("/api/projects", headers={"X-Koma-Owner-Id": "user-a"})
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]
    assert "tasks" not in list_response.json()[0]

    detail_response = client.get(
        f"/api/projects/{created['id']}",
        headers={"X-Koma-Owner-Id": "user-a"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["tasks"][0]["description"] == "Write the first endpoint contract"

    other_owner_list = client.get("/api/projects", headers={"X-Koma-Owner-Id": "user-b"})
    assert other_owner_list.status_code == 200
    assert other_owner_list.json() == []

    other_owner_detail = client.get(
        f"/api/projects/{created['id']}",
        headers={"X-Koma-Owner-Id": "user-b"},
    )
    assert other_owner_detail.status_code == 404


def test_project_update_and_delete_are_owner_scoped(client: TestClient) -> None:
    created = client.post(
        "/api/projects",
        json={"title": "Original", "goal_text": "Plan the original goal"},
    ).json()

    blocked_update = client.patch(
        f"/api/projects/{created['id']}",
        headers={"X-Koma-Owner-Id": "user-b"},
        json={"title": "Private edit"},
    )
    assert blocked_update.status_code == 404

    update_response = client.patch(
        f"/api/projects/{created['id']}",
        json={"title": "Updated", "goal_text": "Plan the updated goal"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated"
    assert update_response.json()["goal_text"] == "Plan the updated goal"

    blocked_delete = client.delete(
        f"/api/projects/{created['id']}",
        headers={"X-Koma-Owner-Id": "user-b"},
    )
    assert blocked_delete.status_code == 404

    delete_response = client.delete(f"/api/projects/{created['id']}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/projects/{created['id']}").status_code == 404


def test_task_edit_completion_and_reopen_persist(client: TestClient) -> None:
    project = client.post(
        "/api/projects",
        json={"title": "Task edits", "goal_text": "Check task persistence"},
    ).json()
    task_response = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": "First title"},
    )
    assert task_response.status_code == 201
    task = task_response.json()

    edited_response = client.patch(
        f"/api/projects/{project['id']}/tasks/{task['id']}",
        json={
            "title": "Edited title",
            "description": "Edited description",
            "acceptance_criteria": "The edit is saved",
            "estimate_minutes": 45,
        },
    )
    assert edited_response.status_code == 200
    assert edited_response.json()["title"] == "Edited title"
    assert edited_response.json()["estimate_minutes"] == 45

    checked_response = client.patch(
        f"/api/projects/{project['id']}/tasks/{task['id']}/completion",
        json={"completed": True},
    )
    assert checked_response.status_code == 200
    assert checked_response.json()["status"] == "done"

    unchecked_response = client.patch(
        f"/api/projects/{project['id']}/tasks/{task['id']}/completion",
        json={"completed": False},
    )
    assert unchecked_response.status_code == 200
    assert unchecked_response.json()["status"] == "todo"

    reopened = client.get(f"/api/projects/{project['id']}").json()
    assert reopened["tasks"][0]["title"] == "Edited title"
    assert reopened["tasks"][0]["description"] == "Edited description"
    assert reopened["tasks"][0]["status"] == "todo"


def test_task_reorder_and_delete(client: TestClient) -> None:
    project = client.post(
        "/api/projects",
        json={
            "title": "Order tasks",
            "goal_text": "Keep task order stable",
            "tasks": [
                {"title": "First"},
                {"title": "Second"},
                {"title": "Third"},
            ],
        },
    ).json()
    tasks = project["tasks"]

    bad_reorder = client.patch(
        f"/api/projects/{project['id']}/tasks/reorder",
        json={"task_ids": [tasks[2]["id"], tasks[0]["id"]]},
    )
    assert bad_reorder.status_code == 400

    reorder_response = client.patch(
        f"/api/projects/{project['id']}/tasks/reorder",
        json={"task_ids": [tasks[2]["id"], tasks[0]["id"], tasks[1]["id"]]},
    )
    assert reorder_response.status_code == 200
    assert [task["title"] for task in reorder_response.json()] == ["Third", "First", "Second"]
    assert [task["position"] for task in reorder_response.json()] == [0, 1, 2]

    delete_response = client.delete(f"/api/projects/{project['id']}/tasks/{tasks[0]['id']}")
    assert delete_response.status_code == 204

    reopened = client.get(f"/api/projects/{project['id']}").json()
    assert [task["title"] for task in reopened["tasks"]] == ["Third", "Second"]


def test_api_validation_errors_are_clear(client: TestClient) -> None:
    invalid_project = client.post(
        "/api/projects",
        json={"title": "   ", "goal_text": "Plan something"},
    )
    assert invalid_project.status_code == 422
    assert "title" in str(invalid_project.json()["detail"])

    missing_task_project = client.post(
        "/api/projects/404/tasks",
        json={"title": "Task for missing project"},
    )
    assert missing_task_project.status_code == 404

    project = client.post(
        "/api/projects",
        json={"title": "Validation", "goal_text": "Validate bad task input"},
    ).json()
    invalid_task = client.post(
        f"/api/projects/{project['id']}/tasks",
        json={"title": ""},
    )
    assert invalid_task.status_code == 422
    assert "title" in str(invalid_task.json()["detail"])


def test_invalid_initial_task_does_not_leave_partial_project(client: TestClient) -> None:
    response = client.post(
        "/api/projects",
        json={
            "title": "Invalid initial tasks",
            "goal_text": "Do not save partial AI output",
            "tasks": [{"title": "Child without parent", "parent_task_id": 999}],
        },
    )

    assert response.status_code == 400
    assert client.get("/api/projects").json() == []
