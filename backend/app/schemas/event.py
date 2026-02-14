from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EventItem(BaseModel):
    id: int
    user_id: str
    event: str
    event_time: datetime
    location: str
    participants: str
    remark: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class EventCreateRequest(BaseModel):
    user_id: str = "user_001"
    event: str
    event_time: str
    location: str
    participants: str
    remark: str = ""


class EventUpdateRequest(BaseModel):
    user_id: str = "user_001"
    event: str | None = None
    event_time: str | None = None
    location: str | None = None
    participants: str | None = None
    remark: str | None = None


class EventResetResponse(BaseModel):
    user_id: str
    deleted_count: int


class EventBatchCreateRequest(BaseModel):
    user_id: str = "user_001"
    events: list[dict[str, Any]]


class EventBatchCreateResponse(BaseModel):
    status: str
    msg: str
    detail: list[str]
    success_count: int
    fail_count: int


class EventExecuteUpdateSQLRequest(BaseModel):
    user_id: str = "user_001"
    sql: str


class EventExecuteUpdateSQLResponse(BaseModel):
    user_id: str
    affected_rows: int
    status: str = "success"
