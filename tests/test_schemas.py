from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models import TaskPriority, TaskStatus
from app.schemas import TaskCreate, TaskResponse, TaskUpdate


def test_task_create_strips_whitespace_and_uses_defaults() -> None:
    task = TaskCreate(title="  Write tests  ", description="  Add coverage  ")

    assert task.title == "Write tests"
    assert task.description == "Add coverage"
    assert task.status is TaskStatus.TODO
    assert task.priority is TaskPriority.MEDIUM
    assert task.due_date is None


@pytest.mark.parametrize("title", ["", "ab", " " * 3, "x" * 101])
def test_task_create_rejects_title_outside_length(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskCreate(title=title)


def test_task_create_accepts_future_timezone_aware_due_date() -> None:
    due_date = datetime.now(timezone.utc) + timedelta(days=1)

    task = TaskCreate(title="Write tests", due_date=due_date)

    assert task.due_date == due_date


@pytest.mark.parametrize(
    ("due_date", "message"),
    [
        (datetime(2099, 1, 1), "must include a timezone"),
        (datetime(2000, 1, 1, tzinfo=timezone.utc), "must be in the future"),
    ],
)
def test_task_create_rejects_invalid_due_date(
    due_date: datetime,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        TaskCreate(title="Write tests", due_date=due_date)


def test_task_update_allows_omitted_fields() -> None:
    task = TaskUpdate()

    assert task.title is None
    assert task.description is None
    assert task.status is None
    assert task.priority is None
    assert task.due_date is None


def test_task_update_strips_whitespace() -> None:
    task = TaskUpdate(title="  Update tests  ", description="  Add coverage  ")

    assert task.title == "Update tests"
    assert task.description == "Add coverage"


@pytest.mark.parametrize("title", ["ab", " " * 3, "x" * 101])
def test_task_update_rejects_title_outside_length(title: str) -> None:
    with pytest.raises(ValidationError):
        TaskUpdate(title=title)


def test_task_response_parses_typed_fields() -> None:
    task = TaskResponse(
        id="123e4567-e89b-12d3-a456-426614174000",
        title="Write tests",
        description=None,
        status="todo",
        priority="high",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        due_date=None,
    )

    assert isinstance(task.id, UUID)
    assert task.status is TaskStatus.TODO
    assert task.priority is TaskPriority.HIGH
