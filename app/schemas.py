from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models import TaskPriority, TaskStatus


class TaskSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

class TaskCreate(TaskSchema):
    title: str = Field(min_length=3, max_length=100)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                raise ValueError("due_date must include a timezone")

            if value <= datetime.now(timezone.utc):
                raise ValueError("due_date must be in the future")

        return value


class TaskUpdate(TaskSchema):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    due_date: datetime | None