from fastapi import APIRouter, Query

from app.schemas.reminder import TomorrowReminderResponse
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/tomorrow", response_model=TomorrowReminderResponse)
def list_tomorrow_reminders(
    user_id: str = Query(default="user_001"),
) -> TomorrowReminderResponse:
    result = ReminderService().list_tomorrow_reminders(user_id=user_id)
    return TomorrowReminderResponse(**result)
