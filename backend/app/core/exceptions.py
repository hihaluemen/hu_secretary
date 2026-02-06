from typing import Any


class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 400,
        detail: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.detail = detail


class BadRequestError(AppError):
    def __init__(self, message: str, code: str = "BAD_REQUEST", detail: Any | None = None) -> None:
        super().__init__(message=message, code=code, status_code=400, detail=detail)


class NotFoundError(AppError):
    def __init__(self, message: str, code: str = "NOT_FOUND", detail: Any | None = None) -> None:
        super().__init__(message=message, code=code, status_code=404, detail=detail)
