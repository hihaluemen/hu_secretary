from datetime import datetime

from pydantic import BaseModel


class TomorrowReminderItem(BaseModel):
    event_id: int
    user_id: str
    event: str
    event_time: datetime
    location: str
    participants: str
    remark: str | None = None
    remind_date: str
    target_date: str


class TomorrowReminderResponse(BaseModel):
    user_id: str
    remind_date: str
    target_date: str
    total: int
    items: list[TomorrowReminderItem]
