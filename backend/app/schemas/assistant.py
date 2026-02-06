from typing import Any

from pydantic import BaseModel, Field


class AssistantProcessRequest(BaseModel):
    user_id: str = Field(default="user_001")
    text: str
    dry_run: bool = False


class AssistantProcessResponse(BaseModel):
    user_id: str
    input: str
    normalized_input: str
    intent: dict[str, str]
    add: dict[str, Any]
    select: list[dict[str, Any]]
    update_sql: str
    dry_run: bool

