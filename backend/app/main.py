import logging
import time
import uuid

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api.v1.assistant import router as assistant_router
from app.api.v1.asr import router as asr_router
from app.api.v1.events import router as events_router
from app.api.v1.health import router as health_router
from app.api.v1.reminders import router as reminders_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.schemas.common import ErrorResponse
from app.services.reminder_scheduler import ReminderSchedulerRunner

settings = get_settings()
logger = logging.getLogger(__name__)

setup_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(assistant_router, prefix=settings.API_PREFIX)
app.include_router(asr_router, prefix=settings.API_PREFIX)
app.include_router(events_router, prefix=settings.API_PREFIX)
app.include_router(reminders_router, prefix=settings.API_PREFIX)

reminder_scheduler_runner = ReminderSchedulerRunner()


@app.on_event("startup")
async def startup_event() -> None:
    await reminder_scheduler_runner.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await reminder_scheduler_runner.stop()


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.time()
    request.state.request_id = request_id
    response = await call_next(request)
    elapsed_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Elapsed-MS"] = str(elapsed_ms)
    logger.info(
        "request_id=%s method=%s path=%s status=%s elapsed_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    request_id = getattr(request.state, "request_id", "unknown")
    body = ErrorResponse(code=exc.code, message=exc.message, detail=exc.detail).model_dump()
    body["request_id"] = request_id
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    body = ErrorResponse(code="VALIDATION_ERROR", message="请求参数校验失败", detail=exc.errors()).model_dump()
    body["request_id"] = request_id
    return JSONResponse(status_code=422, content=body)


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("request_id=%s unexpected_error=%s", request_id, str(exc))
    body = ErrorResponse(code="INTERNAL_ERROR", message="服务内部错误", detail=None).model_dump()
    body["request_id"] = request_id
    return JSONResponse(status_code=500, content=body)
