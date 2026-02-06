from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    env: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    detail: dict | list | str | None = None


class ResponseMeta(BaseModel):
    request_id: str
    elapsed_ms: int | None = None
