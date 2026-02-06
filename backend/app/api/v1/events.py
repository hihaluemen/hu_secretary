from fastapi import APIRouter, Query

from app.core.config import get_settings
from app.core.exceptions import BadRequestError
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreateRequest, EventItem, EventResetResponse, EventUpdateRequest

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventItem])
def list_events(
    user_id: str = Query(default="user_001"),
    keyword: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
) -> list[EventItem]:
    repo = EventRepository()
    rows = repo.list_events(user_id=user_id, keyword=keyword, date_from=date_from, date_to=date_to)
    return [EventItem(**item) for item in rows]


@router.get("/{event_id}", response_model=EventItem)
def get_event(event_id: int, user_id: str = Query(default="user_001")) -> EventItem:
    repo = EventRepository()
    row = repo.get_event(event_id=event_id, user_id=user_id)
    return EventItem(**row)


@router.post("", response_model=EventItem)
def create_event(req: EventCreateRequest) -> EventItem:
    repo = EventRepository()
    row = repo.create_event(user_id=req.user_id, payload=req.model_dump())
    return EventItem(**row)


@router.put("/{event_id}", response_model=EventItem)
def update_event(event_id: int, req: EventUpdateRequest) -> EventItem:
    repo = EventRepository()
    row = repo.update_event(event_id=event_id, user_id=req.user_id, payload=req.model_dump(exclude_none=True))
    return EventItem(**row)


@router.delete("/{event_id}")
def delete_event(event_id: int, user_id: str = Query(default="user_001")) -> dict[str, str]:
    repo = EventRepository()
    repo.delete_event(event_id=event_id, user_id=user_id)
    return {"status": "success"}


@router.post("/reset-demo", response_model=EventResetResponse)
def reset_demo(user_id: str = Query(default="user_001")) -> EventResetResponse:
    settings = get_settings()
    if not settings.DEMO_ENABLE_RESET:
        raise BadRequestError(message="演示数据重置未开启", code="DEMO_RESET_DISABLED")
    repo = EventRepository()
    deleted = repo.clear_events(user_id=user_id)
    return EventResetResponse(user_id=user_id, deleted_count=deleted)
