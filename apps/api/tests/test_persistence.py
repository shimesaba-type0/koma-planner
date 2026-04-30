from collections.abc import Iterator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.database import create_db_and_tables
from app.models import TaskStatus
from app.repositories import (
    create_breakdown_run,
    create_project,
    create_task,
    delete_project,
    delete_task,
    get_project,
    list_breakdown_runs,
    list_projects,
    list_tasks,
    reorder_tasks,
    update_project,
    update_task,
)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    create_db_and_tables(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


def test_project_requires_owner_id(session: Session) -> None:
    with pytest.raises(ValueError):
        create_project(
            session,
            owner_id="",
            title="Plan launch",
            goal_text="Launch a small service",
        )


def test_project_crud_is_scoped_by_owner(session: Session) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Write docs",
        goal_text="Document the data model",
    )

    assert project.id is not None
    assert get_project(session, owner_id="user-a", project_id=project.id) == project
    assert get_project(session, owner_id="user-b", project_id=project.id) is None
    assert list_projects(session, owner_id="user-a") == [project]
    assert list_projects(session, owner_id="user-b") == []

    updated = update_project(
        session,
        owner_id="user-a",
        project_id=project.id,
        title="Write bilingual docs",
    )

    assert updated is not None
    assert updated.title == "Write bilingual docs"
    assert delete_project(session, owner_id="user-b", project_id=project.id) is False
    assert delete_project(session, owner_id="user-a", project_id=project.id) is True
    assert get_project(session, owner_id="user-a", project_id=project.id) is None


def test_task_crud_and_reorder(session: Session) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Build MVP",
        goal_text="Finish the first persistence layer",
    )
    assert project.id is not None

    first = create_task(session, owner_id="user-a", project_id=project.id, title="Create models")
    second = create_task(session, owner_id="user-a", project_id=project.id, title="Write tests")

    assert first is not None
    assert second is not None
    assert first.id is not None
    assert second.id is not None
    assert [task.title for task in list_tasks(session, owner_id="user-a", project_id=project.id)] == [
        "Create models",
        "Write tests",
    ]
    assert list_tasks(session, owner_id="user-b", project_id=project.id) == []

    completed = update_task(
        session,
        owner_id="user-a",
        project_id=project.id,
        task_id=first.id,
        status=TaskStatus.DONE,
    )
    assert completed is not None
    assert completed.status == TaskStatus.DONE

    reordered = reorder_tasks(
        session,
        owner_id="user-a",
        project_id=project.id,
        task_ids=[second.id, first.id],
    )
    assert reordered is not None
    assert [task.id for task in reordered] == [second.id, first.id]
    assert (
        reorder_tasks(
            session,
            owner_id="user-a",
            project_id=project.id,
            task_ids=[second.id, second.id, first.id],
        )
        is None
    )

    assert delete_task(session, owner_id="user-b", project_id=project.id, task_id=first.id) is False
    assert delete_task(session, owner_id="user-a", project_id=project.id, task_id=first.id) is True
    assert [task.id for task in list_tasks(session, owner_id="user-a", project_id=project.id)] == [second.id]

    third = create_task(session, owner_id="user-a", project_id=project.id, title="Keep positions stable")

    assert third is not None
    assert third.position == 1


def test_new_task_position_uses_max_existing_position(session: Session) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Keep task order",
        goal_text="Avoid duplicate task positions",
    )
    assert project.id is not None

    first = create_task(session, owner_id="user-a", project_id=project.id, title="First")
    second = create_task(session, owner_id="user-a", project_id=project.id, title="Second")
    third = create_task(session, owner_id="user-a", project_id=project.id, title="Third")
    assert first is not None
    assert second is not None
    assert third is not None
    assert first.id is not None
    assert second.id is not None

    assert delete_task(session, owner_id="user-a", project_id=project.id, task_id=second.id) is True

    fourth = create_task(session, owner_id="user-a", project_id=project.id, title="Fourth")

    assert fourth is not None
    assert fourth.position == 3


def test_task_parent_must_belong_to_same_owner_scoped_project(session: Session) -> None:
    first_project = create_project(
        session,
        owner_id="user-a",
        title="First project",
        goal_text="Plan the first thing",
    )
    second_project = create_project(
        session,
        owner_id="user-a",
        title="Second project",
        goal_text="Plan the second thing",
    )
    other_owner_project = create_project(
        session,
        owner_id="user-b",
        title="Other owner project",
        goal_text="Plan a private thing",
    )
    assert first_project.id is not None
    assert second_project.id is not None
    assert other_owner_project.id is not None

    parent = create_task(session, owner_id="user-a", project_id=first_project.id, title="Parent")
    other_owner_parent = create_task(
        session,
        owner_id="user-b",
        project_id=other_owner_project.id,
        title="Private parent",
    )
    assert parent is not None
    assert parent.id is not None
    assert other_owner_parent is not None
    assert other_owner_parent.id is not None

    assert (
        create_task(
            session,
            owner_id="user-a",
            project_id=second_project.id,
            parent_task_id=parent.id,
            title="Cross-project child",
        )
        is None
    )
    assert (
        create_task(
            session,
            owner_id="user-a",
            project_id=first_project.id,
            parent_task_id=other_owner_parent.id,
            title="Cross-owner child",
        )
        is None
    )

    child = create_task(
        session,
        owner_id="user-a",
        project_id=first_project.id,
        parent_task_id=parent.id,
        title="Valid child",
    )
    assert child is not None
    assert child.parent_task_id == parent.id


def test_deleting_task_removes_descendants(session: Session) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Remove hierarchy",
        goal_text="Delete nested tasks cleanly",
    )
    assert project.id is not None

    parent = create_task(session, owner_id="user-a", project_id=project.id, title="Parent")
    assert parent is not None
    assert parent.id is not None
    child = create_task(
        session,
        owner_id="user-a",
        project_id=project.id,
        parent_task_id=parent.id,
        title="Child",
    )
    assert child is not None
    assert child.id is not None
    grandchild = create_task(
        session,
        owner_id="user-a",
        project_id=project.id,
        parent_task_id=child.id,
        title="Grandchild",
    )
    assert grandchild is not None

    assert delete_task(session, owner_id="user-a", project_id=project.id, task_id=parent.id) is True

    assert list_tasks(session, owner_id="user-a", project_id=project.id) == []


def test_breakdown_runs_are_scoped_by_project_owner(session: Session) -> None:
    project = create_project(
        session,
        owner_id="user-a",
        title="Break down launch",
        goal_text="Launch the first MVP",
    )
    assert project.id is not None

    run = create_breakdown_run(
        session,
        owner_id="user-a",
        project_id=project.id,
        provider="mock",
        model="mock-v1",
        prompt_version="breakdown-v1",
        input_goal=project.goal_text,
        raw_response='{"tasks":[]}',
    )

    assert run is not None
    assert run.id is not None
    assert list_breakdown_runs(session, owner_id="user-a", project_id=project.id) == [run]
    assert list_breakdown_runs(session, owner_id="user-b", project_id=project.id) == []

    assert delete_project(session, owner_id="user-a", project_id=project.id) is True
    assert list_breakdown_runs(session, owner_id="user-a", project_id=project.id) == []
